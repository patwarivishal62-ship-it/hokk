#!/usr/bin/env python3
"""Validate the Kala Katha Shopify theme before it is zipped.

Checks, in order:
  1. every JSON file parses (config/, locales/, templates/)
  2. every section {% schema %} parses and is internally consistent
     (unique ids, valid types, defaults inside range/option lists, presets
      referencing real blocks and settings)
  3. every templates/*.json only references sections, settings, blocks and
     values that really exist
  4. config/settings_data.json (theme settings + header/footer groups)
  5. every `render`/`include` target exists as a snippet
  6. every `'key' | t` translation key exists in locales/en.default.json
  7. Liquid block tags are balanced in every .liquid file
  8. layout/theme.liquid has the OS 2.0 plumbing

Run:  python3 tools/validate.py
Exit code is 0 when the theme is clean, 1 when anything failed.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ERRORS = []
WARNINGS = []

# Official Shopify setting types — shopify.dev "Input settings" + "Sidebar settings".
# Anything outside this list makes the theme fail to upload.
OFFICIAL_TYPES = {
    # basic input settings
    'checkbox', 'number', 'radio', 'range', 'select', 'text', 'textarea',
    # specialised input settings
    'article', 'article_list', 'blog', 'collection', 'collection_list', 'color',
    'color_background', 'color_palette', 'color_scheme', 'color_scheme_group',
    'font_picker', 'html', 'image_picker', 'inline_richtext', 'link_list', 'liquid',
    'metaobject', 'metaobject_list', 'page', 'product', 'product_list', 'richtext',
    'text_alignment', 'url', 'video', 'video_url',
    # sidebar settings
    'header', 'paragraph',
    # app blocks
    '@app',
}

SETTINGS_DIR = ROOT / 'sections'
SNIPPETS_DIR = ROOT / 'snippets'
TEMPLATES_DIR = ROOT / 'templates'
LOCALES_DIR = ROOT / 'locales'


def err(msg):
    ERRORS.append(msg)


def warn(msg):
    WARNINGS.append(msg)


def read(path):
    return path.read_text(encoding='utf-8')


def rel(path):
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path):
    try:
        return json.loads(read(path))
    except Exception as exc:  # noqa: BLE001
        err(f'{rel(path)}: invalid JSON — {exc}')
        return None


# ---------------------------------------------------------------- settings
SCHEMA_RE = re.compile(r'\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema\s*-?%\}', re.S)
SETTINGS_WITHOUT_ID = {'header', 'paragraph'}


def on_step(value, minimum, step):
    """True when value sits on the range's step grid (float tolerant)."""
    if not step:
        return True
    ratio = (value - minimum) / step
    return abs(ratio - round(ratio)) < 1e-6
ID_RE = re.compile(r'^[a-z_][a-z0-9_]*$')


