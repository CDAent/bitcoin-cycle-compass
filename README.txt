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
