# The Chambers of Men — Brand Guidelines v2

**Status:** v2 (supersedes v1 teal/gold palette)
**Updated:** 2026-04-18
**Live styleguide:** `/styleguide/` (serves `templates/website/styleguide.html`)

---

## 1. Identity

**Vision:** Restoring Men to the Image of God
**Mandate:** Awaken. Equip. Deploy.
**Character:** A private-members-club feel — considered, crafted, after-hours. Warm and grounded, never corporate or generic. Tactile and printed rather than glossy and digital.

**Signature taglines:**
- "Keep climbing, brother."
- "You're not alone, brother."

---

## 2. Logo

The Chambers of Men mark is an **organic, hand-drawn "cm" script**. The curves echo rock formations and the contours of ascent. It is not the boxed "CM" placeholder used on v1 of the site — that mark is retired.

### Variants
- **Mark only** — the "cm" script alone. Use in navigation, favicons, and any compact context.
- **Lockup** — "cm" mark above "CHAMBERS OF MEN" wordmark. Use in hero surfaces, footers, deck title slides, and any standalone brand surface.
- **Wordmark only** — "CHAMBERS OF MEN" in DM Sans, all-caps, letterspaced. Use only when the mark is not viable (e.g. one-line footers, small format print).

### Asset files (delivered 2026-04-19)
Live in `static/brand/`:
- `cm-mark-black.png` — mark only, black silhouette on transparent. **Primary asset** — use as mask source.
- `cm-mark-white.png` — mark only, white. For direct `<img>` use on dark surfaces.
- `cm-lockup-black.png` — mark + "CHAMBERS OF MEN" wordmark, black.
- `cm-lockup-white.png` — mark + wordmark, white.

SVG not yet delivered. PNGs are high-resolution and work for web + decks. Ask the designer for SVG when convenient (sharper at print/large-format, smaller file).

### Recolouring via CSS mask-image

Because the logos are PNG, not SVG, they can't be recoloured with `fill` or `currentColor`. Use CSS `mask-image` instead — the black PNG becomes a shape mask, and the element's `background` becomes the logo colour. This is the preferred technique across the site.

```css
.logo-mark {
  display: inline-block;
  width: 40px; height: 40px;
  background: var(--cream);                  /* logo colour — swap to any token */
  -webkit-mask: url('/static/brand/cm-mark-black.png') center/contain no-repeat;
          mask: url('/static/brand/cm-mark-black.png') center/contain no-repeat;
}
.logo-lockup {
  display: inline-block;
  width: 160px; height: 110px;
  background: var(--cream);
  -webkit-mask: url('/static/brand/cm-lockup-black.png') center/contain no-repeat;
          mask: url('/static/brand/cm-lockup-black.png') center/contain no-repeat;
}
```

In Django templates, use `{% static "brand/cm-mark-black.png" %}` for the URL.

### Direct `<img>` use (alternative)

If a surface doesn't need recolouring and the logo is simply cream-on-dark, an `<img>` tag with `cm-mark-white.png` works fine and is slightly faster to render.

```html
<img src="{% static 'brand/cm-mark-white.png' %}" alt="Chambers of Men" width="40" height="40">
```

### Placement rules
| Surface | Variant | Size |
|---|---|---|
| Website nav | Mark only | 40px tall |
| Website hero | Lockup | 120–160px tall |
| Website footer | Lockup | 80px tall |
| Favicon | Mark only | 32px / 16px |
| Deck title slide | Lockup, centred | ~25% slide width |
| Deck content slide | Mark only, top-left | 40px tall, 48px from edges |
| Social avatar | Mark only on terracotta fill | Full bleed |

### Clear space
Minimum clear space around the mark equals the height of the "c" counter (the enclosed loop). Never crowd the mark against edges, rules, or other marks.

### Minimum size
- Mark: 24px tall (digital), 12mm tall (print)
- Lockup: 60px tall (digital), 25mm tall (print)