def check_setting(setting, where, ids_seen):
    stype = setting.get('type')
    if not stype:
        err(f'{where}: setting without a "type": {json.dumps(setting)[:120]}')
        return
    if stype in SETTINGS_WITHOUT_ID:
        if not setting.get('content'):
            err(f'{where}: {stype} setting needs a "content" string')
        return

    sid = setting.get('id')
    if not sid:
        err(f'{where}: {stype} setting has no "id"')
        return
    if not ID_RE.match(sid):
        err(f'{where}: invalid setting id "{sid}" (lowercase letters, numbers, underscores)')
    if sid in ids_seen:
        err(f'{where}: duplicate setting id "{sid}"')
    ids_seen.add(sid)

    if not setting.get('label') and stype not in {'@app'}:
        warn(f'{where}: setting "{sid}" has no label')

    if stype not in OFFICIAL_TYPES:
        err(f'{where}: invalid setting type "{stype}" for "{sid}" (not a documented Shopify setting type)')
        return

    default = setting.get('default')

    if stype == 'select':
        options = setting.get('options')
        if not options:
            err(f'{where}: select "{sid}" has no options')
        else:
            values = []
            for opt in options:
                if 'value' not in opt or 'label' not in opt:
                    err(f'{where}: select "{sid}" option missing value/label: {opt}')
                values.append(opt.get('value'))
            if default is not None and default not in values:
                err(f'{where}: select "{sid}" default "{default}" is not one of {values}')
            if not options[0].get('value') and default is None:
                warn(f'{where}: select "{sid}" has an empty first option and no default')
    elif stype == 'range':
        for key in ('min', 'max', 'step', 'default'):
            if key not in setting:
                err(f'{where}: range "{sid}" is missing "{key}"')
        if all(k in setting for k in ('min', 'max', 'step', 'default')):
            lo, hi, step, val = setting['min'], setting['max'], setting['step'], setting['default']
            if not lo <= val <= hi:
                err(f'{where}: range "{sid}" default {val} outside [{lo}, {hi}]')
            if step and not on_step(val, lo, step):
                err(f'{where}: range "{sid}" default {val} is not on a step of {step} from {lo}')
    elif stype == 'checkbox':
        if default is not None and not isinstance(default, bool):
            err(f'{where}: checkbox "{sid}" default must be true/false')
    elif stype in {'text', 'textarea', 'richtext', 'liquid', 'url', 'email', 'handle'}:
        if default is not None and not isinstance(default, str):
            err(f'{where}: {stype} "{sid}" default must be a string')
    elif stype == 'video_url':
        accept = setting.get('accept')
        if not accept:
            err(f'{where}: video_url "{sid}" needs an "accept" list')
    elif stype == 'font_picker':
        if default is not None and not isinstance(default, str):
            err(f'{where}: font_picker "{sid}" default must be a font handle string')


def check_schema(schema, path):
    where = rel(path)
    if not schema.get('name'):
        err(f'{where}: schema has no "name"')

    ids = set()
    for setting in schema.get('settings', []):
        check_setting(setting, where, ids)

    block_types = {}
    for block in schema.get('blocks', []):
        btype = block.get('type')
        if not btype:
            err(f'{where}: block without a "type"')
            continue
        if btype in block_types:
            err(f'{where}: duplicate block type "{btype}"')
        if btype != '@app' and not block.get('name'):
            warn(f'{where}: block "{btype}" has no "name"')
        bids = set()
        for setting in block.get('settings', []):
            check_setting(setting, f'{where} block "{btype}"', bids)
        block_types[btype] = block

    for preset in schema.get('presets', []):
        if not preset.get('name'):
            warn(f'{where}: preset without a name')
        used = {}
        for pblock in preset.get('blocks', []):
            ptype = pblock.get('type')
            if ptype not in block_types:
                err(f'{where}: preset references unknown block type "{ptype}"')
                continue
            used[ptype] = used.get(ptype, 0) + 1
            limit = block_types[ptype].get('limit')
            if isinstance(limit, int) and used[ptype] > limit:
                err(f'{where}: preset uses "{ptype}" {used[ptype]}x but its limit is {limit}')
            valid_ids = {s.get('id') for s in block_types[ptype].get('settings', [])}
            for key, value in pblock.get('settings', {}).items():
                if key not in valid_ids:
                    err(f'{where}: preset block "{ptype}" sets unknown setting "{key}"')
                else:
                    check_value(key, value, block_types[ptype]['settings'], f'{where} preset "{ptype}"')
        for key, value in preset.get('settings', {}).items():
            if key not in ids:
                err(f'{where}: preset sets unknown section setting "{key}"')
            else:
                check_value(key, value, schema.get('settings', []), f'{where} preset')
    return schema


def find_setting(sid, settings):
    for setting in settings or []:
        if setting.get('id') == sid:
            return setting
    return None


