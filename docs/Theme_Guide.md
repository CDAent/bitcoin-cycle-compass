# Theme Guide
## Bitcoin Cycle Compass — Version 8.7 · Sprint 0

All design tokens are declared in the CSS `:root` block inside `index.html`. No external design system or CSS framework is used. All values below are taken directly from the source file — no new colours have been invented.

---

## 1. CSS Custom Properties (Design Tokens)

All tokens are declared in a single `:root` block and versioned additions are appended inline:

```css
/* Primary tokens */
:root {
  /* Backgrounds */
  --bg:          #040b13;   /* Page background (deep navy black) */
  --sidebar:     #050c14;   /* Sidebar background */
  --panel:       #07121d;   /* Card / panel background */
  --panel2:      #091724;   /* Secondary panel background */

  /* Borders & Lines */
  --line:        #1d3445;   /* Default border / separator */
  --card-border: #19334a;   /* Card border colour */

  /* Text */
  --text:        #eef5fb;   /* Primary text (near-white) */
  --muted:       #91a0ad;   /* Muted / secondary text */

  /* Signal Colours */
  --green:       #3ecf48;   /* Positive / bullish */
  --green-soft:  #55c96b;   /* Slightly bullish (softer green) */
  --amber:       #ffb300;   /* Neutral / warning / watch */
  --red:         #ff4444;   /* Negative / bearish */
  --blue:        #1da1f2;   /* Informational / source dots */
  --gold:        #f5a800;   /* Key highlights, active nav, headings */

  /* Signal Background Fills */
  --green-bg:    #0e2e14;   /* Green tint background */
  --red-bg:      #2a0e0e;   /* Red tint background */
  --amber-bg:    #2a1e00;   /* Amber tint background */

  /* Spacing (added v8.3.1) */
  --card-radius:    12px;   /* Card border-radius */
  --control-radius:  9px;   /* Button / input border-radius */
  --space-xs:        6px;
  --space-sm:       10px;
  --space-md:       14px;
  --space-lg:       18px;
}
```

---

## 2. Colour Palette

### 2.1 Background Colours

| Token | Hex | Usage |
|---|---|---|
| `--bg` | `#040b13` | Root page background (radial gradient base) |
| `--sidebar` | `#050c14` | Desktop sidebar background |
| `--panel` | `#07121d` | Cards, detail panels, answer cards |
| `--panel2` | `#091724` | Secondary content areas |

Additional non-token background values used inline:

| Value | Context |
|---|---|
| `#06101a` → `#03080d` | Sidebar gradient (top to bottom) |
| `#04101a` | Input / select background |
| `#06101b` | `theme-color` meta tag |
| `#07111a` | Event card background |
| `#07121d` | Alert card, article card background |
| `#08121d` | Regime score display, alert status card |
| `#061019` | Alert live row background |
| `#081722` | Range button, quick prompt background |
| `#0b1b27` | Alert action button background |
| `#071722` | Refresh status, news intel summary |
| `#0a1722` | Active nav item, section notes |

---

### 2.2 Signal Colours (Positive / Negative / Neutral)

| Token | Hex | CSS Class | Usage |
|---|---|---|---|
| `--green` | `#3ecf48` | `.pos` | Positive signal, bullish, rising values |
| `--green-soft` | `#55c96b` | `.market-state-slightly-bullish` | Slightly bullish |
| `--amber` | `#ffb300` | `.neu` | Neutral, mixed signals, warning |
| `--red` | `#ff4444` | `.neg` | Negative signal, bearish, falling values |
| `--blue` | `#1da1f2` | `.source::before` | Source indicators, informational |
| `--gold` | `#f5a800` | Active nav, headings, highlights | Key UI accents |

---

### 2.3 Market State Colour Mapping

Market states are determined by the `normalizeMarketState()` function and applied via `marketStateClass()`:

| State | CSS Class | Colour | Score Range |
|---|---|---|---|
| **Bullish** | `.market-state-bullish` | `--green` `#3ecf48` | ≥ 70 |
| **Slightly Bullish** | `.market-state-slightly-bullish` | `--green-soft` `#55c96b` | 55–69 |
| **Neutral** | `.market-state-neutral` | `--muted` `#91a0ad` | 45–54 |
| **Slightly Bearish** | `.market-state-slightly-bearish` | `--amber` `#ffb300` | 32–44 |
| **Bearish** | `.market-state-bearish` | `--red` `#ff4444` | < 32 |