### Do not
- Redraw, re-outline, or re-weight the mark
- Place the mark on busy photography without a tint overlay (min 40% dark)
- Rotate, skew, stretch, or apply drop shadows
- Use the retired boxed "CM" initials
- Pair with teal or gold (v1 accents)

---

## 3. Colour System

The palette is **dark members-club base, terracotta primary, sage secondary**. Cream is the reading colour; deep slate is the ground. Blues and the raw-paper cream are tactile supports — they bridge the warm accents and the cool base.

### Tokens

```css
:root {
  /* Ground — the members-club dark base */
  --bg-deep: #0B0F14;          /* Near-black, cool-tinted. Page background. */
  --bg-base: #11161C;          /* Primary sections */
  --bg-surface: #181F28;       /* Cards, panels */
  --bg-elevated: #1F2731;      /* Raised cards, modals */
  --bg-card: rgba(24,31,40,.7);/* Glass cards */

  /* Primary accent — terracotta (replaces v1 teal) */
  --terracotta: #D17F56;
  --terracotta-light: #E39972;
  --terracotta-dim: #B86B47;
  --terracotta-glow: rgba(209,127,86,.15);

  /* Secondary accent — sage (replaces v1 gold) */
  --sage: #7A9879;
  --sage-light: #94AB93;
  --sage-dim: #5F7A5E;
  --sage-glow: rgba(122,152,121,.14);

  /* Tertiary — steel blue (info, supporting meta) */
  --steel: #7A95AE;
  --steel-light: #A8C5DE;
  --steel-dim: #5C7A95;
  --steel-glow: rgba(122,149,174,.10);

  /* Paper — the cream that carries the type */
  --cream: #EFE9DB;            /* Primary text, reverse surfaces */
  --cream-warm: #E8DFCC;       /* Slightly warmer for print/paper */

  /* Text */
  --text-primary: #EFE9DB;
  --text-secondary: #A8B0B8;
  --text-dim: #6B737C;

  /* Lines & glass */
  --border: rgba(239,233,219,.08);
  --border-hover: rgba(209,127,86,.22);
  --glass: rgba(24,31,40,.55);
  --glass-border: rgba(239,233,219,.08);
}
```

### Usage rules
- **Terracotta** is the call-to-action colour. Primary buttons, active nav underlines, key highlights, hover states, link accents. Never use it for body copy.
- **Sage** is for supporting emphasis: scripture references, italic pull quotes, secondary badges, "senior tier" labelling. Never stack sage next to terracotta without cream or dark between them — they vibrate.
- **Steel** is for meta information: dates, locations, frequency tags, status dots that aren't success/warning.
- **Cream** is the only reading colour on dark surfaces.
- **Paper-grain overlay** (see §5) sits above colour fills at ~1.8% opacity. Every large surface gets it.

