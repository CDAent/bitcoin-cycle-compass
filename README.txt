BITCOIN CYCLE COMPASS VERSION 6.4

BITCOIN CYCLE COMPASS VERSION 6.2

FILES TO UPLOAD
Upload the complete contents of this package to the root of your existing GitHub repository, including the hidden .github folder.

FIRST-TIME SETUP
1. Upload all files and folders.
2. Open the repository Actions tab.
3. Select "Update live market data" and choose Run workflow.
4. In Settings > Actions > General, set Workflow permissions to "Read and write permissions" if the action cannot commit data/live.json.
5. Keep GitHub Pages publishing from main / root.

AUTOMATIC UPDATES
The GitHub Action runs hourly and writes data/live.json. The phone dashboard checks that file every 15 minutes while open.

LIVE SOURCES
- BTC index: trimmed average/median check using Coinbase, Kraken, Bitstamp and CoinGecko index.
- FX: Frankfurter.
- Fear & Greed: Alternative.me.
- Stablecoins: DefiLlama.
- Macro: FRED public CSV series.
- On-chain: Blockchain.com public charts.
- ETF: dual-method tracking: confirmed Farside net flows plus a separate live demand proxy using IBIT, FBTC, ARKB, BITB, GBTC and BTC ETF price/volume participation. The proxy is clearly labelled and is not treated as confirmed net flow.
- Market proxies: Stooq daily prices for GLD, QQQ, SLV and EEM.
- News: GDELT live news search.

The cycle forecasts are estimates, not live facts or financial advice.


VERSION 6.4
- Working navigation opens detailed views for each dashboard category.
- News uses multiple live Google News RSS searches with GDELT fallback.
- Events link to official Fed, BLS, BEA and CME calendars.
- Local 30-day snapshot history and device-stored alert levels.
