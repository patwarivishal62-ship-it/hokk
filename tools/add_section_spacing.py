#!/usr/bin/env python3
"""Give every padded section real "Section spacing" controls.

Ten sections declared `padding_top` / `padding_bottom` and never read them, and
most sections had no spacing control at all. This script makes the global rule
in assets/base.css

    .section { padding-top: var(--section-pad-top, var(--section-space)); ... }

actually reachable from the editor:

  1. every section whose root element carries the `section` class gets a
     "Section spacing" header + `padding_top` / `padding_bottom` ranges
  2. every such section emits a scoped {% style %} block that sets those two
     custom properties on its own #shopify-section-<id> wrapper, so they
     inherit into `.section` (and never leak to a neighbouring section)
  3. sections that are not vertically padded (header, footer, marquee,
     announcement bar, cart drawer …) are left alone

Usage:
    python3 tools/add_section_spacing.py            # dry run
    python3 tools/add_section_spacing.py --apply    # write the changes
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SECTIONS = ROOT / 'sections'

SCHEMA_RE = re.compile(r'(\{%-?\s*schema\s*-?%\})(.*?)(\{%-?\s*endschema\s*-?%\})', re.S)
CLASS_RE = re.compile(r'class="([^"]*)"')

_RANGE_COMMON = {
    "type": "range",
    "min": 0,
    "max": 180,
    "step": 4,
    "unit": "px",
    "info": "Matches the global section spacing by default. On mobile this is scaled by the ratio in Theme settings › Layout.",
    "default": 96,
}
RANGE_TOP = dict(_RANGE_COMMON, id="padding_top", label="Top padding")
RANGE_BOTTOM = dict(_RANGE_COMMON, id="padding_bottom", label="Bottom padding")
HEADER = {"type": "header", "content": "Section spacing"}

STYLE_BLOCK = """{%- style -%}
  /* Section spacing — Theme settings › this section */
  #shopify-section-{{ section.id }} {
    --section-pad-top: {{ section.settings.padding_top }}px;
    --section-pad-bottom: {{ section.settings.padding_bottom }}px;
  }
{%- endstyle -%}
"""

# Sections that must never get vertical padding controls
SKIP = {
    'header.liquid', 'footer.liquid', 'announcement-bar.liquid', 'marquee.liquid',
    'cart-drawer.liquid', 'main-404.liquid',
}


def root_has_section_class(markup):
    for classes in CLASS_RE.findall(markup):
        if 'section' in classes.split():
            return True
    return False


def markup_of(text):
    return SCHEMA_RE.sub(' ', text)


def process(path, apply):
    name = path.name
    if name in SKIP:
        return None, 'skipped (not vertically padded)'
    text = path.read_text()
    m = SCHEMA_RE.search(text)
    if not m:
        return None, 'skipped (no schema)'
    schema = json.loads(m.group(2))
    markup = markup_of(text)
    if not root_has_section_class(markup):
        return None, 'skipped (no .section root)'

    ids = {s.get('id') for s in schema.get('settings', [])}
    changes = []

    # normalise settings that were already declared (older, inconsistent ranges)
    for s in schema.get('settings', []):
        canonical = {'padding_top': RANGE_TOP, 'padding_bottom': RANGE_BOTTOM}.get(s.get('id'))
        if canonical and s != canonical:
            s.clear()
            s.update(canonical)
            changes.append('schema ~ normalised ' + canonical['id'])

    if not {'padding_top', 'padding_bottom'} <= ids:
        settings = schema.setdefault('settings', [])
        if 'padding_top' not in ids:
            settings.append(HEADER)
            settings.append(RANGE_TOP)
        if 'padding_bottom' not in ids:
            settings.append(RANGE_BOTTOM)
        changes.append('schema += section spacing')

    if '--section-pad-top' not in markup:
        # insert the scoped style block just before the root element
        lines = text.split('\n')
        insert_at = None
        for i, line in enumerate(lines):
            if line.startswith('<'):
                insert_at = i
                break
        if insert_at is None:
            return None, 'skipped (could not locate root element)'
        lines.insert(insert_at, STYLE_BLOCK.rstrip('\n'))
        text = '\n'.join(lines)
        changes.append('markup += {% style %} padding vars')

    if any('schema' in c for c in changes):
        # NOTE: re-match on the *current* text — the style block inserted above
        # has shifted every offset, and stale ones silently splice the file.
        m = SCHEMA_RE.search(text)
        pretty = json.dumps(schema, indent=2, ensure_ascii=False)
        text = text[:m.start()] + m.group(1) + '\n' + pretty + '\n' + m.group(3) + text[m.end():]

    if changes and apply:
        path.write_text(text)
    return changes, None


def main():
    apply = '--apply' in sys.argv
    touched = 0
    for path in sorted(SECTIONS.glob('*.liquid')):
        changes, skip = process(path, apply)
        if skip:
            print(f'  ~ {path.name:32s} {skip}')
            continue
        if changes:
            touched += 1
            print(f'  {"+" if apply else "•"} {path.name:32s} {", ".join(changes)}')
    print()
    print(('applied to ' if apply else 'would change ') + f'{touched} section(s)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