Score pill background colours when states are applied to `.score-pill`:

| State | Background | Text Colour |
|---|---|---|
| `.market-state-bullish` | `var(--green-bg)` `#0e2e14` | `var(--green)` `#3ecf48` |
| `.market-state-slightly-bullish` | `var(--green-bg)` `#0e2e14` | `var(--green-soft)` `#55c96b` |
| `.market-state-neutral` | `#111821` with `1px solid var(--line)` | `var(--muted)` `#91a0ad` |
| `.market-state-slightly-bearish` | `var(--amber-bg)` `#2a1e00` | `var(--amber)` `#ffb300` |
| `.market-state-bearish` | `var(--red-bg)` `#2a0e0e` | `var(--red)` `#ff4444` |
| `.static` (plain) | `#102030` | `#eef5fb` with `1px solid #244153` |

---

### 2.4 Market Regime Background Colours (Regime Score Display)

Applied directly to `#regimeScore.style.background` in `render()`:

| Regime | Background |
|---|---|
| Bullish | `#143e1c` |
| Slightly Bullish | `#13381d` |
| Neutral | `#111821` |
| Slightly Bearish | `#2a1e00` |
| Bearish | `#3d1212` |

---

### 2.5 Status Colours

#### Success / Positive Status

| Element | Colour | CSS |
|---|---|---|
| Refresh status success border | `#2d6f38` | `.refresh-status.success` |
| Refresh status success text | `#8fe39f` | `.refresh-status.success` |
| Support status success | `#8fe39f` | `.support-status.success` |
| Alert enabled indicator | `var(--green)` `#3ecf48` | `.alert-card.enabled .alert-card-indicator` |
| Alert active dot | `var(--green)` with glow | `.alert-dot.active` |

#### Warning / Neutral Status

| Element | Colour | CSS |
|---|---|---|
| Alert disabled indicator | `var(--muted)` `#91a0ad` | `.alert-card-indicator` (default) |
| Alert dot inactive | `var(--muted)` `#91a0ad` | `.alert-dot` (default) |

#### Error / Negative Status

| Element | Colour | CSS |
|---|---|---|
| Refresh status error border | `#7c2e2e` | `.refresh-status.error` |
| Refresh status error text | `#ff8f8f` | `.refresh-status.error` |
| Support status error | `#ff8f8f` | `.support-status.error` |
| Alert error text | `#ff8f8f` | `.alert-error` |
| Alert triggered comparison | `var(--red-bg)` background, `var(--red)` text | `.alert-live-comparison.triggered` |

#### Alert OK Status

| Element | Colour | CSS |
|---|---|---|
| Alert OK comparison | `#0e2410` background, `var(--green)` text | `.alert-live-comparison.ok` |

---

### 2.6 Warning / Watchlist Colours

| Element | Colour |
|---|---|
| `market-impact.watchlist` | `#55a9ff` |
| `market-impact.bullish` | `var(--green)` `#3ecf48` |
| `market-impact.bearish` | `var(--red)` `#ff4444` |
| `market-impact.neutral` | `var(--amber)` `#ffb300` |

---

### 2.7 Evidence Quality Badge Colours

Rendered by `.fact-badge` in the Analyst view:

| Quality | Class | Text Colour | Border Colour |
|---|---|---|---|
| High | `.fact-badge.high` | `#50d890` | `#23734c` |
| Medium | `.fact-badge.medium` | `#f1bd48` | `#7f6421` |
| Low | `.fact-badge.low` | `#ef6d6d` | `#7c3030` |

---

### 2.8 Candlestick Chart Colours

| Signal | Class | Fill & Stroke |
|---|---|---|
| Up candle | `.candle-up` | `#3ecf48` (= `--green`) |
| Down candle | `.candle-down` | `#ff4444` (= `--red`) |

History movement arrows:

| Direction | Class | Colour |
|---|---|---|
| Up | `.move-arrow-up` | `var(--green)` |
| Down | `.move-arrow-down` | `var(--red)` |

---

### 2.9 Glossary Icon Tone Colours

