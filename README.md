# House of Kala Katha — Shopify Theme

An editorial, craft-first **Shopify Online Store 2.0 theme** for *House of Kala Katha* — Indian handloom, ikat, kalamkari & patola, re-cut for everyday life.

> “Kala is the art. Katha is the story.”

---

## What's in this repo

| Path | What it is |
| --- | --- |
| `shopify-hokk/` | **The Shopify theme** (this is the deployable artifact) |
| `preview/` | A static HTML preview of the design (no Shopify needed) — currently served as a live preview |
| `README.md` | This file |

The theme is built entirely on **OS 2.0 conventions** — JSON templates, section groups, the Section Rendering API, native storefront filtering, and Shopify's font library.

---

## Design system

Inspired by the reference landing page — a warm, editorial, heritage-craft aesthetic.

- **Palette** — cream `#F3ECE1` · espresso `#211912` · terracotta `#A94A33` · brass `#B98A4E` · muted taupe `#7A6A58`
- **Type** — *Fraunces* (display/serif) + *Inter* (body), both from Shopify's font library
- **Voice** — eyebrow kickers (`KALA · CRAFT — KATHA · STORY`), big serif headlines, generous whitespace, a running craft ticker, dark "story" sections
- **Editorial sections** — hero, marquee, philosophy, categories, seasonal story, lookbook, testimonials, featured collection, newsletter

Everything is theme-editor configurable (colors, fonts, page width, buttons, logo, menus, social links, cart type).

---

## Live preview

The `preview/` folder is served on **port 8080** (see the live preview panel). Pages:

- `/` — homepage (hero → marquee → philosophy → categories → story → lookbook → testimonials → featured products → newsletter)
- `/product.html` — product page (gallery, variant pills, quantity, accordions)
- `/collection.html` — collection page (banner, native filters, sort, product grid, pagination)

> Placeholder photography is AI-generated and bundled so the theme looks complete on install; replace with your own shoot via the theme editor.

---

## Installing on Shopify

### Option A — ZIP upload (fastest)
1. Zip the **contents** of `shopify-hokk/` (not the folder itself):
   ```bash
   cd shopify-hokk && zip -r ../hokk-theme.zip . && cd ..
   ```
2. Shopify Admin → **Online Store → Themes → Add theme → Upload zip file**.

### Option B — Shopify CLI
```bash
shopify theme dev --path shopify-hokk        # live dev server
shopify theme push --path shopify-hokk       # push to a store
```

### Option C — GitHub integration
Push this repo and connect it under **Online Store → Themes → Add theme → Connect from GitHub**.

---

## After installing — set up the essentials

1. **Menus** — create/assign these link lists:
   - `main-menu` (header nav)
   - footer menu columns: `footer`, `main-menu` (or any two menus you create — set them in **Footer → blocks**)
2. **Homepage sections** (`templates/index.json`) — upload real images into **Hero, Philosophy, Categories, Story, Lookbook, Newsletter** (they fall back to bundled imagery until you do).
3. **Featured collection** section — pick the collection to feature.
4. **Collections** — add native filters (size, colour, price, availability) in **Products → Collections → … → Search & discovery**; the grid auto-renders them.
5. **Theme settings** — brand colors, fonts, logo, social links, cart type (drawer/page).

---

## Theme structure

```
shopify-hokk/
├── layout/            theme.liquid (fonts, CSS vars, meta, cart drawer, groups)
├── config/            settings_schema.json · settings_data.json
├── locales/           en.default.json
├── sections/
│   ├── header-group.json · footer-group.json   ← section groups
│   ├── header · footer · announcement-bar      ← group members
│   ├── hero · marquee · philosophy · categories · story · lookbook · testimonials
│   ├── featured-collection · newsletter · contact-form · rich-text
│   └── main-*         ← required product/collection/cart/search/page/blog/account sections
├── snippets/          icon, price, card-product, variant-picker, quantity-input,
│                      cart-drawer, pagination, predictive-search, meta-tags, address-fields
├── templates/         index · product · collection · cart · search · page* · blog · article
│   └── customers/     account · order · addresses · login · register · activate · reset
├── assets/            theme.css · theme.js · starter imagery
```

### Culture page (`/pages/culture`)

`templates/page.culture.json` + `sections/culture-banners.liquid` — the Culture
page as a stack of **full-width clickable banner images** (the region text is
designed into the banners themselves). Each banner is a block: image, optional
mobile image, link URL (any page/collection/product/blog/external) and an
accessible label. Banners are never cropped — the complete image always shows.
Section settings: optional visible page title (a hidden H1 keeps SEO intact
either way), space between banners, top/bottom padding. Setup: create a page
titled *Culture* in Shopify admin, assign the **culture** template, then add it
to your main menu. (An earlier editorial "cultural regions" section exists in
git history if ever needed again.)

### Region pages (all five regions)

`templates/page.{north-india, north-east-india, south-india, east-india,
west-central-india}.json` + `sections/culture-hero.liquid` +
`sections/culture-archive.liquid` — deep editorial region chapters. Each page:
hero (breadcrumb/eyebrow/H1/supporting line/intro) + two Region archive
instances carrying the full content: landscape essay, in-flow images, 5 map
cards, 5 tradition chapters, technique rows, materials, motifs, colour
palettes with swatches, artisan essay, then-and-now comparison, authenticity
guide, future section, closing with cross-region links. Content companions:
`culture-content/*.md` (fact-verified, GI appendix each). The archive's 9
block types: image, India map (visual map of India with the region's states
gold-highlighted and numbered pins per craft, from each map card's “Pin
state”), heading+text, map card, tradition chapter, technique row, comparison
row, study item, link. The hero
section carries breadcrumb/eyebrow/H1/supporting line/intro; the archive
section builds the entire body from blocks: heading+text (H2 sections),
map cards (auto-group into a grid), tradition chapters (image, tags, body,
characteristic, CTA), technique rows, comparison rows (auto-group into one
table under the first row's column titles), study items (optional colour
swatch) and links. North India ships with all content preloaded across two
archive instances (Shopify caps blocks at 50 per section). Content source of
truth: `culture-content/` (one doc per region).


### Shopify norms this theme follows
- JSON templates list **content sections only**; header/footer render via `{% sections 'header-group' %}` / `{% sections 'footer-group' %}`.
- Cart drawer updates through the **Section Rendering API** (`?sections=cart-drawer`).
- Native storefront **filters** + **sort** (`collection.filters`, `sort_by`).
- Fonts loaded with `font_face` from Shopify's library; colors driven by CSS custom properties in `settings_schema.json`.
- Accessibility: skip link, aria labels, `prefers-reduced-motion`, semantic landmarks.
