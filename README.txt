Bitcoin Cycle Compass Version 7

Deployment
1. Upload all files and folders in this package to the GitHub Pages repository.
2. Run the Update live market data GitHub Action once.
3. Wait for GitHub Pages deployment to complete.
4. Fully close and reopen the installed app to clear the previous service-worker view.

Version 7 uses a single integrated compass needle. The needle rotates only during manual or automatic data refresh.


ANIMATED LOGO SETUP
Place these two PNG files in the same root folder as index.html:
- bitcoin-compass-base.png
- bitcoin-compass-needle.png

Both PNGs must have exactly the same pixel dimensions and canvas alignment.
The complete needle image is rotated automatically during live-data refresh.
No separate animation frames are required.
The rotation pivot is currently set to 50% across and 40.72% down the full image canvas.
If your hub is slightly above or below this point, adjust transform-origin in index.html.

CENTRE-PIVOT FIX
The supplied needle layer was shifted 1 px left and 3 px up so its hub aligns with the base-logo hub.
The CSS rotation origin is now 49.64% horizontally and 36.48% vertically.


VERSION 7.1 DISPLAY UPDATE
- Global Liquidity now displays a modelled percentage share rather than an abstract score.
- Five named liquidity destinations plus Other always total 100%.
- Colour coding remains tied to the underlying strength of each signal.
- Compass AI Research now uses a horizontal Weak-to-Confident meter.
- Fear & Greed colour bands now follow balanced index categories:
  Extreme Fear 0-24, Fear 25-44, Neutral 45-54, Greed 55-74, Extreme Greed 75-100.


VERSION 7.2 LIQUIDITY AND SENTIMENT UPDATE
- Fear & Greed colours now use:
  0-24 dark red, 25-44 red, 45-54 yellow, 55-74 green, 75-100 dark green.
- Global Liquidity Estimates now use seven primary categories plus Other:
  Cash & short-term bills; Government bonds & fixed income; Global equities;
  Bitcoin & digital assets; Gold & precious metals; Broad commodities;
  Real estate & REITs; and Other.
- The eight displayed percentages total 100%.
- These remain modelled relative liquidity signals, not audited market-size statistics.


VERSION 7.3 DASHBOARD REORGANISATION
- BTC Live Price is now the first/top dashboard widget.
- Global Capital Allocation contains nine named destinations plus Other.
- Allocation rows re-sort from highest percentage to lowest on every refresh.
- Trend arrows are green for rising, amber for neutral and red for falling.
- Risk Appetite remains only in Today's Snapshot and is not duplicated.


VERSION 7.4 LOGO AND DATA REBUILD
- Rebuilt from the previous capital-allocation release.
- Uses only bitcoin-compass-base.png and bitcoin-compass-needle.png for the animated dashboard logo.
- Preserves the capital-allocation categories, descending sorting and colour-coded trend arrows.
- Preserves the centred needle pivot and refresh animation.
- Updates the app version, manifest, service-worker cache and live-data version marker.


VERSION 7.5 TREND COLOUR UPDATE
- Green = increasing, amber = no material change, red = declining.
- Global Capital Allocation percentage badges and arrows now use actual trend data.
- Global Liquidity detail page now shows trend arrows and labels.
- Added liquidityTrends to scheduled and browser-fallback data.
- Fixed the undefined stable_change updater reference.


VERSION 8.0 COMPASS AI ANALYST AND WEEKLY HISTORY
- Added Compass Ai Analyst with free-text questions and six quick prompts.
- Analyst interprets current dashboard metrics and available weekly history.
- History & Trends now uses weekly records with 3-month, 6-month, 1-year,
  2-year and 4-year views.
- Added up to 208 weekly Bitcoin records from a four-year market feed.
- Local dashboard snapshots are stored weekly instead of daily.
- Global Liquidity uses separate Destination, Allocation and Trend columns.


VERSION 8.1 DATE LOCALISATION AND EXTERNAL RESEARCH
- AUD displays dates as DD/MM/YY.
- USD displays dates as MM/DD/YY.
- Weekly-history, ETF and macro observation dates follow the selected currency.
- Compass Ai Analyst now provides deeper interpretation, competing evidence,
  scenario analysis, historical context and invalidation factors.
- Added optional External Financial Research through a private endpoint.
- Provider API keys remain on the private server rather than in GitHub Pages.


VERSION 8.1 RC1 EVIDENCE FRAMEWORK
- Compass Ai Analyst answers now separate Verified Facts, Market Interpretation,
  Supporting Evidence, Risks & Counterarguments, and View-Changing Conditions.
- Added Evidence-Based Mode, enabled by default.
- Added Conservative, Balanced and Opportunistic emphasis profiles.
- Added Show Evidence with source type, observation date, value and reliability rank.
- Added Evidence Quality and confidence summary based only on available data.
- External research requests now require attributable sources, publication dates,
  URLs, uncertainty labels and conflicting evidence.
- Anonymous claims, rumours, unsourced social posts and promotional content are
  explicitly excluded by the external research source policy.
- External answers without a source list are visibly marked incomplete.


VERSION 8.2 HISTORY AND MARKET INTELLIGENCE
- Added 1 Week and 1 Month daily history views.
- Retained weekly 3 Month, 6 Month, 1 Year, 2 Year and 4 Year views.
- Market articles sort newest first.
- Article metadata order is source, time, then star rating.
- Stars measure estimated global financial significance, not article quality.
- Added impact score, directional tag, affected-market tags and “Why this matters”.


VERSION 8.2.1 MARKET INTELLIGENCE DISPLAY REFINEMENT
- Increased market-significance star size for easier scanning.
- Added plain-language significance labels beside the stars.
- Removed the visible numeric importance/impact score.
- Removed the Watchlist label.
- Direction labels now appear only when classified as Bullish, Bearish or Neutral.
- The full article card remains the link to the source.