def check_value(sid, value, settings, where):
    setting = find_setting(sid, settings)
    if not setting:
        return
    stype = setting.get('type')
    if stype == 'select':
        allowed = [o.get('value') for o in setting.get('options', [])]
        if value not in allowed:
            err(f'{where}: setting "{sid}" value {value!r} is not one of {allowed}')
    elif stype == 'range':
        lo, hi, step = setting.get('min'), setting.get('max'), setting.get('step', 1)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            err(f'{where}: setting "{sid}" must be a number, got {value!r}')
        elif not lo <= value <= hi:
            err(f'{where}: setting "{sid}" value {value} outside [{lo}, {hi}]')
        elif step and not on_step(value, lo, step):
            err(f'{where}: setting "{sid}" value {value} is off the {step} step grid')
    elif stype == 'checkbox':
        if not isinstance(value, bool):
            err(f'{where}: setting "{sid}" must be true/false, got {value!r}')
    elif stype == 'collection_list':
        if not isinstance(value, list):
            err(f'{where}: setting "{sid}" must be a list of collection handles')
    elif stype in {'text', 'textarea', 'richtext', 'url', 'email', 'handle', 'liquid'}:
        if not isinstance(value, str):
            err(f'{where}: setting "{sid}" must be a string, got {value!r}')


# ----------------------------------------------------------------- sections
def collect_sections():
    schemas = {}
    for path in sorted(SETTINGS_DIR.glob('*.liquid')):
        match = SCHEMA_RE.search(read(path))
        if not match:
            err(f'{rel(path)}: no {{% schema %}} block')
            continue
        try:
            schema = json.loads(match.group(1))
        except Exception as exc:  # noqa: BLE001
            err(f'{rel(path)}: schema is not valid JSON — {exc}')
            continue
        check_schema(schema, path)
        schemas[path.stem] = schema
    return schemas


def check_settings_schema():
    path = ROOT / 'config' / 'settings_schema.json'
    data = load_json(path)
    if data is None:
        return {}
    if not isinstance(data, list):
        err('config/settings_schema.json must be a JSON array of groups')
        return {}
    ids = set()
    settings_by_id = {}
    for group in data:
        if not isinstance(group, dict):
            err('config/settings_schema.json: group is not an object')
            continue
        if 'theme_info' in group:
            continue
        if not group.get('name'):
            err('config/settings_schema.json: group without a name')
        for setting in group.get('settings', []):
            check_setting(setting, f"settings_schema group \"{group.get('name')}\"", ids)
            if setting.get('id'):
                settings_by_id[setting['id']] = setting
    return settings_by_id


# ---------------------------------------------------------------- templates
def check_template(path, schemas):
    data = load_json(path)
    if data is None:
        return
    where = rel(path)
    if not isinstance(data, dict) or 'sections' not in data:
        err(f'{where}: missing a "sections" object')
        return
    sections = data['sections']
    order = data.get('order')
    if order is None:
        err(f'{where}: missing an "order" array')
        order = list(sections.keys())
    if sorted(order) != sorted(sections.keys()):
        err(f'{where}: "order" does not match the section keys')

    seen_types = {}
    for sid, section in sections.items():
        stype = section.get('type')
        if not stype:
            err(f'{where}: section "{sid}" has no type')
            continue
        if stype not in schemas:
            err(f'{where}: section "{sid}" references unknown section "{stype}.liquid"')
            continue
        seen_types[stype] = seen_types.get(stype, 0) + 1
        schema = schemas[stype]
        s_where = f'{where} → {sid} ({stype})'

        for key, value in section.get('settings', {}).items():
            if find_setting(key, schema.get('settings', [])) is None:
                err(f'{s_where}: unknown section setting "{key}"')
            else:
                check_value(key, value, schema.get('settings', []), s_where)

        block_defs = {b['type']: b for b in schema.get('blocks', []) if b.get('type')}
        blocks = section.get('blocks', {})
        block_counts = {}
        for bid, block in blocks.items():
            btype = block.get('type')
            if btype not in block_defs:
                err(f'{s_where}: unknown block type "{btype}" (block "{bid}")')
                continue
            block_counts[btype] = block_counts.get(btype, 0) + 1
            limit = block_defs[btype].get('limit')
            if isinstance(limit, int) and block_counts[btype] > limit:
                err(f'{s_where}: block type "{btype}" appears {block_counts[btype]}x but its limit is {limit}')
            for key, value in block.get('settings', {}).items():
                if find_setting(key, block_defs[btype].get('settings', [])) is None:
                    err(f'{s_where}: block "{btype}" has unknown setting "{key}"')
                else:
                    check_value(key, value, block_defs[btype].get('settings', []), f'{s_where} block "{btype}"')

        block_order = section.get('block_order')
        if blocks and block_order is None:
            err(f'{s_where}: has blocks but no "block_order"')
        if block_order is not None:
            if sorted(block_order) != sorted(blocks.keys()):
                err(f'{s_where}: "block_order" does not match the block keys')

    for stype, count in seen_types.items():
        if stype.startswith('main-') and count > 1:
            err(f'{where}: section "{stype}" appears {count} times — only one main section is allowed')


