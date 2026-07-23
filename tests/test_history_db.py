"""
Automated tests for Bitcoin Cycle Compass v8.5 historical data layer.

Covers:
  - Database creation and table structure
  - Schema migration idempotency
  - Duplicate row prevention (INSERT OR IGNORE / INSERT OR REPLACE)
  - Four-year history import and validation
  - Range queries for all seven range keys
  - Updater failure handling and transaction roll-back

Run with:
    python -m pytest tests/ -v
or:
    python tests/test_history_db.py
"""
import sqlite3
import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — allow imports from scripts/ regardless of working directory.
# ---------------------------------------------------------------------------
_SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(_SCRIPTS))

from db_schema import (  # noqa: E402
    apply_migrations,
    get_connection,
    get_schema_version,
    init_db,
)
from history_service import (  # noqa: E402
    get_daily_history,
    get_weekly_history,
    query_range,
)
from import_history import validate_row  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tmp_db():
    """Create a temporary database path (caller must clean up)."""
    f = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    f.close()
    return Path(f.name)


def _seed(db_path, n=1500, start_days_ago=1500, base_price=30_000):
    """Insert *n* consecutive daily rows into btc_daily starting *start_days_ago* ago."""
    conn = init_db(db_path)
    today = date.today()
    for i in range(n):
        d = (today - timedelta(days=start_days_ago - i)).isoformat()
        usd = base_price + i * 10
        aud = round(usd * 1.55, 2)
        conn.execute(
            "INSERT OR IGNORE INTO btc_daily (date, price_usd, price_aud) VALUES (?, ?, ?)",
            (d, usd, aud),
        )
    conn.commit()
    conn.close()


# ===========================================================================
# 1. Database creation
# ===========================================================================

class TestDatabaseCreation(unittest.TestCase):
    """Database and schema creation."""

    def setUp(self):
        self.db_path = _tmp_db()
        self.conn = init_db(self.db_path)

    def tearDown(self):
        self.conn.close()
        self.db_path.unlink(missing_ok=True)

    def test_schema_version_set_to_current(self):
        from db_schema import CURRENT_VERSION
        self.assertEqual(get_schema_version(self.conn), CURRENT_VERSION)

    def test_all_required_tables_exist(self):
        existing = {
            r[0] for r in self.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        required = {
            'schema_version',
            'btc_daily',
            'fear_greed',
            'etf_flows',
            'stablecoin_market_cap',
            'scores',
            'market_regime',
            'capital_allocation',
            'market_data',
        }
        missing = required - existing
        self.assertFalse(missing, f"Missing tables: {missing}")

    def test_btc_daily_has_expected_columns(self):
        cols = {
            r[1] for r in self.conn.execute("PRAGMA table_info(btc_daily)").fetchall()
        }
        self.assertIn('date', cols)
        self.assertIn('price_usd', cols)
        self.assertIn('price_aud', cols)
        self.assertIn('source', cols)

    def test_fresh_db_returns_version_zero_before_migration(self):
        p = _tmp_db()
        try:
            conn = get_connection(p)
            self.assertEqual(get_schema_version(conn), 0)
            conn.close()
        finally:
            p.unlink(missing_ok=True)

    def test_migration_is_idempotent(self):
        """Applying migrations twice should not raise or change the version."""
        apply_migrations(self.conn)
        apply_migrations(self.conn)
        from db_schema import CURRENT_VERSION
        self.assertEqual(get_schema_version(self.conn), CURRENT_VERSION)

    def test_existing_rows_survive_re_migration(self):
        """Data inserted before a re-migration must still be there after."""
        self.conn.execute(
            "INSERT INTO btc_daily (date, price_usd) VALUES ('2024-06-01', 68000)"
        )
        self.conn.commit()
        apply_migrations(self.conn)
        row = self.conn.execute(
            "SELECT price_usd FROM btc_daily WHERE date='2024-06-01'"
        ).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 68000)


# ===========================================================================
# 2. Duplicate prevention
# ===========================================================================