| Tone | Class | Background | Text |
|---|---|---|---|
| Positive | `.glossary-icon.tone-pos` | `var(--green-bg)` | `var(--green)` |
| Neutral | `.glossary-icon.tone-neu` | `var(--amber-bg)` | `var(--amber)` |
| Negative | `.glossary-icon.tone-neg` | `var(--red-bg)` | `var(--red)` |
| Gold | `.glossary-icon.tone-gold` | `#1a2a10` | `var(--gold)` |

---

## 3. Arrow Mapping

Arrows are rendered as Unicode characters by JavaScript functions:

### 3.1 Market State Arrows (`marketStateArrow()`)

| State | Arrow |
|---|---|
| `bullish` | `▲` |
| `slightly-bullish` | `▲` |
| `neutral` | `➜` |
| `slightly-bearish` | `▼` |
| `bearish` | `▼` |

### 3.2 Movement Arrows (`movementArrow()`)

| Condition | Arrow |
|---|---|
| Positive (value > EPSILON) | `▲` |
| Negative (value < −EPSILON) | `▼` |
| Flat (≈ 0) | `•` |

### 3.3 Trend Arrows in History Table

| Direction | Character | CSS Class |
|---|---|---|
| Up | `▲` | `.move-arrow-up` (green) |
| Down | `▼` | `.move-arrow-down` (red) |

### 3.4 Regime Movement Arrows (in Regime Card)

Calculated from `regimeScore - prevScore`:

| Delta | Arrow | Class |
|---|---|---|
| Positive | `▲ +N this week` | `movement-pos` |
| Negative | `▼ N this week` | `movement-neg` |

---

## 4. Typography

### 4.1 Font Stack

```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
```

System UI fonts are used throughout. No external font CDN.

### 4.2 Font Sizes

| Context | Size |
|---|---|
| App title (desktop) | `24px` |
| Detail panel title (`h2`) | `26px` |
| Card heading (`h3`) | `13px` |
| Detail card heading (`h4`) | uses default |
| Large score / probability (`big-score`, `probability`) | `46–52px` |
| Live BTC price | `29px` |
| Regime score number | `48px` |
| Fear & Greed value | `39px` |
| Stable value / ETF value | `29px` |
| Research score reading | `14px` |
| Overall market signal | `20px` |
| Signal animal emoji | `38px` |
| Score denominator | `22px` |
| Score sub-label | `15px` |
| Forecast range | `16–17px` |
| Nav item | `14px` |
| Card small text | `11px` |
| Source badges | `9–11px` |
| Rank row text | `12px` |
| News item | `10px` |
| Footer | `10px` |
| Market star rating | `16–20px` |
| Market article headline | `13.5px` |
| Market article summary | `11.5px` |

### 4.3 Font Weights

| Usage | Weight |
|---|---|
| Large scores, probabilities | `900` |
| App title, nav active label | `900` |
| Section headings | `800` |
| Score pills, trend arrows | `900` |
| Body text | `400` (inherited) |
| Star rating (filled) | `400–500` |
| Star rating (empty) | `200` |

---

## 5. Spacing

All spacing uses the tokens defined in `:root` (added v8.3.1) plus raw pixel values:

| Token | Value | Usage |
|---|---|---|
| `--space-xs` | `6px` | Tight gaps, small padding |
| `--space-sm` | `10px` | Internal card padding, gap |
| `--space-md` | `14px` | Standard card padding |
| `--space-lg` | `18px` | Section gaps |

Dashboard grid gap: `10px`
Card padding: `13px` (dashboard), `14px` (detail card via `--space-md`)

---

## 6. Border Radius

| Token | Value | Applied To |
|---|---|---|
| `--card-radius` | `12px` | `.card`, `.detail-card`, `.analyst-chat`, `.answer-card` |
| `--control-radius` | `9px` | Buttons, inputs, selects |

Additional radii used inline:

| Value | Context |
|---|---|
| `999px` | Fully rounded pills (`.toggle`, `.score-pill`, `.range-btn`, `.fact-badge`) |
| `8px` | Alert cards, setting inputs, news items, pin buttons |
| `10px` | Alert cards, refresh status, market articles |
| `11px` | Dashboard cards |
| `7px` | Alert field inputs and selects |
| `4px` | Event tag |

