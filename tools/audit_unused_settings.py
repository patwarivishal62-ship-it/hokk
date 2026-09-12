#!/usr/bin/env python3
"""Reverse audit: schema settings that nothing in the markup ever reads.

A declared setting the section never reads is a dead knob in the editor — the
merchant moves a slider and nothing happens. This is the second half of
tools/audit_settings_refs.py (which looks for the opposite: markup reading a
setting that was never declared).

Known blind spots, reported but not counted as failures:
  * a section that passes its whole settings object into a snippet
    (`render 'x', opts: section.settings`) — those reads cannot be traced here
  * block settings read only through `block.settings[block_type]`-style tricks

Run:  python3 tools/audit_unused_settings.py [--verbose]
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA_RE = re.compile(r'\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema\s*-?%\}', re.S)
STRIP_RE = re.compile(
    r'\{%-?\s*schema\s*-?%\}.*?\{%-?\s*endschema\s*-?%\}'
    r'|\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}',
    re.S,
)
SIDEBAR = {'header', 'paragraph'}
WHOLESALE_RE = re.compile(r"(section\.settings|settings)\s*(?:\||,\s*block|-?%\})")


def main():
    verbose = '--verbose' in sys.argv
    dead = []
    wholesale = []

    for path in sorted((ROOT / 'sections').glob('*.liquid')):
        text = path.read_text()
        m = SCHEMA_RE.search(text)
        if not m:
            continue
        schema = json.loads(m.group(1))
        markup = STRIP_RE.sub(' ', text)

        passed_whole = bool(re.search(r'(?:opts|s|settings|cfg)\s*:\s*section\.settings', markup))
        if passed_whole:
            wholesale.append(path.name)

        # A section that hands the whole block object to a snippet
        # (`render 'faq-item', block: block`) reads those settings over there,
        # so count the reads that happen inside that snippet.
        block_reads = set()
        for snippet in re.findall(r"render\s+'([a-z0-9\-_]+)'[^%]*?\bblock\s*:\s*block", markup):
            snippet_path = ROOT / 'snippets' / (snippet + '.liquid')
            if snippet_path.exists():
                block_reads |= set(re.findall(r'\.settings\.([a-zA-Z_]\w*)', snippet_path.read_text()))

        def check(settings, where):
            if passed_whole:
                return  # reads happen inside the snippet; cannot be traced here
            for s in settings:
                sid = s.get('id')
                if not sid or s.get('type') in SIDEBAR:
                    continue
                # the only reliable read pattern: section.settings.<id> / block.settings.<id>
                pat = re.compile(r'\.settings\.' + re.escape(sid) + r'\b')
                if pat.search(markup):
                    continue
                if where.startswith('block:') and sid in block_reads:
                    continue
                dead.append((path.name, where, sid, s.get('label')))

        check(schema.get('settings', []), 'section')
        for b in schema.get('blocks', []):
            check(b.get('settings', []), 'block:' + str(b.get('type')))

    print(f'sections scanned       : {len(list((ROOT / "sections").glob("*.liquid")))}')
    print(f'pass whole settings obj : {len(wholesale)} ({", ".join(wholesale[:6])}{" …" if len(wholesale) > 6 else ""})')
    print()
    if dead:
        print(f'DEAD SETTINGS ({len(dead)}) — declared but never read:')
        for f, where, sid, label in dead:
            if verbose or where == 'section':
                print(f'  - {f:34s} {where:22s} {sid}  ({label})')
        if not verbose:
            block_dead = [d for d in dead if d[1] != 'section']
            if block_dead:
                print(f'  … and {len(block_dead)} block-level setting(s) (run with --verbose)')
    else:
        print('No dead settings: every declared setting is read somewhere in markup.')

    # settings_data / template values must not reference removed ids either
    return 1 if [d for d in dead if d[1] == 'section'] else 0


if __name__ == '__main__':
    sys.exit(main())
