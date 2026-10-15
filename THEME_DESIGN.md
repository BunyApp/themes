# Designing a Good Theme

The JSON schema (`_template.json`) tells you which fields are required. It doesn't tell you
which surface each color paints, which colors sit on top of which, or how to keep the result
readable. This doc is that context — read it before picking hex values, not after.

`scripts/build.py --check` validates *shape* (right keys, valid hex, non-empty strings). It does
not and cannot validate *contrast*. A theme with perfectly formatted JSON can still be
unreadable. That part is on you (or the session writing the theme).

## Two kinds of theme, two jobs

- **`app/*.json`** — the app chrome: tab bar, nav bars, list rows, buttons, the background
  behind every screen. Each field is a `light|dark` pair — `"#RRGGBB|#RRGGBB"`.

  The `|dark` half is optional. `"#RRGGBB"` on its own is fine and just means "same color in
  both appearances":

  ```json
  "colorAccent": "#2772db"
  ```

  is equivalent to:

  ```json
  "colorAccent": "#2772db|#2772db"
  ```

  Only reach for this when a color is genuinely meant to be identical in light and dark — most
  fields (especially the backgrounds) should still differ per appearance.
- **`reader/*.json`** — only the reading surface (the text view itself) plus its chapter
  banner. A single hex per field — the reader has its own separate light/dark theme slots in
  the app, so one reader theme JSON only describes one look, not a light/dark pair.

Don't reuse a reader-theme mindset for app themes or vice versa — they're rendered by
completely different code paths and have different field shapes.

## App theme fields — what actually renders where

