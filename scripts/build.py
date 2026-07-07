#!/usr/bin/env python3
"""Validates and assembles the Buny theme store manifest from per-theme JSON files."""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FILENAME_RE = re.compile(r"^[a-z0-9_]+\.json$")
APP_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}\|#[0-9a-fA-F]{6}$")
READER_HEX_RE = re.compile(r"^[0-9A-Fa-f]{6}$")

APP_COLOR_KEYS = [
    "colorAccent", "colorNavPrimary", "colorNavSecondary",
    "colorLabelPrimary", "colorLabelSecondary", "colorBackgroundPrimary",
    "colorBackgroundSecondary", "colorBackgroundHue",
]
APP_KEYS = {"label", "icon", "author", *APP_COLOR_KEYS}

READER_HEX_KEYS = ["backgroundHex", "textHex", "bannerTextColor", "bannerBackgroundColor"]
READER_KEYS = {"label", "icon", "author", "font", "bold", *READER_HEX_KEYS}


class ValidationError(Exception):
    pass


def _require_nonempty_str(theme, key, path):
    if not isinstance(theme.get(key), str) or not theme[key].strip():
        raise ValidationError(f"{path}: '{key}' must be a non-empty string")


def validate_app_theme(theme, path):
    keys = set(theme.keys())
    if keys != APP_KEYS:
        raise ValidationError(
            f"{path}: key mismatch (extra={sorted(keys - APP_KEYS)}, missing={sorted(APP_KEYS - keys)})"
        )
    _require_nonempty_str(theme, "label", path)
    _require_nonempty_str(theme, "icon", path)
    _require_nonempty_str(theme, "author", path)
    for key in APP_COLOR_KEYS:
        if not APP_COLOR_RE.match(theme[key]):
            raise ValidationError(f"{path}: '{key}' must match '#RRGGBB|#RRGGBB'")


def validate_reader_theme(theme, path):
    keys = set(theme.keys())
    if keys != READER_KEYS:
        raise ValidationError(
            f"{path}: key mismatch (extra={sorted(keys - READER_KEYS)}, missing={sorted(READER_KEYS - keys)})"
        )
    _require_nonempty_str(theme, "label", path)
    _require_nonempty_str(theme, "icon", path)
    _require_nonempty_str(theme, "author", path)
    _require_nonempty_str(theme, "font", path)
    if not isinstance(theme["bold"], bool):
        raise ValidationError(f"{path}: 'bold' must be a bool")
    for key in READER_HEX_KEYS:
        if not READER_HEX_RE.match(theme[key]):
            raise ValidationError(f"{path}: '{key}' must be a 6-digit hex string")


def load_category(dirname, validate):
    directory = ROOT / dirname
    themes = []
    seen_ids = set()
    if not directory.is_dir():
        return themes
    for path in sorted(directory.glob("*.json")):
        if path.name.startswith("_"):
            continue
        if not FILENAME_RE.match(path.name):
            raise ValidationError(f"{path}: filename must match ^[a-z0-9_]+\\.json$")
        theme_id = f"store.{path.stem}"
        if theme_id in seen_ids:
            raise ValidationError(f"{path}: duplicate id '{theme_id}'")
        seen_ids.add(theme_id)
        data = json.loads(path.read_text())
        validate(data, path)
        themes.append({"id": theme_id, **data})
    return themes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate only (default behavior)")
    parser.add_argument("--build", action="store_true", help="also write manifest.json")
    parser.add_argument("--out", default="_site", help="output directory for --build")
    args = parser.parse_args()

    try:
        app_themes = load_category("app", validate_app_theme)
        reader_themes = load_category("reader", validate_reader_theme)
    except ValidationError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"ok: {len(app_themes)} app theme(s), {len(reader_themes)} reader theme(s)")

    if args.build:
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        manifest = {"version": 1, "appThemes": app_themes, "readerThemes": reader_themes}
        (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"wrote {out_dir / 'manifest.json'}")


if __name__ == "__main__":
    main()