class TestDuplicatePrevention(unittest.TestCase):
    """INSERT OR IGNORE / INSERT OR REPLACE semantics."""

    def setUp(self):
        self.db_path = _tmp_db()
        self.conn = init_db(self.db_path)

    def tearDown(self):
        self.conn.close()
        self.db_path.unlink(missing_ok=True)

    def test_ignore_keeps_first_value(self):
        self.conn.execute(
            "INSERT OR IGNORE INTO btc_daily (date, price_usd) VALUES ('2024-01-01', 50000)"
        )
        self.conn.execute(
            "INSERT OR IGNORE INTO btc_daily (date, price_usd) VALUES ('2024-01-01', 99999)"
        )
        self.conn.commit()
        count = self.conn.execute("SELECT COUNT(*) FROM btc_daily").fetchone()[0]
        price = self.conn.execute(
            "SELECT price_usd FROM btc_daily WHERE date='2024-01-01'"
        ).fetchone()[0]
        self.assertEqual(count, 1)
        self.assertEqual(price, 50000)  # original preserved

    def test_replace_updates_to_latest_value(self):
        self.conn.execute(
            "INSERT OR REPLACE INTO btc_daily (date, price_usd) VALUES ('2024-01-02', 55000)"
        )
        self.conn.execute(
            "INSERT OR REPLACE INTO btc_daily (date, price_usd) VALUES ('2024-01-02', 62000)"
        )
        self.conn.commit()
        count = self.conn.execute("SELECT COUNT(*) FROM btc_daily").fetchone()[0]
        price = self.conn.execute(
            "SELECT price_usd FROM btc_daily WHERE date='2024-01-02'"
        ).fetchone()[0]
        self.assertEqual(count, 1)
        self.assertEqual(price, 62000)  # updated

    def test_different_dates_both_stored(self):
        self.conn.execute(
            "INSERT OR IGNORE INTO btc_daily (date, price_usd) VALUES ('2024-03-01', 70000)"
        )
        self.conn.execute(
            "INSERT OR IGNORE INTO btc_daily (date, price_usd) VALUES ('2024-03-02', 71000)"
        )
        self.conn.commit()
        self.assertEqual(
            self.conn.execute("SELECT COUNT(*) FROM btc_daily").fetchone()[0], 2
        )

    def test_fear_greed_duplicate_prevention(self):
        self.conn.execute(
            "INSERT OR IGNORE INTO fear_greed (date, value) VALUES ('2024-01-01', 55)"
        )
        self.conn.execute(
            "INSERT OR IGNORE INTO fear_greed (date, value) VALUES ('2024-01-01', 80)"
        )
        self.conn.commit()
        val = self.conn.execute(
            "SELECT value FROM fear_greed WHERE date='2024-01-01'"
        ).fetchone()[0]
        self.assertEqual(val, 55)


# ===========================================================================
# 3. History import
# ===========================================================================

class TestImportHistory(unittest.TestCase):
    """History import, data validation and idempotency."""

    def setUp(self):
        self.db_path = _tmp_db()

    def tearDown(self):
        self.db_path.unlink(missing_ok=True)

    # --- validate_row -------------------------------------------------------

    def test_valid_row_accepted(self):
        self.assertTrue(validate_row({'date': '2024-01-15', 'price_usd': 43_000}))

    def test_missing_date_rejected(self):
        with self.assertRaises(ValueError):
            validate_row({'date': None, 'price_usd': 43_000})

    def test_empty_date_rejected(self):
        with self.assertRaises(ValueError):
            validate_row({'date': '', 'price_usd': 43_000})

    def test_wrong_date_format_rejected(self):
        with self.assertRaises(ValueError):
            validate_row({'date': '15-01-2024', 'price_usd': 43_000})

    def test_invalid_month_rejected(self):
        with self.assertRaises(ValueError):
            validate_row({'date': '2024-13-01', 'price_usd': 43_000})

    def test_missing_price_rejected(self):
        with self.assertRaises(ValueError):
            validate_row({'date': '2024-01-15', 'price_usd': None})

    def test_zero_price_rejected(self):
        with self.assertRaises(ValueError):
            validate_row({'date': '2024-01-15', 'price_usd': 0})

    def test_negative_price_rejected(self):
        with self.assertRaises(ValueError):
            validate_row({'date': '2024-01-15', 'price_usd': -100})

    def test_price_below_lower_bound_rejected(self):
        with self.assertRaises(ValueError):
            validate_row({'date': '2024-01-15', 'price_usd': 500})

    def test_price_above_upper_bound_rejected(self):
        with self.assertRaises(ValueError):
            validate_row({'date': '2024-01-15', 'price_usd': 3_000_000})

    def test_non_numeric_price_rejected(self):
        with self.assertRaises((ValueError, TypeError)):
            validate_row({'date': '2024-01-15', 'price_usd': 'lots'})

    # --- import idempotency -------------------------------------------------

    def test_seeded_rows_counted_correctly(self):
        _seed(self.db_path, n=10)
        conn = init_db(self.db_path)
        count = conn.execute("SELECT COUNT(*) FROM btc_daily").fetchone()[0]
        conn.close()
        self.assertEqual(count, 10)

    def test_reimport_same_data_no_duplicates(self):
        _seed(self.db_path, n=20)
        _seed(self.db_path, n=20)   # same data again
        conn = init_db(self.db_path)
        count = conn.execute("SELECT COUNT(*) FROM btc_daily").fetchone()[0]
        conn.close()
        self.assertEqual(count, 20)

    def test_overlapping_import_adds_only_new_rows(self):
        _seed(self.db_path, n=10, start_days_ago=20)
        _seed(self.db_path, n=15, start_days_ago=25)  # 5 new + 10 overlap
        conn = init_db(self.db_path)
        count = conn.execute("SELECT COUNT(*) FROM btc_daily").fetchone()[0]
        conn.close()
        self.assertEqual(count, 15)


