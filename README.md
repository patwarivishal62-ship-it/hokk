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

`templates/page.culture.json` + `sections/cultural-regions.liquid` — an editorial
culture page: intro (breadcrumb, eyebrow, H1, copy) followed by regional
"chapters". Each region is a **block** (type `region`), so merchants reorder by
dragging, hide with the eye icon, and add new ones (regions, states, weaving
traditions, weaver stories) without code. Chapter numbers follow visible block
order automatically. Per region: image + optional mobile image, eyebrow, title,
richtext description, signature weaves (comma list, optionally linked to store
search), CTA label + URL, image side (left/right), text alignment, background
color and vertical spacing. Section-level: intro fields, image ratio, image
width %, container width, chapter numbering, and the standard background /
typography group. Setup: create a page titled *Culture* in Shopify admin,
assign the **culture** template, then add it to your main menu.


### Shopify norms this theme follows
- JSON templates list **content sections only**; header/footer render via `{% sections 'header-group' %}` / `{% sections 'footer-group' %}`.
- Cart drawer updates through the **Section Rendering API** (`?sections=cart-drawer`).
- Native storefront **filters** + **sort** (`collection.filters`, `sort_by`).
- Fonts loaded with `font_face` from Shopify's library; colors driven by CSS custom properties in `settings_schema.json`.
- Accessibility: skip link, aria labels, `prefers-reduced-motion`, semantic landmarks.