def check_settings_data(schemas, theme_setting_ids):
    path = ROOT / 'config' / 'settings_data.json'
    data = load_json(path)
    if data is None:
        return
    current = data.get('current')
    if not isinstance(current, dict):
        err('config/settings_data.json: missing a "current" object')
        return

    for key, value in current.items():
        if key in {'sections'}:
            continue
        if key not in theme_setting_ids:
            err(f'settings_data.json current: unknown theme setting "{key}"')
        else:
            check_value(key, value, [theme_setting_ids[key]], 'settings_data.json current')
        setting = theme_setting_ids[key]
        if setting.get('type') == 'font_picker' and isinstance(value, str) and not re.match(r'^[a-z0-9_]+_[nio][0-9]$', value):
            warn(f'settings_data.json: font handle "{value}" looks unusual')

    groups = current.get('sections', {})
    for group_name in ('header-group', 'footer-group'):
        if group_name not in groups:
            err(f'settings_data.json: missing the "{group_name}" section group')
            continue
        group = groups[group_name]
        if group.get('type') != group_name:
            err(f'settings_data.json: "{group_name}" needs "type": "{group_name}"')
        gorder = group.get('sections', {})
        order = group.get('order', [])
        if sorted(order) != sorted(gorder.keys()):
            err(f'settings_data.json: "{group_name}" order does not match its sections')
        for sid, section in gorder.items():
            stype = section.get('type')
            if stype not in schemas:
                err(f'settings_data.json {group_name}: unknown section "{stype}"')
                continue
            schema = schemas[stype]
            s_where = f'settings_data.json {group_name} → {sid} ({stype})'
            for key, value in section.get('settings', {}).items():
                if find_setting(key, schema.get('settings', [])) is None:
                    err(f'{s_where}: unknown setting "{key}"')
                else:
                    check_value(key, value, schema.get('settings', []), s_where)
            block_defs = {b['type']: b for b in schema.get('blocks', []) if b.get('type')}
            blocks = section.get('blocks', {})
            counts = {}
            for bid, block in blocks.items():
                btype = block.get('type')
                if btype not in block_defs:
                    err(f'{s_where}: unknown block type "{btype}"')
                    continue
                counts[btype] = counts.get(btype, 0) + 1
                limit = block_defs[btype].get('limit')
                if isinstance(limit, int) and counts[btype] > limit:
                    err(f'{s_where}: block type "{btype}" exceeds its limit of {limit}')
                for key, value in block.get('settings', {}).items():
                    if find_setting(key, block_defs[btype].get('settings', [])) is None:
                        err(f'{s_where}: block "{btype}" has unknown setting "{key}"')
                    else:
                        check_value(key, value, block_defs[btype].get('settings', []), f'{s_where} block "{btype}"')
            if blocks and sorted(section.get('block_order', [])) != sorted(blocks.keys()):
                err(f'{s_where}: "block_order" does not match the block keys')
            if 'disabled_on' in schema and isinstance(schema['disabled_on'], dict):
                if group_name in schema['disabled_on'].get('groups', []):
                    err(f'{s_where}: this section is disabled on the {group_name} group')


# ------------------------------------------------------------- liquid files
RENDER_RE = re.compile(r'\{%-?\s*(?:render|include)\s+[\'"]([a-z0-9\-_]+)[\'"]', re.S)
T_RE = re.compile(r"'([a-z0-9_]+(?:\.[a-z0-9_]+)+)'\s*\|\s*t\b")
OPENERS = {'if', 'unless', 'for', 'form', 'capture', 'schema', 'stylesheet', 'javascript',
           'style', 'paginate', 'case', 'comment', 'tablerow', 'raw', 'block'}