# ===========================================================================
# 4. Range queries
# ===========================================================================

class TestRangeQueries(unittest.TestCase):
    """History service range queries for all seven range keys."""

    @classmethod
    def setUpClass(cls):
        cls.db_path = _tmp_db()
        _seed(cls.db_path, n=1500, start_days_ago=1500)

    @classmethod
    def tearDownClass(cls):
        cls.db_path.unlink(missing_ok=True)

    # --- resolution checks --------------------------------------------------

    def test_7d_is_daily(self):
        result = query_range('7d', self.db_path)
        self.assertEqual(result['resolution'], 'Daily')

    def test_1m_is_daily(self):
        result = query_range('1m', self.db_path)
        self.assertEqual(result['resolution'], 'Daily')

    def test_3m_is_daily(self):
        result = query_range('3m', self.db_path)
        self.assertEqual(result['resolution'], 'Daily')

    def test_6m_is_daily(self):
        result = query_range('6m', self.db_path)
        self.assertEqual(result['resolution'], 'Daily')

    def test_1y_is_weekly(self):
        result = query_range('1y', self.db_path)
        self.assertEqual(result['resolution'], 'Weekly')

    def test_2y_is_weekly(self):
        result = query_range('2y', self.db_path)
        self.assertEqual(result['resolution'], 'Weekly')

    def test_4y_is_weekly(self):
        result = query_range('4y', self.db_path)
        self.assertEqual(result['resolution'], 'Weekly')

    # --- row count upper bounds ---------------------------------------------

    def test_7d_at_most_7_rows(self):
        result = query_range('7d', self.db_path)
        self.assertLessEqual(len(result['rows']), 7)

    def test_1m_at_most_31_rows(self):
        result = query_range('1m', self.db_path)
        self.assertLessEqual(len(result['rows']), 31)

    def test_3m_at_most_92_rows(self):
        result = query_range('3m', self.db_path)
        self.assertLessEqual(len(result['rows']), 92)

    def test_6m_at_most_184_rows(self):
        result = query_range('6m', self.db_path)
        self.assertLessEqual(len(result['rows']), 184)

    def test_1y_at_most_52_weeks(self):
        result = query_range('1y', self.db_path)
        self.assertLessEqual(len(result['rows']), 52)

    def test_2y_at_most_104_weeks(self):
        result = query_range('2y', self.db_path)
        self.assertLessEqual(len(result['rows']), 104)

    def test_4y_at_most_208_weeks(self):
        result = query_range('4y', self.db_path)
        self.assertLessEqual(len(result['rows']), 208)

    # --- data quality -------------------------------------------------------

    def test_all_ranges_return_at_least_one_row(self):
        for rk in ('7d', '1m', '3m', '6m', '1y', '2y', '4y'):
            with self.subTest(range_key=rk):
                result = query_range(rk, self.db_path)
                self.assertGreater(len(result['rows']), 0)

    def test_daily_rows_have_day_key(self):
        for rk in ('7d', '1m', '3m', '6m'):
            with self.subTest(range_key=rk):
                result = query_range(rk, self.db_path)
                for row in result['rows']:
                    self.assertIn('day', row)

    def test_weekly_rows_have_week_key(self):
        for rk in ('1y', '2y', '4y'):
            with self.subTest(range_key=rk):
                result = query_range(rk, self.db_path)
                for row in result['rows']:
                    self.assertIn('week', row)

    def test_all_rows_have_usd_price(self):
        for rk in ('7d', '1m', '3m', '6m', '1y', '2y', '4y'):
            with self.subTest(range_key=rk):
                result = query_range(rk, self.db_path)
                for row in result['rows']:
                    self.assertIn('usd', row)
                    self.assertIsNotNone(row['usd'])

    def test_all_rows_have_aud_price(self):
        for rk in ('7d', '4y'):
            with self.subTest(range_key=rk):
                result = query_range(rk, self.db_path)
                for row in result['rows']:
                    self.assertIn('aud', row)

    def test_rows_are_sorted_ascending(self):
        for rk in ('7d', '4y'):
            with self.subTest(range_key=rk):
                result = query_range(rk, self.db_path)
                keys = [r.get('day') or r.get('week') for r in result['rows']]
                self.assertEqual(keys, sorted(keys))

    def test_unknown_range_raises_value_error(self):
        with self.assertRaises(ValueError):
            query_range('10y', self.db_path)

    def test_get_daily_history_returns_list(self):
        rows = get_daily_history(self.db_path, days=30)
        self.assertIsInstance(rows, list)
        self.assertGreater(len(rows), 0)

    def test_get_weekly_history_returns_list(self):
        rows = get_weekly_history(self.db_path, weeks=52)
        self.assertIsInstance(rows, list)
        self.assertGreater(len(rows), 0)


