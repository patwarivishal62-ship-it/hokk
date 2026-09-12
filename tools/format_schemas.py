#!/usr/bin/env python3
"""Normalise the formatting of every {% schema %} block.

Sections were authored by hand and later patched by scripts, so key order and
indentation drifted (a range setting might list "type, min, max, step, unit,
info, default, id, label"). Shopify only needs valid JSON, but the files are
read by humans in the repo, so this rewrites each schema with:

  * 2-space indentation
  * a canonical key order on the schema object and on every setting
  * non-ASCII characters preserved (—, ·, ₹ stay readable)

Markup outside the schema block is never touched.

Run:  python3 tools/format_schemas.py [--check]
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA_RE = re.compile(r'(\{%-?\s*schema\s*-?%\})(.*?)(\{%-?\s*endschema\s*-?%\})', re.S)

SCHEMA_ORDER = ['name', 'tag', 'class', 'wrapper', 'templates', 'enabled_on', 'disabled_on',
                'settings', 'blocks', 'max_blocks', 'single_in_tab', 'presets', 'locales',
                'documentation_url', 'style', 'limit']
SETTING_ORDER = ['type', 'id', 'label', 'info', 'content', 'default', 'placeholder',
                 'min', 'max', 'step', 'unit', 'options', 'accept', 'limit',
                 'metaobject_type', 'definition_id', 'visible_if', 'group', 'image_ratio']
BLOCK_ORDER = ['type', 'name', 'limit']
PRESET_ORDER = ['name', 'settings', 'blocks', 'block_order']


def order(d, keys):
    out = {}
    for k in keys:
        if k in d:
            out[k] = d[k]
    for k, v in d.items():          # anything unexpected keeps its place at the end
        if k not in out:
            out[k] = v
    return out


def normalise(obj):
    if isinstance(obj, dict):
        return {k: normalise(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalise(v) for v in obj]
    return obj


def main():
    check = '--check' in sys.argv
    changed = []
    for path in sorted((ROOT / 'sections').glob('*.liquid')):
        text = path.read_text()
        m = SCHEMA_RE.search(text)
        if not m:
            continue
        schema = json.loads(m.group(2))

        for key in ('settings',):
            if key in schema:
                schema[key] = [order(normalise(s), SETTING_ORDER) for s in schema[key]]
        if 'blocks' in schema:
            blocks = []
            for b in schema['blocks']:
                b = order(normalise(b), BLOCK_ORDER)
                if 'settings' in b:
                    b['settings'] = [order(normalise(s), SETTING_ORDER) for s in b['settings']]
                blocks.append(b)
            schema['blocks'] = blocks
        if 'presets' in schema:
            presets = []
            for p in schema['presets']:
                p = order(normalise(p), PRESET_ORDER)
                if 'blocks' in p:
                    p['blocks'] = [order(normalise(b), BLOCK_ORDER + ['settings']) for b in p['blocks']]
                presets.append(p)
            schema['presets'] = presets
        schema = order(schema, SCHEMA_ORDER)

        pretty = json.dumps(schema, indent=2, ensure_ascii=False)
        new_text = text[:m.start()] + m.group(1) + '\n' + pretty + '\n' + m.group(3) + text[m.end():]
        if new_text != text:
            changed.append(path.name)
            if not check:
                path.write_text(new_text)

    verb = 'need formatting' if check else 'reformatted'
    print(f'{verb}: {len(changed)} section schema(s)')
    for name in changed:
        print('  -', name)
    return 1 if (check and changed) else 0


if __name__ == '__main__':
    sys.exit(main())
