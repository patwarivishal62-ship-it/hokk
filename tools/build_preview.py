#!/usr/bin/env python3
"""Build a static design preview of the theme at /home/user/preview.

Shopify Liquid cannot run outside a store, so this renders the parts of the
theme that are plain data/CSS and drops them into a hand-authored HTML page
that uses the REAL class names, REAL stylesheet files and REAL design tokens:

  * assets/base.css, assets/components.css, assets/theme.js  → copied verbatim
  * snippets/theme-tokens.liquid + snippets/color-schemes.liquid → evaluated
    against config/settings_data.json into preview/assets/tokens.css
  * snippets/icon.liquid, snippets/motif.liquid, snippets/clip-paths.liquid →
    the actual inline SVGs are lifted out and used in the page

The result is a faithful look at colours, type scale, spacing, cards, arches,
motifs, buttons and forms. It is NOT the theme (no Liquid, no real products)
and it lives outside the repo so it never lands in the uploaded zip.

Run:  python3 tools/build_preview.py
"""
import json
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path('/home/user/preview')

SETTINGS = json.loads((ROOT / 'config' / 'settings_data.json').read_text())['current']


def s(key, fallback=None):
    value = SETTINGS.get(key, fallback)
    return fallback if value is None else value


def rgb(hexcolor):
    h = str(hexcolor).lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return '%d, %d, %d' % tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# --------------------------------------------------------------------- tokens
def render_color_schemes():
    """snippets/color-schemes.liquid is pure CSS + {{ settings.x }} substitutions."""
    text = (ROOT / 'snippets' / 'color-schemes.liquid').read_text()
    text = re.sub(r'\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}', '', text, flags=re.S)

    def triple(m):
        return rgb(s(m.group(1), '#000000'))

    def single(m):
        value = s(m.group(1), '')
        return str(value)

    text = re.sub(r'\{\{\s*settings\.([a-z0-9_]+)\.red\s*\}\},\s*\{\{\s*settings\.\1\.green\s*\}\},\s*\{\{\s*settings\.\1\.blue\s*\}\}', triple, text)
    text = re.sub(r'\{\{\s*settings\.([a-z0-9_]+)\s*\}\}', single, text)
    text = re.sub(r'\{%-?.*?-?%\}', '', text)
    return text


def render_tokens():
    scale = (s('type_header_scale', 100) or 100) / 100.0
    body_scale = (s('type_body_scale', 100) or 100) / 100.0
    h1 = round((s('type_h1_size', 64) or 64) * scale)
    h2 = round((s('type_h2_size', 40) or 40) * scale)
    h3 = round((s('type_h3_size', 26) or 26) * scale)
    desktop = s('section_spacing', 96) or 96
    mobile = s('section_spacing_mobile', 56) or 56
    ratio = round(mobile / desktop, 4) if desktop else 0.58
    eyebrow_font = 'var(--font-heading)' if s('type_eyebrow_font') == 'heading' else 'var(--font-body)'
    button_font = 'var(--font-heading)' if s('button_font') == 'heading' else 'var(--font-body)'
    eyebrow_case = 'uppercase' if s('type_eyebrow_uppercase', True) else 'none'
    shadow = {
        'soft': '0 1px 2px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.05)',
        'medium': '0 2px 6px rgba(0,0,0,0.07), 0 16px 34px rgba(0,0,0,0.09)',
        'lift': '0 12px 28px rgba(0,0,0,0.13), 0 30px 60px rgba(0,0,0,0.10)',
    }.get(s('card_shadow'), 'none')
    shadow_hover = {
        'soft': '0 2px 6px rgba(0,0,0,0.06), 0 18px 40px rgba(0,0,0,0.10)',
        'medium': '0 4px 10px rgba(0,0,0,0.09), 0 26px 52px rgba(0,0,0,0.14)',
        'lift': '0 18px 38px rgba(0,0,0,0.18), 0 40px 80px rgba(0,0,0,0.14)',
    }.get(s('card_shadow'), 'none')
    btn_shadow = '0 6px 18px rgba(0,0,0,0.14)' if s('button_shadow') else 'none'

    return f"""
:root {{
  --color-sale: {s('color_sale')};
  --color-new: {s('color_new')};
  --color-soldout: {s('color_soldout')};
  --color-rating: {s('color_rating')};
  --color-gold: {s('color_gold')};
  --color-gold-rgb: {rgb(s('color_gold'))};

  --color-ink: {s('color_scheme_2_bg')};
  --color-ink-rgb: {rgb(s('color_scheme_2_bg'))};
  --color-ivory: {s('color_scheme_1_bg')};
  --color-ivory-rgb: {rgb(s('color_scheme_1_bg'))};
  --color-terracotta: {s('color_scheme_3_bg')};
  --color-terracotta-rgb: {rgb(s('color_scheme_3_bg'))};
  --color-indigo: {s('color_scheme_4_bg')};
  --color-marigold: {s('color_scheme_5_bg')};
  --color-leaf: {s('color_scheme_6_bg')};

  --page-width: {s('page_width')}px;
  --gutter: {s('page_gutter')}px;
  --section-space: {desktop}px;
  --section-space-mobile: {mobile}px;
  --section-space-mobile-ratio: {ratio};
  --grid-gap: {s('grid_gap')}px;
  --content-narrow: {s('content_width_narrow')}px;
  --box-padding: {s('box_padding')}px;

  --font-heading: 'Playfair Display', 'Iowan Old Style', 'Times New Roman', serif;
  --font-body: 'Assistant', 'Helvetica Neue', Arial, sans-serif;
  --font-heading-style: normal;
  --font-body-style: normal;
  --font-eyebrow: {eyebrow_font};
  --font-button: {button_font};
  --h1: {h1}px;
  --h2: {h2}px;
  --h3: {h3}px;
  --h4: calc(var(--h3) * 0.78);
  --heading-line-height: {s('type_header_line_height')};
  --heading-letter-spacing: {s('type_header_letter_spacing')}em;
  --heading-case: {s('type_header_case')};
  --body-size: {round(16 * body_scale)}px;
  --body-size-small: {round(14 * body_scale)}px;
  --body-line-height: {s('type_body_line_height')};
  --body-letter-spacing: {s('type_body_letter_spacing')}em;
  --eyebrow-size: {s('type_eyebrow_size')}px;
  --eyebrow-letter-spacing: {s('type_eyebrow_letter_spacing')}em;
  --eyebrow-case: {eyebrow_case};

  --btn-radius: {s('button_radius')}px;
  --btn-border: {s('button_border_width')}px;
  --btn-py: {s('button_padding_y')}px;
  --btn-px: {s('button_padding_x')}px;
  --btn-size: {s('button_size')}px;
  --btn-letter-spacing: {s('button_letter_spacing')}em;
  --btn-case: {s('button_case')};
  --input-radius: {s('input_radius')}px;
  --input-border: {s('input_border_width')}px;

  --card-radius: {s('card_radius')}px;
  --card-border: {s('card_border_width')}px;
  --image-radius: {s('image_radius')}px;
  --border-width: {s('border_width')}px;

  --icon-size: {s('icon_size')}px;
  --icon-weight: {s('icon_weight')};
  --anim-speed: {s('animations_speed')}ms;
  --ease: cubic-bezier(0.22, 0.61, 0.36, 1);
  --transition: all 0.35s var(--ease);

  --bg-card: var(--soft);
  --bg-secondary: var(--soft);
  --border-strong: rgba(var(--text-rgb), 0.24);
  --border-dashed: var(--border-width) dashed var(--border);
  --header-height: 0px;
  --min-col: 260px;
  --stack-gap: var(--grid-gap);

  --overlay-opacity: {(s('overlay_opacity', 30) or 30) / 100.0};
  --motif-size: {s('motif_size')}px;
  --texture-opacity: {(s('texture_opacity', 6) or 6) / 100.0};
  --card-shadow: {shadow};
  --card-shadow-hover: {shadow_hover};
  --btn-shadow: {btn_shadow};
}}
"""


