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
