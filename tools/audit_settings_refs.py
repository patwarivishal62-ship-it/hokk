#!/usr/bin/env python3
"""Audit settings references in Liquid markup.

Catches the most common silent bug in a hand-written theme: markup reading
`settings.foo` / `section.settings.foo` / `block.settings.foo` when no setting
with that id is declared. Shopify does not error on this - it just renders
blank, so the merchant sees a missing heading or an off switch that does
nothing.

Reports three buckets:
  1. theme settings   (settings.X) not declared in config/settings_schema.json
  2. section settings (section.settings.X) not declared in that section's schema
  3. block settings   (block.settings.X) not declared by any block of that section

Also lists `{% schema %}` settings that are never referenced in markup -
usually harmless (they may feed CSS through style attributes) but worth a look.

Run:  python3 tools/audit_settings_refs.py
"""
import json
import pathlib
import re
import sys
import collections

ROOT = pathlib.Path(__file__).resolve().parent.parent

# settings.<id> — but NOT section.settings.<id> / block.settings.<id> / opts.<id>
THEME_RE = re.compile(r'(?<![\w.])settings\.([a-zA-Z_][\w]*)')
SECTION_RE = re.compile(r'section\.settings\.([a-zA-Z_][\w]*)')
BLOCK_RE = re.compile(r'block\.settings\.([a-zA-Z_][\w]*)')
SCHEMA_RE = re.compile(r'\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema\s*-?%\}', re.S)
# markup-only region: strip schema, comment, stylesheet, javascript blocks
STRIP_RE = re.compile(
    r'\{%-?\s*schema\s*-?%\}.*?\{%-?\s*endschema\s*-?%\}'
    r'|\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}'
    r'|\{%-?\s*stylesheet\s*-?%\}.*?\{%-?\s*endstylesheet\s*-?%\}'
    r'|\{%-?\s*javascript\s*-?%\}.*?\{%-?\s*endjavascript\s*-?%\}',
    re.S,
)

# Liquid drops/objects that legitimately own a `.settings`-like namespace
IGNORE_THEME = {'blank', 'section', 'block'}


def theme_setting_ids():
    ids = set()
    schema = json.loads((ROOT / 'config' / 'settings_schema.json').read_text())
    for group in schema:
        for s in group.get('settings', []):
            if s.get('type') in ('header', 'paragraph'):
                continue
            if s.get('id'):
                ids.add(s['id'])
    return ids


def markup_only(text):
    return STRIP_RE.sub(' ', text)


def main():
    problems = []
    unused = []
    theme_ids = theme_setting_ids()

    files = sorted((ROOT / 'sections').glob('*.liquid')) + \
        sorted((ROOT / 'snippets').glob('*.liquid')) + \
        sorted((ROOT / 'layout').glob('*.liquid')) + \
        sorted((ROOT / 'templates').glob('*.liquid'))

    theme_used = collections.Counter()
    declared_per_file = {}

    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text()
        markup = markup_only(text)
        is_section = path.parent.name == 'sections'

        sec_ids, block_ids = set(), set()
        if is_section:
            m = SCHEMA_RE.search(text)
            if m:
                schema = json.loads(m.group(1))
                sec_ids = {s['id'] for s in schema.get('settings', []) if s.get('id')}
                for b in schema.get('blocks', []):
                    for s in b.get('settings', []):
                        if s.get('id'):
                            block_ids.add(s['id'])
                declared_per_file[rel] = sec_ids | block_ids

        # 1. theme settings
        for name in THEME_RE.findall(markup):
            if name in IGNORE_THEME:
                continue
            theme_used[name] += 1
            if name not in theme_ids:
                problems.append(f'{rel}: theme setting "settings.{name}" is not in settings_schema.json')

        # 2. section settings (only meaningful inside a section file)
        if is_section:
            for name in SECTION_RE.findall(markup):
                if name not in sec_ids:
                    problems.append(f'{rel}: "section.settings.{name}" is not declared in the section schema')
            for name in BLOCK_RE.findall(markup):
                if name not in block_ids:
                    problems.append(f'{rel}: "block.settings.{name}" is not declared by any block of this section')

    # 3. theme settings referenced only from snippets/layouts are fine, but a
    #    declared theme setting that nothing ever reads is usually dead weight
    never = sorted(theme_ids - set(theme_used))

    print(f'files scanned        : {len(files)}')
    print(f'theme settings used  : {len(theme_used)} distinct')
    print()
    if problems:
        print(f'UNDECLARED REFERENCES ({len(problems)}):')
        for p in sorted(set(problems)):
            print('  -', p)
    else:
        print('No undeclared settings references.')

    if never:
        print()
        print(f'THEME SETTINGS NEVER READ IN LIQUID ({len(never)}) - check these are wired up:')
        for n in never:
            print('  -', n)

    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