CLOSERS = {'endif', 'endunless', 'endfor', 'endform', 'endcapture', 'endschema', 'endstylesheet',
           'endjavascript', 'endstyle', 'endpaginate', 'endcase', 'endcomment', 'endtablerow',
           'endraw', 'endblock'}
TAG_RE = re.compile(r'\{%-?\s*(\w+)', re.S)


def lookup(dotted, tree):
    cur = tree
    for part in dotted.split('.'):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def check_liquid(locales, snippet_names):
    for path in sorted(list(ROOT.rglob('*.liquid'))):
        if '.git' in path.parts:
            continue
        text = read(path)

        for name in RENDER_RE.findall(text):
            if name not in snippet_names:
                err(f'{rel(path)}: renders missing snippet "{name}"')

        for key in T_RE.findall(text):
            if lookup(key, locales) is None:
                err(f'{rel(path)}: uses missing translation key "{key}"')

        stack = []
        for match in re.finditer(r'\{%-?\s*(\w+)', text):
            tag = match.group(1)
            line = text[:match.start()].count('\n') + 1
            if tag in OPENERS:
                stack.append((tag, line))
            elif tag in CLOSERS:
                expected = tag[3:] if tag != 'endblock' else 'block'
                if tag == 'endif':
                    expected = 'if'
                elif tag == 'endunless':
                    expected = 'unless'
                if not stack:
                    err(f'{rel(path)}:{line}: "{tag}" without an opening tag')
                else:
                    open_tag, open_line = stack.pop()
                    if open_tag != expected:
                        err(f'{rel(path)}:{line}: "{tag}" closes "{{% {open_tag} %}}" opened on line {open_line}')
        for open_tag, open_line in stack:
            err(f'{rel(path)}:{open_line}: unclosed "{{% {open_tag} %}}"')


def check_layout():
    theme = ROOT / 'layout' / 'theme.liquid'
    if not theme.exists():
        err('layout/theme.liquid is missing')
        return
    text = read(theme)
    for needle, label in [
        ('{{ content_for_header }}', 'content_for_header'),
        ('{{ content_for_layout }}', 'content_for_layout'),
        ("{% sections 'header-group' %}", 'header-group'),
        ("{% sections 'footer-group' %}", 'footer-group'),
        ('<!doctype html>', 'doctype'),
        ('<html', 'html element'),
    ]:
        if needle not in text:
            err(f'layout/theme.liquid is missing {label}')

    if not (ROOT / 'layout' / 'password.liquid').exists():
        warn('layout/password.liquid is missing (the password page will use the theme layout)')


def check_assets():
    assets = ROOT / 'assets'
    theme_layout = read(ROOT / 'layout' / 'theme.liquid')
    for name in re.findall(r"'([a-z0-9\-_]+\.(?:css|js))'\s*\|\s*asset_url", theme_layout):
        if not (assets / name).exists():
            err(f'layout/theme.liquid loads missing asset "{name}"')
    for path in sorted(assets.glob('*')):
        if path.suffix in {'.css', '.js'}:
            continue
    for js in sorted(assets.glob('*.js')):
        pass


def main():
    schemas = collect_sections()
    theme_settings = check_settings_schema()

    for path in sorted(TEMPLATES_DIR.rglob('*.json')):
        check_template(path, schemas)

    check_settings_data(schemas, theme_settings)

    locales = load_json(LOCALES_DIR / 'en.default.json') or {}
    snippet_names = {p.stem for p in SNIPPETS_DIR.glob('*.liquid')}
    check_liquid(locales, snippet_names)
    check_layout()
    check_assets()

    print(f'sections: {len(schemas)}  templates: {len(list(TEMPLATES_DIR.rglob("*.json")))}  '
          f'snippets: {len(snippet_names)}  theme settings: {len(theme_settings)}')

    for message in WARNINGS:
        print('WARN ', message)
    for message in ERRORS:
        print('ERROR', message)

    if ERRORS:
        print(f'\n{len(ERRORS)} error(s), {len(WARNINGS)} warning(s)')
        return 1
    print(f'\nTheme is valid. {len(WARNINGS)} warning(s).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