---

## 7. Dark Theme

The application is **dark-only**. No light theme exists.

The root background uses a radial gradient:

```css
background: radial-gradient(circle at 80% 0, #0b1c2b 0, #040b13 46%);
```

The `theme-color` meta tag is `#06101b`, matching the dark sidebar.

`manifest.json` sets:
```json
"background_color": "#040b13",
"theme_color": "#06101b"
```

---

## 8. Animated Compass Logo

The animated compass logo uses two overlapping PNG images with CSS transform:

```css
/* Needle pivot — adjusted for physical hub alignment */
.logo-needle {
  transform-origin: 49.64% 36.48%;
  transform: rotate(0deg);
  will-change: transform;
}

/* Spinning during refresh */
.logo-wrap.refreshing .logo-needle {
  animation: compassSpin 0.82s linear infinite;
}

@keyframes compassSpin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
```

Same animation applies to the mobile header logo (`.mobile-shared-header.refreshing .mobile-logo-needle`).

---

## 9. Button Styles

### Primary Button (`.primary-btn`)

```css
border: 1px solid #ffc233;
background: linear-gradient(#d98f00, #8f5c00);
color: #fff;
padding: 9px 13px;
border-radius: 8px;
font-weight: 800;
min-height: 44px;
```

Active state (`currency-btn.active`):
```css
box-shadow: 0 0 0 2px #ffc23355;
```

Inactive currency button:
```css
background: #07131f;
border-color: #355064;
color: #b9c5cd;
```

### Analyst Send Button

```css
background: linear-gradient(#d98f00, #8f5c00);
color: #fff;
font-weight: 900;
border-radius: 9px;
```

### Range / Control Buttons (`.range-btn`)

```css
border: 1px solid #29465a;
background: #081722;
color: #bfcbd3;
border-radius: 999px;
font-weight: 800;
```

Active state:
```css
border-color: var(--gold);
color: var(--gold);
background: #201806;
```

---

## 10. Focus States

All interactive elements have explicit focus-visible outlines (added v8.3.1):

```css
.nav-btn:focus-visible,
.range-btn:focus-visible,
.analyst-send:focus-visible,
.quick-prompt:focus-visible,
.pin-btn:focus-visible,
.analyst-input:focus-visible,
.analyst-select:focus-visible {
  outline: 2px solid #f5b83d;
  outline-offset: 2px;
}
```

Alert inputs focus:
```css
outline: 2px solid #f5a80055;
border-color: var(--gold);
```

Settings inputs focus:
```css
outline: none;
border-color: var(--gold);
```

---

## 11. Responsive Breakpoints

| Breakpoint | Layout Change |
|---|---|
| `max-width: 1180px` | Sidebar narrows to `170px`; card columns rebalanced |
| `max-width: 900px` | Analyst panel stacks; allocation row shrinks |
| `max-width: 820px` | Full mobile layout: sidebar hidden, mobile header shown, dashboard stacks to single column |
| `max-width: 760px` | Detail grid stacks, analyst input stacks, history controls scroll |

Accessibility:
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

@media (hover: none) {
  button:hover { transform: none; }
  .card[data-open]:hover { transform: none; }
}
```

---

## 12. Transition & Animation

| Element | Transition |
|---|---|
| Buttons (hover/active) | `background-color 0.16s ease`, `border-color 0.16s ease`, `transform 0.12s ease`, `opacity 0.16s ease` |
| Button hover | `transform: translateY(-1px)` |
| Button active | `transform: translateY(0)` |
| Detail panel view | `.view-panel` animation: `viewFade 0.18s ease` |
| Mobile drawer | `transform 0.24s ease` |
| Mobile overlay | `opacity 0.2s ease` |
| Research needle | `left 0.5s ease` |
| Fear & Greed needle | `0.5s` (via inline style) |
| Alert card border | `border-color 0.15s ease` |
| Market article border | `border-color 0.15s ease` |
| Alert dot background | `background 0.2s ease` |
| Loading spinner | `spin 0.8s linear infinite` |

```css
@keyframes viewFade {
  from { opacity: 0.3; transform: translateY(3px); }
  to   { opacity: 1;   transform: none; }
}
```