# ------------------------------------------------------------------ svg assets
def extract_icons():
    text = (ROOT / 'snippets' / 'icon.liquid').read_text()
    stroke = s('icon_weight', 1.5)
    icons = {}
    for name, svg in re.findall(r"\{%-?\s*when '([a-z0-9\-]+)'\s*-?%\}\s*(<svg.*?</svg>)", text, re.S):
        icons[name] = svg.replace('{{ stroke }}', str(stroke))
    return icons


def extract_motif(style):
    text = (ROOT / 'snippets' / 'motif.liquid').read_text()
    branches = dict(re.findall(r"\{%-?\s*when '([a-z0-9\-]+)'\s*-?%\}\s*(<path.*?|<g.*?|<circle.*?)\s*\{%-?\s*when", text + "{%- when", re.S))
    inner = branches.get(style) or branches.get('lotus') or ''
    if not inner:
        m = re.search(r"\{%-?\s*else\s*-?%\}\s*(<path.*?)\{%-?\s*endcase", text, re.S)
        inner = m.group(1) if m else ''
    return (f'<span class="motif motif--{style}" aria-hidden="true" focusable="false">'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 76 76" width="100%" height="100%">{inner}</svg></span>')


def clip_paths():
    text = (ROOT / 'snippets' / 'clip-paths.liquid').read_text()
    return re.sub(r'\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}', '', text, flags=re.S).strip()


ICONS = extract_icons()
MOTIF_STYLE = s('motif_style', 'lotus')


def icon(name, size=None):
    svg = ICONS.get(name, '')
    size = size or s('icon_size', 22)
    return f'<span class="icon icon--{name}" style="--icon-size: {size}px" aria-hidden="true" focusable="false">{svg}</span>'


def motif():
    return extract_motif(MOTIF_STYLE)


TINTS = {
    'ivory': ('#F3E7D3', '#C9A227'),
    'terracotta': ('#D98A62', '#7E3A1E'),
    'indigo': ('#3B5A86', '#DCE6F5'),
    'marigold': ('#F0D9A0', '#A9761F'),
    'leaf': ('#4C7F6E', '#DCEBE3'),
    'ink': ('#33291F', '#C9A227'),
}


def ph(tone='ivory', pattern='arch', label=''):
    """A block-print flavoured placeholder standing in for a product photo."""
    bg, fg = TINTS.get(tone, TINTS['ivory'])
    if pattern == 'arch':
        art = (f'<path d="M40 250 V150 a60 60 0 0 1 120 0 V250 Z" fill="none" stroke="{fg}" stroke-width="2" opacity=".5"/>'
               f'<path d="M65 250 V160 a35 35 0 0 1 70 0 V250" fill="none" stroke="{fg}" stroke-width="1.4" opacity=".45"/>'
               f'<circle cx="100" cy="120" r="6" fill="{fg}" opacity=".5"/>')
    elif pattern == 'dots':
        art = ('<g fill="%s" opacity=".45">' % fg +
               ''.join(f'<circle cx="{20 + x * 20}" cy="{20 + y * 20}" r="3"/>' for x in range(9) for y in range(13)) + '</g>')
    elif pattern == 'stripes':
        art = ('<g stroke="%s" stroke-width="6" opacity=".3">' % fg +
               ''.join(f'<path d="M{-100 + i * 30} 300 L{100 + i * 30} 0"/>' for i in range(14)) + '</g>')
    else:  # 'blocks' — a stamped grid, the way a Bagru print is built
        art = ('<g fill="none" stroke="%s" stroke-width="1.6" opacity=".5">' % fg +
               ''.join(f'<rect x="{16 + x * 42}" y="{16 + y * 42}" width="26" height="26"/>'
                       f'<circle cx="{29 + x * 42}" cy="{29 + y * 42}" r="5"/>'
                       for x in range(4) for y in range(6)) + '</g>')
    return (f'<svg class="placeholder-svg" viewBox="0 0 200 300" preserveAspectRatio="xMidYMid slice" '
            f'role="img" aria-label="{label}"><rect width="200" height="300" fill="{bg}"/>{art}</svg>')


def stars(rating, count=None):
    out = []
    for i in range(1, 6):
        cls = '' if i <= rating else ' class="is-empty"'
        out.append(f'<span{cls}>{icon("star", 14)}</span>')
    label = f'{rating} out of 5 stars'
    count_html = f'<span class="rating__count">({count})</span>' if count else ''
    return (f'<div class="rating"><span class="rating__stars" role="img" aria-label="{label}">'
            f'{"".join(out)}</span>{count_html}</div>')


# ------------------------------------------------------------------- html bits
def product_card(title, price, compare=None, tone='ivory', pattern='arch', badge=None,
                 vendor=None, rating=5, swatches=(), style=None):
    style = style or s('product_card_style', 'standard')
    ratio = s('product_image_ratio', '4 / 5')
    badges = ''
    if badge == 'sale':
        badges = '<span class="badge">&minus;20%</span>'
    elif badge == 'new':
        badges = f'<span class="badge badge--new">{s("product_badge_new_text", "New")}</span>'
    elif badge == 'soldout':
        badges = f'<span class="badge badge--soldout">{s("product_badge_soldout_text", "Sold out")}</span>'
    elif badge:
        badges = f'<span class="badge badge--custom">{badge}</span>'
    vendor_html = f'<span class="product-card__vendor">{vendor}</span>' if vendor else ''
    price_html = f'<span class="price__current{" price__sale" if compare else ""}">{price}</span>'
    if compare:
        price_html += f'<s class="price__compare">{compare}</s><span class="price__badge">&minus;20%</span>'
    swatch_html = ''
    if swatches:
        dots = ''.join(
            f'<span class="product-card__swatch" style="background:{c}" title="{c}"></span>' for c in swatches)
        swatch_html = f'<div class="product-card__swatches">{dots}</div>'
    sold_out = badge == 'soldout'
    cta = ('<span class="btn btn--outline btn--small btn--full" aria-disabled="true">Sold out</span>'
           if sold_out else
           '<button type="button" class="btn btn--outline btn--small btn--full"><span data-btn-label>Add to cart</span></button>')
    return f"""
<article class="product-card card card--{style}" data-animate>
  <div class="product-card__media" style="--ratio: {ratio};">
    <div class="product-card__badges" data-badge-position="{s('product_badge_position', 'top left')}">{badges}</div>
    <a class="product-card__link" href="#" aria-label="{title}">
      <span class="product-card__image product-card__image--primary">{ph(tone, pattern, title)}</span>
    </a>
    <div class="product-card__quick-add">{cta}</div>
  </div>
  <div class="card__body">
    {vendor_html}
    <h3 class="card__title"><a href="#">{title}</a></h3>
    {stars(rating, 12 if rating else None)}
    <div class="price">{price_html}</div>
    {swatch_html}
  </div>
</article>"""


def collection_card(title, count, tone, pattern='blocks'):
    style = s('collection_card_style', 'arch') or 'arch'
    return f"""
<a class="collection-card card card--{style} collection-card--{style}" href="#">
  <span class="collection-card__media">{ph(tone, pattern, title)}</span>
  <span class="collection-card__body">
    <span class="collection-card__title h3">{title}</span>
    <span class="collection-card__count">{count} pieces</span>
    <span class="collection-card__cta link-arrow">Browse {icon('arrow-right', 14)}</span>
  </span>
</a>"""


def section_header(eyebrow, title, text=None, align='left', action=None, size='h2'):
    tag = size
    actions = ''
    if action:
        label, kind = action
        if kind == 'button':
            actions = f'<div class="section-header__actions"><a class="btn btn--outline btn--small" href="#">{label}</a></div>'
        else:
            actions = f'<div class="section-header__actions"><a class="link-arrow" href="#">{label} {icon("arrow-right", 14)}</a></div>'
    motif_row = f'<div class="motif-row section-header__motif">{motif()}</div>' if s('motif_enable', True) else ''
    text_html = f'<div class="section-header__text rte"><p>{text}</p></div>' if text else ''
    eyebrow_html = f'<p class="eyebrow{" eyebrow--center" if align == "center" else ""}">{eyebrow}</p>' if eyebrow else ''
    return f"""
<div class="section-header section-header--{align}" data-animate>
  <div class="section-header__copy">
    {eyebrow_html}
    <{tag} class="section-header__title">{title}</{tag}>
    {motif_row if align == 'center' else ''}
    {text_html}
  </div>
  {actions}
</div>"""


# ------------------------------------------------------------------ page build
def build_page():
    body_attrs = (
        f'class="template-index"'
        f' data-animations="{s("animations_style") if s("animations_enable") else "none"}"'
        f' data-stagger="{"true" if s("animations_stagger") else "false"}"'
        f' data-header-behavior="{s("header_behavior", "sticky")}"'
        f' data-cart-type="{s("cart_type", "drawer")}"'
        f' data-currency-code="false"'
        f' data-arch="{s("arch_shape") if s("arch_enable") else "off"}"'
        f' data-arch-cards="{"true" if s("arch_on_cards") else "false"}"'
        f' data-badge-shape="{s("product_badge_shape", "pill")}"'
        f' data-hover-zoom="{"true" if s("image_hover_zoom") else "false"}"'
        f' data-btn-hover="{s("button_hover", "invert")}"'
        f' data-card-hover="{"true" if s("card_shadow_on_hover") else "false"}"'
        f' data-align="{s("product_text_align", "left")}"'
        f' data-print-border="off"'
        f' data-full-bleed="false"'
        f' data-floating-labels="{"true" if s("input_floating_label") else "false"}"'
    )

    announcement = f"""
<div class="announcement color-scheme-2 announcement--bordered">
  <div class="announcement__inner container announcement__inner--rotating">
    <div class="announcement__stack">
      <div class="announcement__slide announcement__slide--static">
        <span class="announcement__icon">{icon('truck', 16)}</span>
        <span class="announcement__text">Complimentary shipping across India above &#8377;5,000 &middot; made to order in Jaipur</span>
      </div>
    </div>
  </div>
</div>"""

    header = f"""
<header class="header header--{s('header_layout', 'logo-center')} color-scheme-1 header--bordered">
  <div class="header__inner container">
    <div class="header__cell header__cell--left">
      <button type="button" class="header__icon header__menu-btn hide-desktop" data-panel-open="MenuDrawer" aria-label="Menu">{icon('menu', 22)}</button>
      <nav class="header__nav hide-mobile" aria-label="Primary">
        <ul class="nav" role="list">
          <li class="nav__item nav__item--children"><a class="nav__link" href="#">Textiles {icon('chevron-down', 14)}</a>
            <div class="nav__panel"><div class="nav__panel-inner container">
              <ul class="nav__columns" style="--nav-columns: 2;" role="list">
                <li class="nav__column"><a class="nav__column-title" href="#">Cotton</a>
                  <ul class="nav__sublist" role="list"><li><a class="nav__sublink" href="#">Block-printed</a></li><li><a class="nav__sublink" href="#">Indigo shibori</a></li></ul></li>
                <li class="nav__column"><a class="nav__sublink nav__sublink--single" href="#">Table linen</a></li>
              </ul>
            </div></div>
          </li>
          <li class="nav__item"><a class="nav__link" href="#">Brass</a></li>
          <li class="nav__item"><a class="nav__link" href="#">Pottery</a></li>
          <li class="nav__item nav__item--mega"><a class="nav__link" href="#">The house {icon('chevron-down', 14)}</a>
            <div class="nav__panel nav__panel--mega"><div class="nav__panel-inner container">
              <ul class="nav__columns" style="--nav-columns: 3;" role="list">
                <li class="nav__column"><a class="nav__column-title" href="#">Our story</a>
                  <ul class="nav__sublist" role="list"><li><a class="nav__sublink" href="#">Three generations</a></li><li><a class="nav__sublink" href="#">The makers</a></li></ul></li>
                <li class="nav__column"><a class="nav__column-title" href="#">Craft</a>
                  <ul class="nav__sublist" role="list"><li><a class="nav__sublink" href="#">Natural dyes</a></li><li><a class="nav__sublink" href="#">Repair for life</a></li></ul></li>
                <li class="nav__column"><a class="nav__column-title" href="#">Visit</a>
                  <ul class="nav__sublist" role="list"><li><a class="nav__sublink" href="#">The haveli</a></li><li><a class="nav__sublink" href="#">Workshop tours</a></li></ul></li>
              </ul>
            </div></div>
          </li>
          <li class="nav__item"><a class="nav__link" href="#">Journal</a></li>
        </ul>
      </nav>
    </div>
    <div class="header__cell header__cell--center">
      <a class="header__logo-link" href="#">
        <span class="header__logo-text">House of Kala Katha</span>
      </a>
    </div>
    <div class="header__cell header__cell--right">
      <a class="header__phone hide-mobile" href="tel:+911412200000">+91 141 220 0000</a>
      <button type="button" class="header__icon" aria-label="Search">{icon('search', 20)}</button>
      <a class="header__icon" href="#" aria-label="Account">{icon('user', 20)}</a>
      <button type="button" class="header__icon header__cart" data-panel-open="CartDrawer" aria-label="Cart">{icon('cart', 20)}<span class="cart-drawer__count" data-cart-count hidden>0</span></button>
    </div>
  </div>
</header>"""

    hero = f"""
<div class="hero section color-scheme-5 section--banner" style="--section-pad-top: 0px; --section-pad-bottom: 0px;">
  <div class="container">
    <div class="hero__grid" style="--hero-text: 46%;">
      <div class="hero__content" data-animate>
        <p class="eyebrow">House of Kala Katha &middot; est. 1974</p>
        <h1 class="hero__title">Objects that carry a story</h1>
        <div class="motif-row hero__motif">{motif()}</div>
        <div class="hero__text rte"><p>Block-printed textiles, cast brass and slow pottery from the families we have worked with for three generations. Printed once, never reprinted.</p></div>
        <div class="hero__actions">
          <a class="btn" href="#">Shop the house</a>
          <a class="btn btn--outline" href="#">Our story</a>
        </div>
        <p class="hero__meta">Natural dyes &middot; Maker named on every piece &middot; Repair for life</p>
      </div>
      <div class="hero__media" data-animate>
        <div class="media arch" style="aspect-ratio: 4 / 5;">{ph('terracotta', 'arch', 'Hero')}</div>
      </div>
    </div>
  </div>
</div>"""

    marquee_items = ['Handmade in Jaipur', 'Natural dyes only', 'Free shipping over &#8377;5,000', 'Maker named on every piece']
    marquee_icons = ['hand', 'leaf', 'truck', 'sparkle']
    group = ''.join(
        f'<span class="marquee__item">{icon(marquee_icons[i % 4], 16)}<span>{t}</span></span>'
        f'<span class="marquee__separator" aria-hidden="true"><span class="marquee__dot"></span></span>'
        for i, t in enumerate(marquee_items))
    marquee = f"""
<div class="marquee-section color-scheme-2 marquee--left marquee--flush" data-marquee style="--marquee-duration: 30s;">
  <span class="marquee__rule marquee__rule--top" aria-hidden="true"></span>
  <div class="marquee__viewport">
    <div class="marquee__track" data-marquee-track>
      <span class="marquee__group">{group}</span>
      <span class="marquee__group" aria-hidden="true">{group}</span>
    </div>
  </div>
  <span class="marquee__rule marquee__rule--bottom" aria-hidden="true"></span>
</div>"""

    collections = f"""
<div class="section collection-list-section color-scheme-1">
  <div class="container">
    {section_header('Browse by craft', 'Six rooms of the house', 'Textiles, brass, clay, wood, paper and the table — each room made by a different family of makers.', align='center', action=('All collections', 'link'))}
    <div class="grid" style="--cols: 3; --cols-tablet: 2; --cols-mobile: 1;">
      <div class="grid__item" data-animate>{collection_card('Block-printed textiles', 48, 'terracotta')}</div>
      <div class="grid__item" data-animate>{collection_card('Cast brass', 26, 'marigold', 'dots')}</div>
      <div class="grid__item" data-animate>{collection_card('Slow pottery', 31, 'leaf', 'stripes')}</div>
    </div>
  </div>
</div>"""

    products = f"""
<div class="section featured-collection color-scheme-1">
  <div class="container">
    {section_header('Featured', 'The block-print table', 'Printed lengths, napkins and runners from the Bagru workshop.', align='split', action=('View the whole collection', 'button'))}
    <div class="grid product-grid" style="--cols: 4; --cols-tablet: 3; --cols-mobile: 2;">
      <div class="grid__item" data-animate>{product_card('Bagru table runner', '&#8377;2,480', '&#8377;3,100', 'terracotta', 'blocks', badge='sale', vendor='Bagru workshop', rating=5, swatches=('#C2643C', '#243A5E', '#2F5D50'))}</div>
      <div class="grid__item" data-animate>{product_card('Indigo napkin set of four', '&#8377;1,950', tone='indigo', pattern='stripes', badge='new', vendor='Sanganer', rating=4)}</div>
      <div class="grid__item" data-animate>{product_card('Brass serving thali', '&#8377;4,200', tone='marigold', pattern='dots', vendor='Moradabad', rating=5)}</div>
      <div class="grid__item" data-animate>{product_card('Terracotta water jug', '&#8377;1,600', tone='leaf', pattern='arch', badge='soldout', vendor='Molela', rating=0)}</div>
    </div>
  </div>
</div>"""

    story = f"""
<div class="section image-with-text color-scheme-1">
  <div class="container">
    <div class="iwt__grid" style="--iwt-gap: 56px; --iwt-split: 52%;">
      <div class="iwt__media" data-animate>
        <div class="iwt__image media arch" style="aspect-ratio: 4 / 5;">{ph('ink', 'blocks', 'Workshop')}</div>
        <span class="iwt__badge">Est. 1974</span>
      </div>
      <div class="iwt__content" data-animate>
        <p class="eyebrow">The workshop</p>
        <h2 class="iwt__heading">Printed one pass, one colour at a time</h2>
        <div class="iwt__text rte"><p>A single Bagru print can need nine separate blocks and nine days of drying. We keep the count honest — you can read the registration marks on the reverse of every length.</p></div>
        <div class="iwt__stat"><span class="iwt__stat-value">40+</span><span class="iwt__stat-label">artisan families</span></div>
        <ul class="iwt__list" role="list">
          <li>{icon('check', 16)} Natural dyes, no azo pigments</li>
          <li>{icon('check', 16)} Fair rates paid weekly</li>
          <li>{icon('check', 16)} Maker&rsquo;s name stamped underneath</li>
        </ul>
        <div class="iwt__action"><a class="btn" href="#">Explore the craft</a><a class="btn btn--outline" href="#">Meet the makers</a></div>
      </div>
    </div>
  </div>
</div>"""

    usps = [('hand', 'Made by one pair of hands', 'Every order names its maker. No assembly lines.'),
            ('leaf', 'Natural dyes only', 'Indigo, madder, pomegranate and iron.'),
            ('truck', 'Ships in 48 hours', 'Free across India above &#8377;5,000.'),
            ('returns', '14-day returns', 'Send it back unwashed and we refund.')]
    usp_html = ''.join(f"""
      <div class="grid__item" data-animate>
        <div class="multicolumn__card multicolumn--box">
          <span class="multicolumn__icon">{icon(name, 22)}</span>
          <h3 class="multicolumn__title">{title}</h3>
          <div class="multicolumn__text rte"><p>{text}</p></div>
        </div>
      </div>""" for name, title, text in usps)
    multicolumn = f"""
<div class="section multicolumn multicolumn--box multicolumn--align-center color-scheme-1">
  <div class="container">
    {section_header('Why Kala Katha', 'Four promises we keep', align='center')}
    <div class="grid" style="--cols: 4; --cols-tablet: 2; --cols-mobile: 1;">{usp_html}</div>
  </div>
</div>"""

    testimonials_data = [('The indigo throw is heavier and softer than I expected. You can feel the hand in it.', 'Meera S.', 'Mumbai'),
                         ('It arrived wrapped in muslin with the maker&rsquo;s name on the tag. It felt like a gift.', 'Daniel R.', 'London'),
                         ('Three years of daily use and the brass has only grown warmer. Worth every rupee.', 'Ananya K.', 'Bengaluru')]
    t_cards = ''.join(f"""
      <div class="grid__item" data-animate>
        <figure class="testimonial-card">
          <span class="testimonial-card__mark" aria-hidden="true">{icon('quote', 26)}</span>
          <span class="rating-stars" role="img" aria-label="5 out of 5 stars">{''.join(f'<span class="rating-stars__star">{icon("star", 14)}</span>' for _ in range(5))}</span>
          <blockquote class="testimonial-card__quote"><p>{quote}</p></blockquote>
          <figcaption class="testimonial-card__meta">
            <span class="testimonial-card__who">
              <span class="testimonial-card__name">{name}</span>
              <span class="testimonial-card__role">{place}</span>
              <span class="testimonial-card__verified">{icon('check-circle', 13)} Verified buyer</span>
            </span>
          </figcaption>
        </figure>
      </div>""" for quote, name, place in testimonials_data)
    testimonials = f"""
<div class="section testimonials color-scheme-5">
  <div class="container">
    {section_header('Kind words', 'What our customers keep', align='center')}
    <div class="grid" style="--cols: 3; --cols-tablet: 2; --cols-mobile: 1;">{t_cards}</div>
  </div>
</div>"""

    quote = f"""
<div class="section quote-section color-scheme-1 quote-style--portrait quote-align--center">
  <div class="container">
    <div class="quote-section__inner">
      <div class="motif-row">{motif()}</div>
      <span class="quote-section__mark" aria-hidden="true">{icon('quote', 30)}</span>
      <blockquote class="quote-section__text"><p>We are not selling objects. We are asking you to keep a piece of someone&rsquo;s life&rsquo;s work in your home.</p></blockquote>
      <footer class="quote-section__byline">
        <span class="quote-section__meta"><span>Ananya Kala</span><span>Founder, House of Kala Katha</span></span>
      </footer>
    </div>
  </div>
</div>"""

    faq_items = [('How should I wash block-printed cotton?', 'Cold water, a mild soap, dry in shade for the first three washes. The dye settles after that.'),
                 ('Do you repair pieces?', 'Yes. Send anything back at any time and our makers will mend it — re-block a faded panel, re-solder a brass handle.'),
                 ('Can I order in bulk for a hotel?', 'We do. Write to us with your quantities and timelines and we will match you with a workshop.')]
    faq_html = ''.join(f"""
        <details class="faq__item" data-accordion{' open' if i == 0 else ''}>
          <summary class="faq__summary"><h3 class="faq__question">{q}</h3><span class="faq__icon" aria-hidden="true">{icon('plus', 18)}</span></summary>
          <div class="faq__body" data-accordion-body><div class="faq__answer rte"><p>{a}</p></div></div>
        </details>""" for i, (q, a) in enumerate(faq_items))
    faq = f"""
<div class="section faq color-scheme-1">
  <div class="container">
    {section_header('Good to know', 'Questions we are asked weekly', align='center')}
    <div class="faq__list">{faq_html}</div>
  </div>
</div>"""

    newsletter = f"""
<div class="section newsletter-section color-scheme-4 newsletter-section--plain newsletter-section--align-center">
  <div class="container">
    <div class="newsletter-section__inner">
      <p class="eyebrow eyebrow--center">The Kala Katha letter</p>
      <h2 class="newsletter-section__heading">Ten per cent off your first piece</h2>
      <div class="newsletter-section__text rte"><p>One letter a month: new releases, the makers behind them, and first access to small runs.</p></div>
      <form class="newsletter-form newsletter-form--inline" onsubmit="return false;">
        <div class="newsletter-form__row">
          <div class="field field--float newsletter-form__field">
            <input class="newsletter-form__input" type="email" id="preview-email" name="email" placeholder=" " autocomplete="email">
            <label class="field__label" for="preview-email">Your email address</label>
          </div>
          <button class="btn newsletter-form__button" type="submit"><span data-btn-label>Subscribe</span></button>
        </div>
      </form>
      <p class="newsletter-section__note">No spam. Unsubscribe in one click.</p>
    </div>
  </div>
</div>"""

    footer = f"""
<footer class="footer color-scheme-2 section" role="contentinfo">
  <div class="footer__motif motif-row">{motif()}</div>
  <div class="container">
    <div class="footer__grid" style="--footer-columns: 4;">
      <div class="footer__block footer__block--brand">
        <div class="footer__logo"><span class="header__logo-text">House of Kala Katha</span></div>
        <div class="footer__rte rte"><p>Handmade in Jaipur since 1974. Textiles, brass and clay from forty artisan families.</p></div>
        <a class="btn btn--outline btn--small footer__cta" href="#">Visit the workshop</a>
      </div>
      <div class="footer__block footer__block--menu">
        <h3 class="footer__heading">Shop</h3>
        <ul class="footer__list" role="list"><li><a href="#">Textiles</a></li><li><a href="#">Brass</a></li><li><a href="#">Pottery</a></li><li><a href="#">Gift cards</a></li></ul>
      </div>
      <div class="footer__block footer__block--menu">
        <h3 class="footer__heading">Help</h3>
        <ul class="footer__list" role="list"><li><a href="#">Shipping</a></li><li><a href="#">Returns</a></li><li><a href="#">Care guide</a></li><li><a href="#">Contact</a></li></ul>
      </div>
      <div class="footer__block footer__block--contact">
        <h3 class="footer__heading">The house</h3>
        <div class="footer__rte rte"><p>14 Kala Katha Haveli, Amer Road<br>Jaipur 302002, Rajasthan</p><p><a href="tel:+911412200000">+91 141 220 0000</a><br><a href="mailto:hello@houseofkalakatha.com">hello@houseofkalakatha.com</a></p></div>
      </div>
    </div>
    <div class="footer__bottom">
      <p class="footer__copy">&copy; 2026 House of Kala Katha. All rights reserved.</p>
      <ul class="social-links" role="list">
        <li><a href="#" aria-label="Instagram">{icon('instagram', 18)}</a></li>
        <li><a href="#" aria-label="Facebook">{icon('facebook', 18)}</a></li>
        <li><a href="#" aria-label="Pinterest">{icon('pinterest', 18)}</a></li>
        <li><a href="#" aria-label="WhatsApp">{icon('whatsapp', 18)}</a></li>
      </ul>
    </div>
  </div>
</footer>"""

    slide_products = [('Kantha quilt', '&#8377;8,400', 'terracotta', 'blocks', None),
                      ('Brass diya set', '&#8377;2,150', 'marigold', 'dots', 'new'),
                      ('Indigo throw', '&#8377;5,600', 'indigo', 'stripes', None),
                      ('Molela horse', '&#8377;3,300', 'leaf', 'arch', None),
                      ('Wooden comb', '&#8377;480', 'ivory', 'blocks', 'sale'),
                      ('Chanderi scarf', '&#8377;2,950', 'ink', 'stripes', None)]
    slides = ''.join(f'''
        <div class="grid__item slider__slide" data-slide style="flex-basis: calc((100% - (var(--gutter) * (var(--cols) - 1))) / var(--cols));">
          {product_card(title, price, tone=tone, pattern=pattern, badge=badge, rating=5 if badge != 'sale' else 4)}
        </div>''' for title, price, tone, pattern, badge in slide_products)
    carousel = f"""
<div class="section featured-collection color-scheme-1">
  <div class="container">
    {section_header('Keep looking', 'More from the house', 'A carousel — drag it, or use the arrows. The same slider module powers product galleries and logo walls.', align='split')}
    <div class="slider featured-collection__slider" data-slider data-per-view="4">
      <div class="slider__viewport grid product-grid" style="--cols: 4; --cols-tablet: 3; --cols-mobile: 2; --gutter: 24px;">{slides}
      </div>
      <div class="slider__controls">
        <button type="button" class="slider__arrow slider__arrow--prev" data-slider-prev aria-label="Previous">{icon('chevron-left', 20)}</button>
        <div class="slider__dots" data-slider-dots></div>
        <button type="button" class="slider__arrow slider__arrow--next" data-slider-next aria-label="Next">{icon('chevron-right', 20)}</button>
      </div>
    </div>
  </div>
</div>"""

    components = f"""
<div class="section color-scheme-1" style="--section-pad-top: 40px;">
  <div class="container">
    {section_header('Design system', 'Components, straight from the theme CSS', 'Every element below is styled by assets/base.css and assets/components.css — the same files the theme ships.', align='left', size='h2')}

    <div class="grid" style="--cols: 2; --cols-tablet: 1; --cols-mobile: 1;">
      <div class="grid__item">
        <div class="box">
          <h3 class="h4">Buttons</h3>
          <div class="preview-row">
            <a class="btn" href="#">Solid</a>
            <a class="btn btn--outline" href="#">Outline</a>
            <a class="btn btn--ghost" href="#">Ghost</a>
            <a class="btn btn--small" href="#">Small</a>
            <a class="btn btn--full" href="#">Full width</a>
          </div>
          <h3 class="h4">Badges &amp; chips</h3>
          <div class="preview-row">
            <span class="badge">Sale</span>
            <span class="badge badge--new">New</span>
            <span class="badge badge--soldout">Sold out</span>
            <span class="badge badge--sale">&minus;20%</span>
            <a class="chip" href="#">Indigo</a>
            <a class="chip" href="#">Brass</a>
          </div>
          <h3 class="h4">Price</h3>
          <div class="preview-row">
            <div class="price"><span class="price__current">&#8377;2,480</span></div>
            <div class="price price--sale"><span class="price__current price__sale">&#8377;2,480</span><s class="price__compare">&#8377;3,100</s><span class="price__badge">&minus;20%</span></div>
            <div class="price price--large"><span class="price__current">&#8377;12,900</span><span class="price__unit">&#8377;645 / 100 g</span></div>
          </div>
        </div>
      </div>
      <div class="grid__item">
        <div class="box">
          <h3 class="h4">Form fields {('(floating labels on)' if s('input_floating_label') else '(labels above)')}</h3>
          <div class="field field--float"><input type="text" id="c-name" placeholder=" " value="Meera Sharma"><label class="field__label" for="c-name">Name</label></div>
          <div class="field field--float"><input type="email" id="c-email" placeholder=" "><label class="field__label" for="c-email">Email</label></div>
          <div class="select-wrap"><select aria-label="Topic"><option>Order enquiry</option><option>Wholesale</option><option>Repair</option></select></div>
          <div class="field field--float"><textarea id="c-msg" placeholder=" " rows="3"></textarea><label class="field__label" for="c-msg">Message</label></div>
          <label class="checkbox"><input type="checkbox" checked><span>Send me the Kala Katha letter</span></label>
          <h3 class="h4">Quantity + pagination</h3>
          <div class="preview-row">
            <div class="quantity"><button type="button" class="quantity__btn">&minus;</button><input class="quantity__input" type="number" value="2"><button type="button" class="quantity__btn">+</button></div>
            <nav class="pagination"><a class="pagination__item is-current" href="#">1</a><a class="pagination__item" href="#">2</a><a class="pagination__item" href="#">3</a><a class="pagination__item pagination__next" href="#">Next {icon('arrow-right', 14)}</a></nav>
          </div>
          <h3 class="h4">Motifs &amp; arches</h3>
          <div class="preview-row">
            <span class="motif-row">{motif()}</span>
            <span class="media arch" style="width: 84px; aspect-ratio: 3 / 4;">{ph('indigo', 'dots', 'arch')}</span>
            <span class="media media--rounded" style="width: 84px; aspect-ratio: 3 / 4;">{ph('leaf', 'stripes', 'rounded')}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>"""

    kk_shim = """
  window.KK = {
    moneyFormat: '\\u20B9{{amount}}',
    moneyWithCurrencyFormat: '\\u20B9{{amount}} INR',
    locale: 'en', currency: 'INR', cartType: 'drawer',
    freeShippingThreshold: 5000, lightbox: true,
    searchCollections: true, searchPages: true, predictiveLimit: 5,
    routes: { cart: '#', search: '#', root: '#', account: '#', collections: '#' },
    strings: { addToCart: 'Add to cart', soldOut: 'Sold out', unavailable: 'Unavailable',
      inStock: 'In stock', lowStock: 'Only a few left', backorder: 'Backordered',
      cartError: 'This item could not be added to your cart.',
      freeShippingMet: 'You have free shipping', freeShippingRemaining: 'Free shipping above \\u20B95,000',
      remove: 'Remove', quantity: 'Quantity', increase: 'Increase', decrease: 'Decrease',
      noResults: 'No results', viewAll: 'View all', products: 'Products',
      collections: 'Collections', pages: 'Pages', suggestions: 'Suggestions', copied: 'Copied' }
  };"""

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kala Katha — design preview</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Assistant:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/tokens.css">
<link rel="stylesheet" href="assets/base.css">
<link rel="stylesheet" href="assets/components.css">
<link rel="stylesheet" href="assets/sections.css">
<style>
  /* preview-only chrome: the banner and the small helpers used on this page */
  .preview-banner {{ position: sticky; top: 0; z-index: 200; background: #1E1712; color: #F5EFE4;
    font: 500 12px/1.4 'Assistant', sans-serif; letter-spacing: .08em; text-transform: uppercase;
    padding: .6rem 1rem; display: flex; gap: 1rem; align-items: center; justify-content: center; flex-wrap: wrap; }}
  .preview-banner a {{ color: #E0A33E; }}
  .preview-row {{ display: flex; flex-wrap: wrap; gap: .7rem; align-items: center; margin: .6rem 0 1.4rem; }}
  .box {{ border: var(--border-width) solid var(--border); border-radius: var(--card-radius); padding: clamp(1rem, 3vw, 1.6rem); background: var(--bg-card); }}
  .box .h4 {{ margin-bottom: .2rem; }}
  .header__logo-text {{ font-family: var(--font-heading); font-size: 1.35rem; letter-spacing: .04em; }}
</style>
</head>
<body {body_attrs}>
{clip_paths()}
<div class="preview-banner">
  <span>Design preview — static mock, not the Shopify theme</span>
  <span>Colours, type and spacing come from config/settings_data.json</span>
  <span>CSS/JS are the real theme files</span>
</div>
{announcement}
{header}
<main id="MainContent" class="main-content" role="main" tabindex="-1">
{hero}
{marquee}
{collections}
{products}
{story}
{multicolumn}
{testimonials}
{quote}
{faq}
{carousel}
{newsletter}
{components}
</main>
<div class="drawer drawer--left mobile-menu color-scheme-1" id="MenuDrawer" role="dialog" aria-modal="true" aria-label="Menu" aria-hidden="true" tabindex="-1">
  <div class="drawer__header">
    <span class="drawer__title">Menu</span>
    <button type="button" class="drawer__close" data-panel-close aria-label="Close">{icon('close', 20)}</button>
  </div>
  <div class="drawer__body">
    <ul class="mobile-menu__list" role="list">
      <li><a class="mobile-menu__link" href="#">Textiles</a></li>
      <li><a class="mobile-menu__link" href="#">Brass</a></li>
      <li><a class="mobile-menu__link" href="#">Pottery</a></li>
      <li><a class="mobile-menu__link" href="#">Journal</a></li>
    </ul>
    <div class="mobile-menu__divider"></div>
    <div class="mobile-menu__search">{icon('search', 18)} <span>Search the house</span></div>
  </div>
</div>
<div class="drawer drawer--overlay" data-panel-overlay hidden></div>

<div class="drawer cart-drawer color-scheme-1" id="CartDrawer" role="dialog" aria-modal="true" aria-label="Cart" aria-hidden="true" tabindex="-1">
  <div class="drawer__header">
    <span class="drawer__title">Your cart <span class="cart-drawer__count" data-cart-count-text>(0)</span></span>
    <button type="button" class="drawer__close" data-panel-close aria-label="Close">{icon('close', 20)}</button>
  </div>
  <div class="drawer__body">
    <div class="ship-bar" data-shipping-bar>
      <p class="ship-bar__text" data-shipping-text>Free shipping above &#8377;5,000</p>
      <div class="ship-bar__track"><span class="ship-bar__fill" data-shipping-fill style="width: 0%"></span></div>
    </div>
    <div class="cart-drawer__items" data-cart-items></div>
    <div class="cart-drawer__empty-template" data-cart-empty hidden>
      <div class="cart-drawer__empty">
        <span class="cart-drawer__empty-icon">{icon('bag', 30)}</span>
        <p class="h3">Your cart is empty</p>
        <div class="rte text-muted"><p>Start with the block-print table — it is where most people begin.</p></div>
        <button type="button" class="btn btn--outline" data-panel-close>Continue browsing</button>
      </div>
    </div>
    <p class="cart-drawer__errors form-message form-message--error" data-cart-errors hidden></p>
  </div>
  <div class="drawer__footer">
    <div class="cart-drawer__totals">
      <span class="cart-drawer__totals-label">Subtotal</span>
      <span class="cart-drawer__totals-value" data-cart-subtotal>&#8377;0</span>
    </div>
    <p class="cart-drawer__savings" hidden>You save <strong data-cart-total-savings></strong></p>
    <button type="button" class="btn btn--full cart-drawer__checkout" data-cart-checkout="button">Checkout</button>
    <a class="cart-drawer__view-cart" href="#">View cart</a>
  </div>
</div>
{footer}
<script>{kk_shim}</script>
<script src="assets/theme.js" defer></script>
<script src="assets/sections.js" defer></script>
</body>
</html>
"""


def collect_section_css():
    """Shopify gathers every section's {% stylesheet %} block once per page.
    The preview has to do the same, or most sections would render unstyled."""
    out = []
    for path in sorted((ROOT / 'sections').glob('*.liquid')):
        text = path.read_text()
        blocks = re.findall(r'\{%-?\s*stylesheet\s*-?%\}(.*?)\{%-?\s*endstylesheet\s*-?%\}', text, re.S)
        if blocks:
            out.append('/* ---- %s ---- */' % path.name)
            out.extend(b.strip() for b in blocks)
    return '\n\n'.join(out) + '\n'


def collect_section_js():
    """Same story for {% javascript %} — collected once per page by Shopify."""
    out = []
    for path in sorted((ROOT / 'sections').glob('*.liquid')):
        text = path.read_text()
        blocks = re.findall(r'\{%-?\s*javascript\s*-?%\}(.*?)\{%-?\s*endjavascript\s*-?%\}', text, re.S)
        for b in blocks:
            if re.search(r'\{\{|\{%', b):
                continue  # cannot evaluate Liquid here; skip rather than emit junk
            out.append('/* ---- %s ---- */' % path.name)
            out.append(b.strip())
    return '\n\n'.join(out) + '\n'


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / 'assets').mkdir(parents=True)

    for name in ('base.css', 'components.css', 'theme.js'):
        shutil.copy2(ROOT / 'assets' / name, OUT / 'assets' / name)

    (OUT / 'assets' / 'sections.css').write_text(collect_section_css())
    (OUT / 'assets' / 'sections.js').write_text(collect_section_js())

    tokens = ('/* Generated by tools/build_preview.py from snippets/theme-tokens.liquid\n'
              '   + snippets/color-schemes.liquid + config/settings_data.json. */\n'
              + render_tokens() + '\n' + render_color_schemes() + '\n')
    (OUT / 'assets' / 'tokens.css').write_text(tokens)
    (OUT / 'index.html').write_text(build_page())

    print('preview written to', OUT)
    print('  index.html      %.1f KB' % ((OUT / 'index.html').stat().st_size / 1024))
    print('  assets/tokens.css %.1f KB' % ((OUT / 'assets' / 'tokens.css').stat().st_size / 1024))
    print('  assets/sections.css %.1f KB' % ((OUT / 'assets' / 'sections.css').stat().st_size / 1024))
    print('  assets/sections.js %.1f KB' % ((OUT / 'assets' / 'sections.js').stat().st_size / 1024))
    print('  icons lifted from the theme:', len(ICONS))


if __name__ == '__main__':
    main()
