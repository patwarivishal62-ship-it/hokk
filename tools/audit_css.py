#!/usr/bin/env python3
"""Static CSS audit for the theme.

Two checks, both deliberately conservative (they report, they do not fail the
build unless --strict):

  1. CLASSES   every static class token used in Liquid markup should appear in
               at least one selector in assets/*.css, a section {% stylesheet %}
               block, or an inline {% style %} block.
  2. VARIABLES every `var(--x)` should be defined somewhere: a CSS rule, a
               `style="--x: …"` attribute, or JavaScript (the known JS-owned
               variables are listed in JS_VARS).

Run:  python3 tools/audit_css.py [--strict]
"""
import pathlib
import re
import sys
import collections

ROOT = pathlib.Path(__file__).resolve().parent.parent

STRIP_RE = re.compile(
    r'\{%-?\s*schema\s*-?%\}.*?\{%-?\s*endschema\s*-?%\}'
    r'|\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}'
    r'|\{%-?\s*stylesheet\s*-?%\}.*?\{%-?\s*endstylesheet\s*-?%\}'
    r'|\{%-?\s*javascript\s*-?%\}.*?\{%-?\s*endjavascript\s*-?%\}',
    re.S,
)
STYLE_BLOCK_RE = re.compile(r'\{%-?\s*(?:stylesheet|style)\s*-?%\}(.*?)\{%-?\s*end(?:stylesheet|style)\s*-?%\}', re.S)
# raw <style> elements inside .liquid files (layout/theme.liquid, theme-tokens,
# templates/gift_card.liquid …) hold real CSS too
RAW_STYLE_RE = re.compile(r'<style[^>]*>(.*?)</style>', re.S)
CLASS_ATTR_RE = re.compile(r'class="([^"]*)"')
SELECTOR_RE = re.compile(r'([^{}]+)\{')
CLASS_TOKEN_RE = re.compile(r'\.(-?[_a-zA-Z][\w-]*)')
VAR_USE_RE = re.compile(r'var\(\s*(--[\w-]+)')
VAR_DEF_RE = re.compile(r'(--[\w-]+)\s*:')
STYLE_ATTR_RE = re.compile(r'style="([^"]*)"')

# variables that are set from JavaScript or from a data attribute at runtime
JS_VARS = {'--logo-shift', '--marquee-shift', '--zx', '--zy'}

# classes that are only hooks: state classes toggled by JS, layout hooks that
# are styled through a parent selector, or classes Shopify itself generates
HOOKS = {
    # runtime state, toggled by assets/theme.js or by Shopify itself
    'js', 'no-js', 'is-active', 'is-open', 'is-stuck', 'is-hidden', 'is-loading',
    'is-unavailable', 'is-selected', 'is-in', 'is-modal-overlay', 'is-pinned',
    'color-scheme-1', 'color-scheme-2', 'color-scheme-3', 'color-scheme-4',
    'color-scheme-5', 'color-scheme-6', 'template-index', 'no-print',
    # semantic roots kept for merchant/app custom CSS; visuals come from the
    # `.section`, `.card`, `.drawer` or `.header__icon` rules they also carry
    'blog-posts', 'blog-section', 'cart-drawer', 'cart-section', 'collage',
    'collection-banner', 'collection-main', 'collection-section', 'contact-form-section',
    'custom-liquid', 'customer-section', 'faq', 'gallery', 'image-with-text',
    'list-collections', 'logo-list', 'mobile-menu', 'multicolumn', 'page-section',
    'product-recommendations', 'recommendations-section', 'search-section',
    'store-info', 'testimonials', 'timeline', 'video-section', 'product-block',
    # grid/layout children that are positioned by their styled parent
    'blog-grid', 'collections-grid', 'product-grid', 'search-grid', 'faq__column',
    'faq__head', 'contact-form__panel', 'header__cart', 'header__menu-btn',
    'nav__item--children', 'nav__item--mega', 'slideshow__counter-current',
    'price--sale',  # sale colour is applied by .price__sale on the amount itself
}


def css_sources():
    """All CSS text in the theme: asset files + liquid style blocks."""
    out = []
    for path in sorted((ROOT / 'assets').glob('*.css')):
        out.append((path.relative_to(ROOT).as_posix(), path.read_text()))
    for path in sorted(list(ROOT.rglob('*.liquid'))):
        if '.git' in path.parts:
            continue
        text = path.read_text()
        blocks = STYLE_BLOCK_RE.findall(text) + RAW_STYLE_RE.findall(text)
        # snippets that are pure CSS (no markup at all) — e.g. color-schemes.liquid,
        # which is rendered inside a <style> tag by theme-tokens.liquid
        if not blocks and '<' not in STRIP_RE.sub(' ', text):
            blocks = [text]
        for block in blocks:
            out.append((path.relative_to(ROOT).as_posix(), block))
    return out


def main():
    strict = '--strict' in sys.argv

    selectors, defined_vars = set(), set()
    for name, css in css_sources():
        for chunk in SELECTOR_RE.findall(css):
            selectors.update(CLASS_TOKEN_RE.findall(chunk))
        defined_vars.update(VAR_DEF_RE.findall(css))

    used_classes = collections.Counter()
    used_vars = collections.Counter()
    inline_vars = set()
    js_vars = set(JS_VARS)

    for path in sorted(list(ROOT.rglob('*.liquid'))):
        if '.git' in path.parts:
            continue
        markup = STRIP_RE.sub(' ', path.read_text())
        for attr in CLASS_ATTR_RE.findall(markup):
            if '{{' in attr or '{%' in attr:
                # keep the literal parts, drop liquid-generated modifiers
                attr = re.sub(r'\{\{.*?\}\}|\{%.*?%\}', ' ', attr)
            for token in attr.split():
                # a trailing dash means the token was completed by Liquid that we
                # just stripped out (`banner--{{ style }}`) — not a real class
                if token.endswith('-'):
                    continue
                if re.fullmatch(r'-?[_a-zA-Z][\w-]*', token):
                    used_classes[token] += 1
        for attr in STYLE_ATTR_RE.findall(markup):
            inline_vars.update(VAR_DEF_RE.findall(attr))
        for var in VAR_USE_RE.findall(markup):
            used_vars[var] += 1

    js_text = ''
    for path in sorted((ROOT / 'assets').glob('*.js')):
        js_text += path.read_text()
    js_vars.update(re.findall(r"setProperty\(\s*'(--[\w-]+)'", js_text))
    js_vars.update(re.findall(r'"(--[\w-]+)"\s*:', js_text))
    defined_vars.update(inline_vars)

    missing_classes = sorted(c for c in used_classes if c not in selectors and c not in HOOKS)
    undefined_vars = sorted(v for v in used_vars if v not in defined_vars and v not in js_vars)

    print(f'css sources          : {len(css_sources())}')
    print(f'selector classes     : {len(selectors)}')
    print(f'classes used in liquid: {len(used_classes)}')
    print(f'custom props defined : {len(defined_vars)}   used: {len(used_vars)}')
    print()

    if missing_classes:
        print(f'CLASSES WITH NO SELECTOR ({len(missing_classes)}):')
        for c in missing_classes:
            print(f'  - .{c}  (used {used_classes[c]}x)')
    else:
        print('Every class used in markup has a matching selector.')

    print()
    if undefined_vars:
        print(f'UNDEFINED CUSTOM PROPERTIES ({len(undefined_vars)}):')
        for v in undefined_vars:
            print(f'  - {v}  (used {used_vars[v]}x)')
    else:
        print('Every var() resolves to a defined custom property (or a JS-owned one).')

    if strict and (missing_classes or undefined_vars):
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