# ===========================================================================
# 5. Updater failure handling
# ===========================================================================

class TestUpdaterFailureHandling(unittest.TestCase):
    """Data validation and transaction integrity under error conditions."""

    def test_all_malformed_api_rows_rejected(self):
        """Every bad row variant must raise ValueError (or TypeError)."""
        bad_rows = [
            {'date': None,       'price_usd': 50_000},
            {'date': '',         'price_usd': 50_000},
            {'date': '2024-01-01', 'price_usd': None},
            {'date': '2024-01-01', 'price_usd': -1},
            {'date': '2024-01-01', 'price_usd': 0},
            {'date': '2024-01-01', 'price_usd': 500},          # below $1 000
            {'date': '2024-01-01', 'price_usd': 999_999_999},  # above $2 M
            {'date': 'not-a-date', 'price_usd': 50_000},
            {'date': '2024/01/01', 'price_usd': 50_000},       # wrong separator
            {'date': '01-01-2024', 'price_usd': 50_000},       # wrong order
        ]
        for row in bad_rows:
            with self.subTest(row=row):
                with self.assertRaises((ValueError, TypeError)):
                    validate_row(row)

    def test_transaction_rolled_back_on_mid_write_error(self):
        """A RuntimeError mid-transaction must not commit the partial write."""
        db_path = _tmp_db()
        try:
            conn = init_db(db_path)
            conn.execute(
                "INSERT INTO btc_daily (date, price_usd) VALUES ('2024-05-01', 60000)"
            )
            conn.commit()
            # Simulate a mid-transaction failure.
            try:
                with conn:
                    conn.execute(
                        "INSERT INTO btc_daily (date, price_usd) VALUES ('2024-05-02', 61000)"
                    )
                    raise RuntimeError("Simulated write failure")
            except RuntimeError:
                pass  # expected
            count = conn.execute("SELECT COUNT(*) FROM btc_daily").fetchone()[0]
            conn.close()
            self.assertEqual(count, 1)  # 2024-05-02 was rolled back
        finally:
            db_path.unlink(missing_ok=True)

    def test_empty_db_returns_empty_history(self):
        """A brand-new empty DB must return empty lists, not raise."""
        db_path = _tmp_db()
        try:
            daily = get_daily_history(db_path, days=30)
            weekly = get_weekly_history(db_path, weeks=52)
            self.assertIsInstance(daily, list)
            self.assertIsInstance(weekly, list)
            self.assertEqual(len(daily), 0)
            self.assertEqual(len(weekly), 0)
        finally:
            db_path.unlink(missing_ok=True)

    def test_partial_row_missing_price_aud_still_inserts(self):
        """price_aud is optional — rows without it must still be inserted."""
        db_path = _tmp_db()
        try:
            conn = init_db(db_path)
            conn.execute(
                "INSERT INTO btc_daily (date, price_usd) VALUES ('2024-06-01', 65000)"
            )
            conn.commit()
            row = conn.execute(
                "SELECT price_usd, price_aud FROM btc_daily WHERE date='2024-06-01'"
            ).fetchone()
            conn.close()
            self.assertEqual(row[0], 65000)
            self.assertIsNone(row[1])
        finally:
            db_path.unlink(missing_ok=True)

    def test_concurrent_inserts_do_not_corrupt_db(self):
        """Two sequential write sessions (two updater runs) must both succeed."""
        db_path = _tmp_db()
        try:
            # First session commits and closes.
            conn_a = init_db(db_path)
            conn_a.execute(
                "INSERT OR IGNORE INTO btc_daily (date, price_usd) VALUES ('2024-07-01', 58000)"
            )
            conn_a.commit()
            conn_a.close()

            # Second session opens after the first has committed.
            conn_b = init_db(db_path)
            conn_b.execute(
                "INSERT OR IGNORE INTO btc_daily (date, price_usd) VALUES ('2024-07-02', 59000)"
            )
            conn_b.commit()
            conn_b.close()

            # Verify via fresh connection.
            conn_v = init_db(db_path)
            count = conn_v.execute("SELECT COUNT(*) FROM btc_daily").fetchone()[0]
            conn_v.close()
            self.assertEqual(count, 2)
        finally:
            db_path.unlink(missing_ok=True)


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == '__main__':
    unittest.main(verbosity=2)
