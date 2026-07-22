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
- ETF: best-effort Farside public table extraction. It displays Unavailable if the page layout blocks extraction.
- Market proxies: Stooq daily prices for GLD, QQQ, SLV and EEM.
- News: GDELT live news search.

The cycle forecasts are estimates, not live facts or financial advice.
