# Contributing a Theme

1. Fork this repo and create a branch.
2. Copy `app/_template.json` (app theme) or `reader/_template.json` (reader theme) to
   `<category>/<your_theme_id>.json`. Use snake_case for the filename, since it becomes the theme's id
   (`store.<filename>`). Renaming the file later changes the id.
3. Read [THEME_DESIGN.md](THEME_DESIGN.md), then fill in the fields. Don't add an `id` field; the
   filename supplies it. Every field is required, including `icon` (an SF Symbol available on iOS
   17.6) and, for reader themes, `font` (a font name that ships with iOS).
4. Run `python3 scripts/build.py --check` locally. It checks the JSON's shape only. Contrast, the
   icon and the font are on you: THEME_DESIGN.md says how to check each.
5. Open a PR. CI runs the same shape check automatically.
6. Once merged, your theme is live at the manifest URL within about a minute.