| Field | Renders as | Sits on top of |
|---|---|---|
| `colorAccent` | Tab bar selection tint, buttons, links, checkmarks, progress rings, icons. It is also the UIKit window tint, so search bar cursors and Cancel buttons and system alert buttons use it. **It is also a fill with white text on top:** selected listing chips, the active library filter, set search filters and the "Load More" button | `colorBackgroundPrimary`, `colorBackgroundHue` **and** `colorBackgroundSecondary`; and white text sits on it |
| `colorNavPrimary` | Nav bar title text, drawn over a frosted/blurred material | `colorBackgroundPrimary` (blurred, but treat as if solid) |
| `colorNavSecondary` | Section-header captions and "see more" links in the content area (History, Search, source pages) | `colorBackgroundPrimary` **and** `colorBackgroundHue` |
| `colorLabelPrimary` | Primary body/title text everywhere in the content area | `colorBackgroundPrimary` **and** `colorBackgroundSecondary` — this is the highest-traffic pair in the whole theme, check both |
| `colorLabelSecondary` | Secondary/caption text (subtitles, metadata) | Same as above |
| `colorBackgroundPrimary` | Top stop of the full-screen vertical gradient behind every screen | — |
| `colorBackgroundHue` | Bottom stop of that same gradient | — |
| `colorBackgroundSecondary` | List row / card backgrounds (settings rows, history items, source rows, analytics tiles, rows in sheets, the reader's settings sheet), sitting *on top of* the gradient | `colorBackgroundPrimary`/`colorBackgroundHue` (needs to read as a distinct surface, not blend in) |

`colorBackgroundPrimary` and `colorBackgroundHue` are not a foreground/background pair — they're
the two ends of one gradient. Keep them close in hue and lightness. A big jump between them
reads as a rendering bug, not a design choice. `colorBackgroundSecondary` is the one background
field that should visibly differ from the other two — it's what makes a list row look like a
raised card instead of empty space.

**Your app theme can also be a reading surface.** The reader has a built-in "App Theme" reader
theme. When someone picks it, a whole chapter is drawn as `colorLabelPrimary` on
`colorBackgroundPrimary`, and the chapter banner as `colorLabelPrimary` on
`colorBackgroundSecondary`. So hold `colorLabelPrimary` on `colorBackgroundPrimary` to the reader
bar below (aim for 7:1), not just the chrome bar.

## Reader theme fields

| Field | Renders as |
|---|---|
| `backgroundHex` / `textHex` | The full reading surface, read for long stretches — hold this pair to a higher bar than app chrome |
| `font` | Required and non-empty (`build.py` rejects `""`, so a store theme can't ask for the system font). The app hands it to `UIFont(name:)`, which matches a font's **full name** (`"Charter Roman"`) or **PostScript name**. It has to be a font that ships with iOS. A name iOS doesn't have falls back silently to the system font, with no error anywhere. See "Fonts" below |
| `bold` | Whether body text renders bold by default |
| `bannerBackgroundColor` / `bannerTextColor` | The chapter-title banner strip — its own independent foreground/background pair, doesn't need to relate to `backgroundHex`/`textHex` at all |

A good recipe for the banner pair: swap the reading pair's roles (background↔text) or pick an
accent duo that echoes the theme's mood — see `reader/forest.json`, where the banner is
literally `backgroundHex`/`textHex` swapped.

### Fonts

These names are confirmed to ship with iOS (checked against the iOS 27 runtime's font files) and
suit long reading: `"Georgia"`, `"Athelas Regular"`, `"Baskerville"`, `"Charter Roman"`,
`"Cochin"`, `"Hoefler Text"`, `"Iowan Old Style Roman"`, `"Marion Regular"`, `"Palatino"`,
`"Optima Regular"`, `"Avenir Next Regular"`, `"Seravek"`, `"Times New Roman"`.
The exact string matters: `"Optima"` and `"Avenir Next"` are family names, not face names, and
don't resolve.

Being installed on a Mac proves nothing: macOS ships fonts iOS doesn't. **`"Garamond"` is one of
them**, so a reader theme using it renders in the system font on iPhone. Apple's published font
lists also include download-on-demand fonts, which an app can't load by name either.

## Icon

`icon` is an SF Symbol name, drawn with `Image(systemName:)`. The app supports iOS 17.6, and a
symbol that doesn't exist there renders as empty space, with no error. SF Symbols 6 (iOS 18)
renamed many symbols (`doc.*` → `document.*`, `*.circlepath` → `*.trianglehead.*`). Use the
**old** names, which still work on newer iOS. Check availability in the SF Symbols app.

## Contrast: compute it, don't eyeball it

You can't render the theme to check it. Compute WCAG relative luminance instead — it's cheap
arithmetic and it's exact, so do this for every foreground/background pair called out above
rather than guessing from the hex values.

For each sRGB channel `c` (0–1, i.e. `hex_byte / 255`):

```
c_lin = c/12.92                        if c <= 0.03928
        ((c + 0.055) / 1.055) ^ 2.4    otherwise
```

```
L = 0.2126*R_lin + 0.7152*G_lin + 0.0722*B_lin
contrast_ratio = (L_lighter + 0.05) / (L_darker + 0.05)
```

Minimums (check **light and dark independently** — a pair that passes in dark mode can fail in
light mode with the same theme):

- `colorLabelPrimary` / `colorLabelSecondary` vs. both backgrounds it sits on: **≥ 4.5:1**, aim
  for 7:1 since this is read continuously, not glanced at.
- `colorAccent` vs. every background it sits on: **≥ 3:1 required, aim for 4.5:1**. It renders as
  text and icon color, not just a decorative fill.
- White vs. `colorAccent`: **≥ 3:1 required, aim for 4.5:1**, because chips, filters and "Load More"
  put white text on a solid accent fill. This pulls against the previous rule in dark mode: on a
  near-black background, an accent light enough to reach 4.5:1 against the background is usually
  too light for white text. A mid-tone accent that clears 3:1 both ways is the practical target.
  Very light accents (yellows, pastels) fail white text in both appearances.
- `colorNavPrimary` / `colorNavSecondary` vs. `colorBackgroundPrimary`: **≥ 4.5:1**.
- Reader `textHex` vs. `backgroundHex`: **≥ 7:1** — this is the one pair someone stares at for an
  entire chapter.
- Reader `bannerTextColor` vs. `bannerBackgroundColor`: **≥ 4.5:1**.
- App theme `colorLabelPrimary` vs. `colorBackgroundPrimary`: aim for **7:1**, because the App Theme
  reader theme uses it as a reading surface.

`colorBackgroundPrimary` vs. `colorBackgroundHue` is exempt — that pair is a gradient, not text
on a surface, so contrast between them isn't the goal (closeness is).

## Practical order of operations

1. Pick the background family first: `colorBackgroundPrimary` and `colorBackgroundHue` close
   together, then `colorBackgroundSecondary` a clear step lighter or darker than both (whichever
   direction fits the theme's mood).
2. Pick `colorLabelPrimary`/`colorLabelSecondary` against that background family, checking both
   surfaces above.
3. Pick `colorAccent` last — it's the one saturated color in the theme, so it must clear
   contrast against every surface it can land on, not just look nice in isolation.
4. Repeat 1–3 independently for light and dark. A theme that's a straight color-invert of itself
   for dark mode usually fails contrast on one side — dark mode isn't "the same theme with the
   hexes flipped."

## Quick don'ts

- Don't set `colorAccent` to the same hue and lightness as the background family — it
  disappears against exactly the surfaces it needs to stand out on.
- Don't treat "looks fine in dark mode" as proof the light half also works, or vice versa.
- Don't pick a reader `font` because it's on your Mac. Use a name from "Fonts" above.
- Don't use an SF Symbol newer than iOS 17.6 for `icon`.
- Don't skip `scripts/build.py --check` — it catches shape errors so review time goes to the
  actual color judgment calls, not typos.
