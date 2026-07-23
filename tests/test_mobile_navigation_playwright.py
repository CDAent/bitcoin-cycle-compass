import contextlib
import http.server
import socket
import socketserver
import threading
from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")

ROOT = Path(__file__).resolve().parents[1]


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):  # noqa: D401
        return


@pytest.fixture(scope="module")
def app_url():
    with contextlib.ExitStack() as stack:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        stack.enter_context(sock)
        sock.bind(("127.0.0.1", 0))
        host, port = sock.getsockname()
        sock.close()

        handler = lambda *args, **kwargs: _QuietHandler(*args, directory=str(ROOT), **kwargs)
        server = socketserver.TCPServer((host, port), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://{host}:{port}/index.html"
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


def _overlap(a, b):
    a_left, a_right = a["x"], a["x"] + a["width"]
    a_top, a_bottom = a["y"], a["y"] + a["height"]
    b_left, b_right = b["x"], b["x"] + b["width"]
    b_top, b_bottom = b["y"], b["y"] + b["height"]
    return not (
        a_right <= b_left
        or b_right <= a_left
        or a_bottom <= b_top
        or b_bottom <= a_top
    )


def test_mobile_header_navigation_and_layout(app_url):
    mobile_viewports = [(375, 667), (390, 844), (430, 932), (768, 1024)]
    nav_routes = ["dashboard", "markets", "liquidity", "onchain", "macro", "news", "history", "analyst", "alerts", "settings", "about"]

    with playwright.sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        console_errors = []
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)

        for width, height in mobile_viewports:
            page.set_viewport_size({"width": width, "height": height})
            page.goto(app_url, wait_until="networkidle")

            assert page.locator("#mobileHeaderLogo").is_visible()
            assert page.locator("#mobileHeaderRefresh").is_visible()
            assert page.locator("#mobileMenuBtn").is_visible()
            assert page.locator("#mobileHeaderTitle").is_visible()

            refresh_box = page.locator("#mobileHeaderRefresh").bounding_box()
            menu_box = page.locator("#mobileMenuBtn").bounding_box()
            logo_box = page.locator("#mobileHeaderLogo").bounding_box()
            title_box = page.locator("#mobileHeaderTitle").bounding_box()
            assert refresh_box and menu_box and logo_box and title_box
            assert refresh_box["width"] >= 44 and refresh_box["height"] >= 44
            assert menu_box["width"] >= 44 and menu_box["height"] >= 44
            assert logo_box["width"] >= 44 and logo_box["height"] >= 44
            assert not _overlap(logo_box, title_box)
            assert not _overlap(title_box, refresh_box)
            assert not _overlap(refresh_box, menu_box)

            has_horizontal_scroll = page.evaluate(
                "() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1"
            )
            assert not has_horizontal_scroll

            for route in nav_routes:
                page.click("#mobileMenuBtn")
                page.wait_for_selector("#mobileDrawer.open")
                page.click(f'#mobileDrawer .nav-item[data-view="{route}"]')
                page.wait_for_timeout(300)
                assert page.locator("#mobileMenuBtn").is_visible()
                page.click("#mobileMenuBtn")
                page.wait_for_selector("#mobileDrawer.open")
                page.click("#mobileNavOverlay")
                page.wait_for_timeout(300)

            assert page.locator('#mobileDrawer .nav-item[data-view="reports"]').count() == 0

            page.goto(app_url, wait_until="networkidle")
            page.evaluate("openDetail('alerts')")
            page.wait_for_selector(".alert-threshold-row")
            assert page.locator(".alert-threshold-row").count() >= 9

            page.goto(app_url, wait_until="networkidle")
            event_columns = page.evaluate("() => getComputedStyle(document.getElementById('eventsList')).gridTemplateColumns")
            assert event_columns and event_columns.count(" ") == 0

        page.set_viewport_size({"width": 1440, "height": 900})
        page.goto(app_url, wait_until="networkidle")
        assert page.locator("#sideRefresh").is_visible()
        assert page.locator("#topRefresh").is_visible()
        desktop_news = page.locator(".c-news").bounding_box()
        desktop_events = page.locator(".c-events").bounding_box()
        assert desktop_news and desktop_events and desktop_news["width"] > desktop_events["width"]
        for route in nav_routes[1:]:
            page.click(f'.sidebar .nav-item[data-view="{route}"]')
            page.wait_for_timeout(250)
            assert not page.locator("#detailPanel").is_hidden()
        page.click('.sidebar .nav-item[data-view="dashboard"]')
        page.wait_for_timeout(250)
        assert page.locator("#detailPanel").is_hidden()

        assert console_errors == []
        browser.close()
