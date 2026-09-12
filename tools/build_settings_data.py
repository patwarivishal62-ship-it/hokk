#!/usr/bin/env python3
"""Build config/settings_data.json from settings_schema.json defaults + brand overrides.

Every value written here is checked against the schema by tools/validate.py.
Run:  python3 tools/build_settings_data.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA = ROOT / 'config' / 'settings_schema.json'
OUT = ROOT / 'config' / 'settings_data.json'

OVERRIDES = {
    'logo_text': 'House of Kala Katha',
    'brand_tagline': 'Objects that carry a story',
    'brand_established': 'Est. 1974 · Jaipur',
    'type_header_font': 'playfair_display_n4',
    'type_body_font': 'assistant_n4',
    'type_h1_size': 64,
    'type_h2_size': 40,
    'page_width': 1400,
    'section_spacing': 96,
    'motif_style': 'lotus',
    'arch_shape': 'pointed',
    'product_card_style': 'standard',
    'product_image_ratio': 'portrait',
    'product_quick_add_style': 'overlay',
    'product_media_layout': 'thumbs_left',
    'collection_products_per_row': '4',
    'collection_products_per_page': '24',
    'collection_filters_layout': 'sidebar',
    'cart_type': 'drawer',
    'cart_free_shipping_threshold': 5000,
    'animations_enable': True,
    'animations_style': 'rise',
    'header_behavior': 'sticky',
    'icon_weight': '1.5',
    'social_instagram_link': 'https://www.instagram.com/houseofkalakatha',
    'social_facebook_link': 'https://www.facebook.com/houseofkalakatha',
    'social_pinterest_link': 'https://www.pinterest.com/houseofkalakatha',
    'social_youtube_link': 'https://www.youtube.com/@houseofkalakatha',
    'contact_phone': '+91 98765 43210',
    'contact_email': 'hello@houseofkalakatha.com',
    'contact_whatsapp': '+919876543210',
    'whatsapp_floating': False,
    'contact_address': 'House of Kala Katha, Amer Road, Jaipur, Rajasthan 302002, India',
    'contact_hours': 'Monday to Saturday, 10:00 – 19:00 IST',
}

HEADER_GROUP = {
    'type': 'header-group',
    'sections': {
        'announcement': {
            'type': 'announcement-bar',
            'settings': {
                'color_scheme': '2',
                'rotate': True,
                'padding': 12,
                'show_social': False,
                'hide_on_mobile': False,
            },
            'blocks': {
                'ship': {
                    'type': 'announcement',
                    'settings': {
                        'text': 'Complimentary shipping across India above ₹5,000',
                        'icon': 'truck',
                        'show_countdown': False,
                    },
                },
                'made': {
                    'type': 'announcement',
                    'settings': {
                        'text': 'Every piece is signed by the maker — look for the stamp underneath',
                        'icon': 'hand',
                        'show_countdown': False,
                    },
                },
                'festive': {
                    'type': 'announcement',
                    'settings': {
                        'text': 'The festive run is closing — order by Sunday',
                        'link': '/collections/all',
                        'icon': 'sparkle',
                        'show_countdown': True,
                        'countdown_date': '2026-12-31T23:59',
                        'countdown_finished': 'The festive run has closed',
                    },
                },
            },
            'block_order': ['ship', 'made', 'festive'],
        },
        'header': {
            'type': 'header',
            'settings': {
                'color_scheme': '1',
                'layout': 'logo-left',
                'logo_width': 170,
                'padding': 16,
                'show_border': True,
                'compact_on_scroll': True,
                'show_search': True,
                'search_style': 'drawer',
                'show_account': True,
                'show_cart': True,
                'cart_icon': 'bag',
                'show_menu_images': True,
                'mega_columns': 4,
                'show_contact_block': True,
                'search_suggestions': 'Block print, Brass, Indigo, Table linen, Gifts under 2000',
            },
        },
    },
    'order': ['announcement', 'header'],
}

FOOTER_GROUP = {
    'type': 'footer-group',
    'sections': {
        'footer': {
            'type': 'footer',
            'settings': {
                'color_scheme': '2',
                'columns': 4,
                'show_motif': True,
                'show_bottom_bar': True,
                'copyright_text': 'All rights reserved',
                'show_payment': True,
                'show_localization': False,
                'show_theme_credit': False,
            },
            'blocks': {
                'brand': {
                    'type': 'text',
                    'settings': {
                        'heading': 'House of Kala Katha',
                        'text': '<p>Block-printed textiles, cast brass and slow pottery, made with forty artisan families across Rajasthan, Gujarat and Bengal since 1974.</p>',
                        'show_logo': True,
                        'logo_width': 160,
                        'show_social': True,
                        'button_label': 'Our story',
                        'button_link': '/pages/about',
                    },
                },
                'shop': {
                    'type': 'menu',
                    'settings': {'heading': 'Shop'},
                },
                'help': {
                    'type': 'menu',
                    'settings': {'heading': 'Help'},
                },
                'newsletter': {
                    'type': 'newsletter',
                    'settings': {
                        'heading': 'The Kala Katha letter',
                        'text': '<p>One letter a month: new releases, the makers behind them and first access to small runs.</p>',
                        'placeholder': 'Your email address',
                        'button_label': 'Subscribe',
                        'form_style': 'underline',
                    },
                },
            },
            'block_order': ['brand', 'shop', 'help', 'newsletter'],
        },
    },
    'order': ['footer'],
}


def main():
    schema = json.loads(SCHEMA.read_text())
    current = {}
    for group in schema:
        if 'theme_info' in group:
            continue
        for setting in group.get('settings', []):
            sid = setting.get('id')
            if not sid:
                continue
            if sid in OVERRIDES:
                current[sid] = OVERRIDES[sid]
            elif setting.get('default') is not None:
                current[sid] = setting['default']
    current['sections'] = {'header-group': HEADER_GROUP, 'footer-group': FOOTER_GROUP}

    preset_values = {k: v for k, v in current.items() if k != 'sections'}
    payload = {
        'current': current,
        'presets': {'Kala Katha': preset_values},
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n')
    print(f'wrote {OUT.relative_to(ROOT)} with {len(preset_values)} theme settings')

    for key, value in OVERRIDES.items():
        if key not in current:
            print('WARNING: override for unknown setting', key)


if __name__ == '__main__':
    main()