### Inversion (light/paper surfaces)
Print collateral, deck cover cards, and physical artefacts can invert to paper:
- Background: `--cream-warm` (#E8DFCC)
- Body: `--bg-deep` (#0B0F14)
- Accent: `--terracotta-dim` (darker for contrast on cream)

Inversion is a controlled move. Don't invert digital surfaces without a clear reason — the members-club mood lives in the dark.

### Retired (do NOT use in v2)
| Legacy token | Hex | Replace with |
|---|---|---|
| `--teal` | `#14B8A6` | `--terracotta` |
| `--teal-light` | `#2DD4BF` | `--terracotta-light` |
| `--teal-dim` | `#0D9488` | `--terracotta-dim` |
| `--teal-glow` | `rgba(20,184,166,.15)` | `--terracotta-glow` |
| `--gold` | `#D4A853` | `--sage` |
| `--gold-light` | `#E8C068` | `--sage-light` |
| `--gold-dim` | `#B8923F` | `--sage-dim` |
| `--gold-glow` | `rgba(212,168,83,.12)` | `--sage-glow` |

---

## 4. Typography

Playfair Display (v1) was swapped out in v2. It was a high-contrast Didone — Mayfair formal, Vogue-adjacent — and too cool for the new hand-drawn mark. Cormorant Garamond is the replacement: an old-style Garamond revival that reads like a leather-bound library. It keeps the members-club gravitas while warming the terminals enough to partner the organic "cm" script. DM Sans stays as the body.

### Fonts
- **Cormorant Garamond** — headings, pull quotes. Weights 300, 400, 500, 600, 700. Italic 300–700.
- **DM Sans** — body, eyebrows, UI. Weights 300, 400, 500, 600, 700.

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300..700;1,300..700&family=DM+Sans:ital,opsz,wght@0,9..40,300..700;1,9..40,300..400&display=swap" rel="stylesheet">
```

### Scale

Cormorant Garamond's max weight is 700 (no 800/900). The headline weights below are calibrated to read with the same visual presence as Playfair 800 without over-darkening. Sizes are bumped slightly from v1 because Cormorant's old-style proportions read a touch smaller at the same pt.

| Role | Font | Size | Weight | Notes |
|---|---|---|---|---|
| Hero H1 | Cormorant Garamond | `clamp(3.2rem, 6.5vw, 5.5rem)` | 600 | letter-spacing -.015em, leading 1.05 |
| Section H2 | Cormorant Garamond | `clamp(2.2rem, 4.2vw, 3.2rem)` | 600 | leading 1.15 |
| Card H3 | Cormorant Garamond | 1.6rem | 600 | — |
| Eyebrow | DM Sans | 0.7rem | 600 | uppercase, tracking-.25em, preceded by a 32px hairline in terracotta |
| Body | DM Sans | 1rem | 400 | leading 1.7 |
| Small / meta | DM Sans | 0.82rem | 500 | text-dim |
| Pull quote | Cormorant Garamond italic | 1.45rem | 400 | sage-dim colour |

### Retired (do NOT use in v2)
- **Playfair Display** — too sharp, too cool. Used throughout v1. Replace on sight when migrating templates.

### Accent spans
- `.at` → terracotta (`color: var(--terracotta)`) — for emphasised words in H1/H2
- `.sg` → sage (`color: var(--sage)`) — for secondary emphasis, scripture, italicised phrases

---

## 5. Texture

Paper-grain is part of the identity. The logo sheet is tactile; the web surface must be too.

### Global noise overlay
```css
body::after {
  content: '';
  position: fixed; inset: 0;
  background: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='g'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23g)' opacity='.018'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 9999;
}
```

Keep opacity at 0.018. Any higher and the surface gets busy; any lower and it vanishes.

### Photo treatment
Photography should feel like it came from an analogue source — darkroom or printed matter:
- Desaturate 15–25% (`filter: saturate(0.8);`)
- Cool shadows, warm highlights (split-tone)
- **Photo-cutout** — a photograph clipped inside the "cm" mark itself (see logo sheet third frame). Used sparingly, for hero images and deck title slides. Implement with SVG `<mask>` or `clip-path`.

### Glass cards
```css
background: var(--glass);
backdrop-filter: blur(16px) saturate(1.2);
-webkit-backdrop-filter: blur(16px) saturate(1.2);
border: 1px solid var(--glass-border);
```

---

## 6. Iconography

**Feather icons**, 1.5px stroke, inline SVG (no icon font).

Why Feather: it matches the hand-drawn quality of the logo better than Material Symbols (which is The Flock's system) or Lucide (too technical).

```html
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
  <!-- path -->
</svg>
```

Icon colour inherits via `stroke="currentColor"` — set on the parent using `--terracotta`, `--sage`, etc.

---

## 7. Components

### Buttons

**Primary (CTA)**
```css
background: var(--terracotta);
color: var(--bg-deep);
padding: .9rem 2.2rem;
border-radius: 6px;
font: 600 .78rem/1 'DM Sans';
letter-spacing: .12em;
text-transform: uppercase;
```
Hover: lift 2px, glow `0 8px 32px rgba(209,127,86,.3)`, background `--terracotta-light`.

**Ghost**
```css
background: transparent;
color: var(--text-primary);
border: 1px solid var(--border);
/* same padding + type as primary */
```
Hover: border → `--sage-dim`, colour → `--sage`.

### Cards (glass)
- Background: `var(--glass)`, 16px blur
- Border: `var(--glass-border)`, hover → `var(--border-hover)`
- Radius: 12px
- Hover: translate-y -4px, shadow `0 16px 48px rgba(0,0,0,.3)`
- Optional top hairline on hover: `linear-gradient(90deg, transparent, var(--terracotta), transparent)`

### Hairline dividers
```html
<div class="sep"></div>
```
```css
.sep {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border), transparent);
  max-width: 1200px;
  margin: 0 auto;
}
```

### Eyebrow label
```html
<div class="eyebrow">The Mandate</div>
```
```css
.eyebrow {
  font: 600 .7rem/1 'DM Sans';
  letter-spacing: .25em;
  text-transform: uppercase;
  color: var(--terracotta);
  display: flex; align-items: center; gap: 1rem;
}
.eyebrow::before {
  content: '';
  width: 32px; height: 1px;
  background: var(--terracotta);
}
```

---

## 8. Motion

- **Reveal on scroll**: `.reveal` fades from `opacity:0; translateY(40px)` to visible on intersection. Easing `cubic-bezier(.16, 1, .3, 1)`, duration 800ms. Stagger with `.reveal-delay-1/2/3/4` (100/200/300/400ms).
- **Hover lift**: `translateY(-2px to -6px)` on cards and buttons.
- **Orbs**: two soft radial-gradient blobs in the hero (`filter: blur(100px)`), one terracotta one sage, animated with an 8s `float` keyframe.

No spring-heavy motion. No parallax. The mood is controlled and quiet, not showy.

---

## 9. Voice

- Warm, purposeful, brotherhood-focused
- Scripture-integrated where appropriate (Proverbs 27:17, Luke 2:52, Matthew 5:14, 1 Timothy 3:4, Ephesians 6:10)
- Never corporate, never casual-to-a-fault
- Opening: "Hi [First Name]," — not "Brother" or "Dear"
- Closing: "Keep climbing, brother. / Benedict / The Chambers of Men"
- Never use filler ("we're excited", "just wanted to check in")

---

## 10. Anti-patterns (v1 → v2 checklist)

When auditing a template:

- [ ] No `--teal`, `--teal-*`, `--gold`, `--gold-*` tokens remain
- [ ] Boxed "CM" nav placeholder replaced with the organic `cm` mark (or awaiting-SVG slot)
- [ ] Paper-grain noise overlay present (body::after)
- [ ] Playfair Display for headings, DM Sans for body
- [ ] Feather icons (1.5px stroke) — not Material Symbols, not Lucide, not emoji
- [ ] Cream (#EFE9DB) is the only reading colour on dark — no bright white `#fff`
- [ ] No saturated blues, greens, or purples outside the defined palette
- [ ] Eyebrows use terracotta hairline + letterspaced DM Sans
- [ ] Hero H1 uses Playfair 800 with accent span in terracotta (`.at`)
- [ ] No drop shadows under the logo
- [ ] No "CM" next to the organic mark (redundant)

---

## 11. Reference

- **Live styleguide**: `/styleguide/` — rendered components, palette swatches, type specimens
- **Logo sheet (reference image)**: `static/brand/reference/logo-sheet.png`
- **Obsidian mirror**: `brain/church/wiki/chambers-brand-v2.md`
- **Related wiki**: `brain/church/wiki/chambers-of-men-overview.md`
