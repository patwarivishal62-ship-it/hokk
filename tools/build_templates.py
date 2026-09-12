#!/usr/bin/env python3
"""Generate every templates/*.json for the Kala Katha theme.

Run from the repository root:  python3 tools/build_templates.py
The files it writes are the ones that ship inside the theme zip.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / 'templates'


def write(rel_path, sections, order=None):
    """Write one template JSON file."""
    path = TEMPLATES / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {'sections': sections, 'order': order or list(sections.keys())}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n')
    print('wrote', path.relative_to(ROOT))


def blocks(*items):
    """Turn (id, type, settings) tuples into a schema-shaped blocks dict."""
    out = {}
    for item in items:
        bid, btype = item[0], item[1]
        settings = item[2] if len(item) > 2 else {}
        out[bid] = {'type': btype, 'settings': settings}
    return out


# ----------------------------------------------------------------- homepage
homepage = {
    'slideshow': {
        'type': 'slideshow',
        'settings': {
            'height': 'large',
            'color_scheme': '2',
            'content_position': 'center-left',
            'text_alignment': 'left',
            'overlay_opacity': 45,
            'autoplay': True,
            'autoplay_speed': 6,
            'loop': True,
            'navigation': 'both',
            'show_progress': True,
        },
        'blocks': blocks(
            ('slide_1', 'slide', {
                'eyebrow': 'House of Kala Katha',
                'heading': 'Objects that carry a story',
                'subheading': 'handmade in Jaipur since 1974',
                'text': '<p>Block-printed textiles, cast brass and slow pottery from the families we have worked with for three generations.</p>',
                'button_label_1': 'Shop the house',
                'button_style_1': 'solid',
                'button_label_2': 'Our story',
                'button_style_2': 'outline',
                'show_motif': True,
            }),
            ('slide_2', 'slide', {
                'eyebrow': 'The festive edit',
                'heading': 'Made by hand, meant to last',
                'subheading': 'natural dyes · reclaimed wood · solid brass',
                'text': '<p>A small-batch collection for the season of gathering. Printed once, never reprinted.</p>',
                'button_label_1': 'Shop the edit',
                'button_style_1': 'solid',
                'content_position': 'center-center',
                'text_alignment': 'center',
                'show_motif': True,
            }),
            ('slide_3', 'slide', {
                'eyebrow': 'Winter 26',
                'heading': 'Nine dips of indigo',
                'subheading': 'dried in the Rajasthan sun',
                'text': '<p>Every length is dipped by hand, oxidised in the open, and signed by the printer.</p>',
                'button_label_1': 'See the indigo room',
                'button_style_1': 'solid',
                'content_position': 'center-right',
                'text_alignment': 'right',
                'text_tone': 'auto',
            }),
        ),
        'block_order': ['slide_1', 'slide_2', 'slide_3'],
    },
    'marquee': {
        'type': 'marquee',
        'settings': {
            'color_scheme': '5',
            'speed': 30,
            'direction': 'left',
            'separator': 'motif',
            'show_border': True,
            'full_width': True,
        },
        'blocks': blocks(
            ('m1', 'item', {'text': 'Handmade in Jaipur', 'icon': 'hand'}),
            ('m2', 'item', {'text': 'Natural dyes only', 'icon': 'leaf'}),
            ('m3', 'item', {'text': 'Free shipping over ₹5,000', 'icon': 'truck'}),
            ('m4', 'item', {'text': 'Maker named on every piece', 'icon': 'sparkle'}),
        ),
        'block_order': ['m1', 'm2', 'm3', 'm4'],
    },
    'collection_list': {
        'type': 'collection-list',
        'settings': {
            'eyebrow': 'Browse by craft',
            'heading': 'Six rooms of the house',
            'text': '<p>Textiles, brass, clay, wood, paper and the table — each room made by a different family of makers.</p>',
            'header_alignment': 'center',
            'columns_desktop': 3,
            'card_style': 'arch',
            'image_ratio': 'tall',
            'show_count': True,
            'view_all_label': 'All collections',
            'view_all_position': 'bottom',
        },
    },
    'featured_collection': {
        'type': 'featured-collection',
        'settings': {
            'eyebrow': 'Featured',
            'heading': 'The block-print table',
            'text': '<p>Printed lengths, napkins and runners from the Bagru workshop.</p>',
            'header_alignment': 'split',
            'products_to_show': 8,
            'layout': 'grid',
            'columns_desktop': 4,
            'columns_mobile': '2',
            'image_ratio': 'portrait',
            'quick_add': True,
            'view_all_label': 'View the whole collection',
            'view_all_style': 'button',
            'show_count': True,
        },
    },
    'story': {
        'type': 'image-with-text',
        'settings': {
            'image_position': 'left',
            'image_width': 52,
            'image_ratio': '4 / 5',
            'arch': True,
            'badge': 'Est. 1974',
            'spacing': 56,
            'color_scheme': '1',
        },
        'blocks': blocks(
            ('cap', 'caption', {'text': 'The workshop'}),
            ('head', 'heading', {'text': 'Printed one pass, one colour at a time', 'size': 'medium', 'tag': 'h2'}),
            ('body', 'text', {'text': '<p>A single Bagru print can need nine separate blocks and nine days of drying. We keep the count honest — you can read the registration marks on the reverse of every length.</p>'}),
            ('stat', 'stat', {'value': '40+', 'label': 'artisan families'}),
            ('list', 'list', {'items': 'Natural dyes, no azo pigments\nFair rates paid weekly\nMaker\u2019s name stamped underneath\nRepair service for life', 'icon': 'check'}),
            ('cta', 'button', {'label': 'Explore the craft', 'style': 'solid', 'label_2': 'Meet the makers'}),
        ),
        'block_order': ['cap', 'head', 'body', 'stat', 'list', 'cta'],
    },
    'usp': {
        'type': 'multicolumn',
        'settings': {
            'eyebrow': 'Why Kala Katha',
            'heading': 'Four promises we keep',
            'header_alignment': 'center',
            'layout': 'grid',
            'columns_desktop': 4,
            'columns_mobile': '1',
            'card_style': 'box',
            'media_type': 'icon',
            'text_alignment': 'center',
            'spacing': 24,
            'color_scheme': '1',
        },
        'blocks': blocks(
            ('u1', 'column', {'icon': 'hand', 'title': 'Made by one pair of hands', 'text': '<p>Every order names its maker. No assembly lines, no anonymous labour.</p>'}),
            ('u2', 'column', {'icon': 'leaf', 'title': 'Natural dyes only', 'text': '<p>Indigo, madder, pomegranate and iron — no azo pigments, ever.</p>'}),
            ('u3', 'column', {'icon': 'truck', 'title': 'Ships in 48 hours', 'text': '<p>Free across India above ₹5,000, worldwide with DHL.</p>'}),
            ('u4', 'column', {'icon': 'returns', 'title': '14-day returns', 'text': '<p>Changed your mind? Send it back unwashed and we will refund.</p>'}),
        ),
        'block_order': ['u1', 'u2', 'u3', 'u4'],
    },
    'lookbook': {
        'type': 'gallery',
        'settings': {
            'eyebrow': 'Lookbook',
            'heading': 'Winter 26, shot in Jaipur',
            'header_alignment': 'split',
            'layout': 'regular',
            'columns_desktop': 4,
            'columns_mobile': '2',
            'ratio': '3 / 4',
            'spacing': 14,
            'rounded': True,
            'lightbox': True,
            'show_product_link': True,
        },
        'blocks': blocks(
            ('g1', 'image', {'caption': 'Indigo, ninth dip', 'tall': True, 'wide': True}),
            ('g2', 'image', {'caption': 'Brass thali'}),
            ('g3', 'image', {'caption': 'Block table, Bagru'}),
            ('g4', 'image', {'caption': 'Drying yard', 'wide': True}),
            ('g5', 'image', {'caption': 'Terracotta', 'tall': True}),
        ),
        'block_order': ['g1', 'g2', 'g3', 'g4', 'g5'],
    },
    'testimonials': {
        'type': 'testimonials',
        'settings': {
            'color_scheme': '5',
            'eyebrow': 'Kind words',
            'heading': 'What our customers keep',
            'header_alignment': 'center',
            'layout': 'grid',
            'columns_desktop': 3,
            'card_style': 'card',
            'show_quote_mark': True,
            'footer_note': 'Reviews collected from verified orders',
        },
        'blocks': blocks(
            ('t1', 'testimonial', {'quote': 'The indigo throw is heavier and softer than I expected. You can feel the hand in it.', 'author': 'Meera S.', 'role': 'Mumbai', 'rating': 5, 'show_verified': True}),
            ('t2', 'testimonial', {'quote': 'It arrived wrapped in muslin with the maker\u2019s name on the tag. It felt like a gift, not a parcel.', 'author': 'Daniel R.', 'role': 'London', 'rating': 5, 'show_verified': True}),
            ('t3', 'testimonial', {'quote': 'Three years of daily use and the brass has only grown warmer. Worth every rupee.', 'author': 'Ananya K.', 'role': 'Bengaluru', 'rating': 5, 'show_verified': True}),
        ),
        'block_order': ['t1', 't2', 't3'],
    },
    'quote': {
        'type': 'quote',
        'settings': {
            'color_scheme': '1',
            'quote': 'We are not selling objects. We are asking you to keep a piece of someone\u2019s life\u2019s work in your home.',
            'author': 'Ananya Kala',
            'role': 'Founder, House of Kala Katha',
            'style': 'portrait',
            'text_alignment': 'center',
            'show_quote_mark': True,
            'show_motif': True,
        },
    },
    'journal': {
        'type': 'blog-posts',
        'settings': {
            'eyebrow': 'The journal',
            'heading': 'Stories from the workshops',
            'header_alignment': 'split',
            'posts_to_show': 3,
            'layout': 'grid',
            'columns_desktop': 3,
            'image_ratio': 'landscape',
            'arch': True,
            'show_excerpt': True,
            'show_date': True,
            'show_author': False,
            'view_all_label': 'Read the journal',
            'view_all_position': 'header',
        },
    },
    'newsletter': {
        'type': 'newsletter',
        'settings': {
            'color_scheme': '4',
            'eyebrow': 'The Kala Katha letter',
            'heading': 'Ten per cent off your first piece',
            'text': '<p>One letter a month: new releases, the makers behind them, and first access to small runs.</p>',
            'text_alignment': 'center',
            'form_style': 'inline',
            'button_label': 'Subscribe',
            'placeholder': 'Your email address',
            'note': 'No spam. Unsubscribe in one click.',
            'layout': 'plain',
            'show_motif': True,
        },
    },
}
write('index.json', homepage)


# ------------------------------------------------------------------ product
write('product.json', {
    'main': {
        'type': 'main-product',
        'settings': {'color_scheme': '1', 'show_full_description_below': True},
        'blocks': blocks(
            ('vendor', 'vendor', {'show_vendor': True}),
            ('title', 'title', {}),
            ('rating', 'rating', {}),
            ('price', 'price', {'show_sale_badge': True}),
            ('variant_picker', 'variant_picker', {'picker_type': 'buttons', 'show_selected_value': True, 'show_size_guide': False}),
            ('quantity_selector', 'quantity_selector', {'default_quantity': 1}),
            ('buy_buttons', 'buy_buttons', {'show_dynamic_checkout': True, 'full_width': True, 'show_pickup_note': False}),
            ('inventory_status', 'inventory_status', {}),
            ('description', 'description', {'truncate': 0}),
            ('acc_care', 'accordion', {'heading': 'Details & care', 'open_by_default': True}),
            ('acc_ship', 'accordion', {'heading': 'Shipping & returns'}),
            ('acc_maker', 'accordion', {'heading': 'Who made this'}),
            ('icons', 'icons', {'icon_1': 'hand', 'text_1': 'Handmade by one maker', 'icon_2': 'leaf', 'text_2': 'Natural dyes', 'icon_3': 'truck', 'text_3': 'Ships in 48 hours'}),
            ('share', 'share', {}),
        ),
        'block_order': ['vendor', 'title', 'rating', 'price', 'variant_picker', 'quantity_selector',
                         'buy_buttons', 'inventory_status', 'description', 'acc_care', 'acc_ship',
                         'acc_maker', 'icons', 'share'],
    },
    'recommendations': {
        'type': 'product-recommendations',
        'settings': {'heading': 'You may also like', 'limit': 4},
    },
})


# --------------------------------------------------------------- collection
write('collection.json', {
    'main': {'type': 'main-collection', 'settings': {'color_scheme': '1'}},
})


# --------------------------------------------------------------------- cart
write('cart.json', {
    'main': {'type': 'main-cart', 'settings': {'color_scheme': '1'}},
})


# --------------------------------------------------------------------- page
write('page.json', {
    'main': {'type': 'main-page', 'settings': {'color_scheme': '1'}},
})

write('page.contact.json', {
    'main': {
        'type': 'contact-form',
        'settings': {
            'eyebrow': 'Write to us',
            'heading': 'We answer every message',
            'text': '<p>Custom orders, trade enquiries, repairs, or a question about a piece you already own — tell us and we will reply within one working day.</p>',
            'header_alignment': 'center',
            'info_title': 'The house in Jaipur',
            'info_phone': '+91 98765 43210',
            'info_email': 'hello@houseofkalakatha.com',
            'show_social': True,
        },
        'blocks': blocks(
            ('name', 'text_field', {'label': 'Name', 'name': 'Name', 'type': 'text', 'half_width': True, 'required': True}),
            ('email', 'text_field', {'label': 'Email', 'name': 'email', 'type': 'email', 'half_width': True, 'required': True}),
            ('phone', 'text_field', {'label': 'Phone', 'name': 'Phone', 'type': 'tel', 'half_width': True, 'required': False}),
            ('topic', 'select', {'label': 'What is this about?', 'name': 'Enquiry type', 'options': 'A custom order, An existing order, A repair, Wholesale, Something else', 'placeholder': 'Please choose'}),
            ('message', 'textarea', {'label': 'Your message', 'name': 'body', 'rows': 6, 'required': True}),
            ('send', 'submit', {'label': 'Send message', 'style': 'solid', 'note': 'Or WhatsApp us on +91 98765 43210'}),
        ),
        'block_order': ['name', 'email', 'phone', 'topic', 'message', 'send'],
    },
    'faq': {
        'type': 'faq',
        'settings': {
            'eyebrow': 'Good to know',
            'heading': 'Questions we are asked often',
            'header_alignment': 'center',
            'layout': 'single',
            'open_first': True,
            'help_text': 'Still unsure about something?',
            'help_label': 'Read our shipping policy',
        },
        'blocks': blocks(
            ('q1', 'faq_item', {'question': 'How should I wash block-printed cotton?', 'answer': '<p>Cold water, a mild liquid detergent and a short gentle cycle or hand wash. Dry in the shade — direct sun fades natural dyes faster than anything else.</p>', 'open_by_default': True}),
            ('q2', 'faq_item', {'question': 'Will the colours run?', 'answer': '<p>Natural dyes settle after the first two washes. Wash separately in cold water until then.</p>'}),
            ('q3', 'faq_item', {'question': 'How long does shipping take?', 'answer': '<p>Orders leave Jaipur within 48 hours. Metro delivery is 2–4 days; international is 5–9 days with DHL.</p>'}),
            ('q4', 'faq_item', {'question': 'Do you repair pieces?', 'answer': '<p>Yes. Send anything back at any time and our makers will mend it.</p>'}),
            ('q5', 'faq_item', {'question': 'Can I order in bulk for a hotel or restaurant?', 'answer': '<p>We do. Write to us with your quantities and timelines and we will match you with a workshop.</p>'}),
        ),
        'block_order': ['q1', 'q2', 'q3', 'q4', 'q5'],
    },
    'stores': {
        'type': 'store-info',
        'settings': {
            'eyebrow': 'Visit us',
            'heading': 'Come and touch the cloth',
            'text': '<p>Three rooms, three cities. Tea is always on.</p>',
            'columns_desktop': 3,
            'card_style': 'card',
            'image_ratio': '4 / 3',
        },
        'blocks': blocks(
            ('s1', 'store', {'name': 'Jaipur — the house', 'badge': 'Flagship', 'phone': '+91 98765 43210', 'email': 'jaipur@houseofkalakatha.com', 'button_label': 'Book a viewing'}),
            ('s2', 'store', {'name': 'Mumbai — Kala Room', 'badge': 'Studio', 'address': '<p>2 Kala Ghoda Lane, Fort<br>Mumbai 400001</p>', 'hours': '<p>Tue – Sun, 11am – 8pm</p>', 'phone': '+91 98123 45678', 'email': 'mumbai@houseofkalakatha.com'}),
            ('s3', 'store', {'name': 'Delhi — by appointment', 'address': '<p>7 Lodhi Colony, New Delhi 110003</p>', 'hours': '<p>Appointment only</p>', 'phone': '+91 98000 11223', 'email': 'delhi@houseofkalakatha.com'}),
        ),
        'block_order': ['s1', 's2', 's3'],
    },
})

write('page.about.json', {
    'hero': {
        'type': 'hero',
        'settings': {
            'eyebrow': 'House of Kala Katha',
            'heading': 'A house, not a factory',
            'heading_2': 'three generations of makers',
            'text': '<p>We began with one printing table in Chandpol Bazaar in 1974. Fifty years later we still print by hand — we simply have more tables, and more families around them.</p>',
            'button_label_1': 'Shop the house',
            'button_label_2': 'Meet the makers',
            'meta_text': 'Jaipur · Bagru · Moradabad · Khurja',
            'meta_icon': 'pin',
            'image_position': 'right',
            'content_width': 46,
            'image_ratio': '3 / 4',
            'arch': True,
            'show_frame': True,
            'caption': 'Since 1974',
        },
    },
    'timeline': {
        'type': 'story-timeline',
        'settings': {
            'eyebrow': 'Since 1974',
            'heading': 'Fifty years of keeping a craft alive',
            'text': '<p>From one printing table to forty artisan families across three states.</p>',
            'header_alignment': 'center',
            'layout': 'center',
            'image_ratio': '4 / 3',
            'arch': True,
            'footer_text': 'The next fifty start with the makers we train today.',
            'footer_label': 'Meet the makers',
        },
        'blocks': blocks(
            ('y1', 'milestone', {'year': '1974', 'title': 'One table, two blocks', 'text': '<p>Kala Devi begins printing lengths of cotton from a single table behind her family\u2019s shop in Chandpol Bazaar.</p>', 'accent': True}),
            ('y2', 'milestone', {'year': '1988', 'title': 'The first workshop', 'text': '<p>Four printers join Kala Devi and the house moves into its own courtyard in Bagru.</p>', 'icon': 'loom'}),
            ('y3', 'milestone', {'year': '2009', 'title': 'Natural dyes only', 'text': '<p>Every synthetic pigment leaves the workshop. The indigo vats are rebuilt from scratch.</p>', 'icon': 'leaf'}),
            ('y4', 'milestone', {'year': '2018', 'title': 'Brass, clay and wood', 'text': '<p>We begin working with casters in Moradabad and potters in Khurja.</p>', 'icon': 'sparkle'}),
            ('y5', 'milestone', {'year': '2026', 'title': 'Forty families, one standard', 'text': '<p>Kala Katha now trains twelve apprentices a year and repairs anything it has ever sold.</p>', 'icon': 'globe'}),
        ),
        'block_order': ['y1', 'y2', 'y3', 'y4', 'y5'],
    },
    'process': {
        'type': 'video',
        'settings': {
            'eyebrow': 'Inside the workshop',
            'heading': 'Nine passes of indigo',
            'text': '<p>Watch a length of cloth move from raw cotton to finished indigo in forty seconds.</p>',
            'header_alignment': 'center',
            'layout': 'full',
            'ratio': '16 / 9',
            'caption': 'Filmed in Bagru, Rajasthan',
        },
    },
    'makers': {
        'type': 'multicolumn',
        'settings': {
            'eyebrow': 'The workshops',
            'heading': 'Where each craft is made',
            'header_alignment': 'center',
            'layout': 'grid',
            'columns_desktop': 3,
            'card_style': 'arch',
            'media_type': 'image',
            'image_ratio': '1 / 1',
            'text_alignment': 'center',
        },
        'blocks': blocks(
            ('c1', 'column', {'title': 'Bagru — block printing', 'text': '<p>Nine families, eleven tables, one indigo vat that has never been allowed to die.</p>'}),
            ('c2', 'column', {'title': 'Moradabad — brass casting', 'text': '<p>Sand-cast, hand-finished, and left unlacquered so it ages with you.</p>'}),
            ('c3', 'column', {'title': 'Khurja — pottery', 'text': '<p>Thrown on the wheel and fired twice, for glazes that do not craze.</p>'}),
        ),
        'block_order': ['c1', 'c2', 'c3'],
    },
    'quote': {
        'type': 'quote',
        'settings': {
            'color_scheme': '3',
            'quote': 'The cloth remembers the hand that printed it.',
            'author': 'Ramesh Chhipa',
            'role': 'Master printer, Bagru',
            'style': 'card',
            'text_alignment': 'center',
        },
    },
    'press': {
        'type': 'logo-list',
        'settings': {
            'eyebrow': 'As seen in',
            'heading': 'Written about, stocked and loved',
            'header_alignment': 'center',
            'layout': 'grid',
            'columns_desktop': 4,
            'treatment': 'grayscale',
            'logo_height': 34,
        },
        'blocks': blocks(
            ('p1', 'logo', {'text': 'Vogue India'}),
            ('p2', 'logo', {'text': 'Condé Nast Traveller'}),
            ('p3', 'logo', {'text': 'Elle Decor'}),
            ('p4', 'logo', {'text': 'The Hindu'}),
        ),
        'block_order': ['p1', 'p2', 'p3', 'p4'],
    },
    'cta': {
        'type': 'rich-text',
        'settings': {
            'color_scheme': '1',
            'eyebrow': 'Start here',
            'heading': 'Slow-made objects for everyday rituals',
            'text': '<p>Everything we sell can be repaired, re-dyed or re-blocked by the family that made it. That is the whole business model.</p>',
            'text_width': 'narrow',
            'text_alignment': 'center',
            'button_label': 'Shop the house',
            'button_style': 'solid',
            'show_motif': True,
        },
    },
})


# --------------------------------------------------------------------- blog
write('blog.json', {
    'main': {'type': 'main-blog', 'settings': {'color_scheme': '1'}},
})

write('article.json', {
    'main': {'type': 'main-article', 'settings': {'color_scheme': '1'}},
})


# ------------------------------------------------------------------- search
write('search.json', {
    'main': {'type': 'main-search', 'settings': {'color_scheme': '1'}},
})

write('list-collections.json', {
    'main': {'type': 'main-list-collections', 'settings': {'color_scheme': '1'}},
})


# ---------------------------------------------------------------------- 404
write('404.json', {
    'main': {'type': 'main-404', 'settings': {'color_scheme': '1'}},
    'recovery': {
        'type': 'featured-collection',
        'settings': {
            'eyebrow': 'While you are here',
            'heading': 'Pieces people come back for',
            'header_alignment': 'center',
            'products_to_show': 4,
            'columns_desktop': 4,
            'layout': 'grid',
            'view_all_label': '',
            'view_all_style': 'none',
        },
    },
})


# ----------------------------------------------------------------- password
write('password.json', {
    'main': {'type': 'main-password', 'settings': {'color_scheme': '1'}},
})


# ---------------------------------------------------------------- customers
write('customers/login.json', {
    'main': {'type': 'main-customers-login', 'settings': {'color_scheme': '1'}},
})
write('customers/register.json', {
    'main': {'type': 'main-customers-register', 'settings': {'color_scheme': '1'}},
})
write('customers/reset_password.json', {
    'main': {'type': 'main-customers-reset-password', 'settings': {'color_scheme': '1'}},
})
write('customers/activate_account.json', {
    'main': {'type': 'main-customers-activate-account', 'settings': {'color_scheme': '1'}},
})
write('customers/account.json', {
    'main': {'type': 'main-customers-account', 'settings': {'color_scheme': '1'}},
})
write('customers/order.json', {
    'main': {'type': 'main-customers-order', 'settings': {'color_scheme': '1'}},
})
write('customers/addresses.json', {
    'main': {'type': 'main-customers-addresses', 'settings': {'color_scheme': '1'}},
})

print('\nAll templates written.')
