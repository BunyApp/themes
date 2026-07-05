# Contributing a Theme

1. Fork this repo and create a branch.
2. Copy `app/_template.json` (app theme) or `reader/_template.json` (reader theme) to
   `<category>/<your_theme_id>.json`. Use snake_case for the filename, since it becomes the theme's id.
3. Fill in the fields. Don't add an `id` field; the filename supplies it.
4. Run `python3 scripts/build.py --check` locally.
5. Open a PR. CI runs the same check automatically.
6. Once merged, your theme is live at the manifest URL within about a minute.
