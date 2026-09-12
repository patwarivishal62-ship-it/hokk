"""Generates snippets/icon.liquid (inline SVG icon set) and snippets/motif.liquid."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

STROKE = {
 'cart': '<circle cx="9.5" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/><path d="M2 3h2.6l2.2 11.2a2 2 0 0 0 2 1.6h8.5a2 2 0 0 0 2-1.5L21 7H6"/>',
 'bag': '<path d="M6.2 2.5h11.6l2.2 4v13a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-13l2.2-4Z"/><path d="M4 6.5h16"/><path d="M16 10a4 4 0 0 1-8 0"/>',
 'search': '<circle cx="11" cy="11" r="7"/><path d="m20.5 20.5-4.2-4.2"/>',
 'user': '<path d="M20 21v-1.6A4.4 4.4 0 0 0 15.6 15H8.4A4.4 4.4 0 0 0 4 19.4V21"/><circle cx="12" cy="7.2" r="4.2"/>',
 'menu': '<path d="M3 6h18M3 12h18M3 18h18"/>',
 'close': '<path d="M18.5 5.5 5.5 18.5M5.5 5.5l13 13"/>',
 'chevron-down': '<path d="m6 9.5 6 6 6-6"/>',
 'chevron-up': '<path d="m6 14.5 6-6 6 6"/>',
 'chevron-left': '<path d="m14.5 5.5-6 6.5 6 6.5"/>',
 'chevron-right': '<path d="m9.5 5.5 6 6.5-6 6.5"/>',
 'arrow-right': '<path d="M4 12h15M13 6l6 6-6 6"/>',
 'arrow-left': '<path d="M20 12H5M11 18l-6-6 6-6"/>',
 'arrow-up': '<path d="M12 20V5M6 11l6-6 6 6"/>',
 'arrow-down': '<path d="M12 4v15M6 13l6 6 6-6"/>',
 'plus': '<path d="M12 5v14M5 12h14"/>',
 'minus': '<path d="M5 12h14"/>',
 'check': '<path d="m20 6.5-11 11-5-5"/>',
 'check-circle': '<circle cx="12" cy="12" r="9.2"/><path d="m8 12.2 2.7 2.7L16.2 9.4"/>',
 'heart': '<path d="M20.6 5.6a5.2 5.2 0 0 0-7.4 0L12 6.8l-1.2-1.2a5.2 5.2 0 1 0-7.4 7.4l1.2 1.2L12 21.4l7.4-7.2 1.2-1.2a5.2 5.2 0 0 0 0-7.4Z"/>',
 'truck': '<path d="M1.8 5.5h12.4v10.8H1.8z"/><path d="M14.2 9h3.9l3.1 3.2v4.1h-7"/><circle cx="6" cy="18.2" r="2"/><circle cx="17.4" cy="18.2" r="2"/>',
 'returns': '<path d="M21.5 4.5v5.2h-5.2"/><path d="M20.4 14.6a8.6 8.6 0 1 1-2-8.4l3.1 3.1"/>',
 'shield': '<path d="M12 21.5s7.6-3.7 7.6-9.6V5.4L12 2.6 4.4 5.4v6.5c0 5.9 7.6 9.6 7.6 9.6Z"/><path d="m9.2 11.8 2 2 3.6-3.8"/>',
 'leaf': '<path d="M11 20.5A7.5 7.5 0 0 1 9.6 6C15.4 4.9 17 4.3 19 2c1 2.1 2 4.4 2 8.3 0 5.7-4.9 10.2-10 10.2Z"/><path d="M2.5 21.5c0-3.1 2-5.6 5.3-6.3 2.4-.5 4.9-2 6-3.2"/>',
 'sparkle': '<path d="M11 2.5 12.9 8.6 19 10.5 12.9 12.4 11 18.5 9.1 12.4 3 10.5 9.1 8.6 11 2.5Z"/><path d="m18.4 15.6.9 2.6 2.6.9-2.6.9-.9 2.6-.9-2.6-2.6-.9 2.6-.9.9-2.6Z"/>',
 'phone': '<path d="M21.5 16.9v2.8a2 2 0 0 1-2.2 2 19.6 19.6 0 0 1-8.5-3 19.3 19.3 0 0 1-6-6 19.6 19.6 0 0 1-3-8.6 2 2 0 0 1 2-2.1h2.8a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L7.6 9.9a16 16 0 0 0 6 6l1.3-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/>',
 'mail': '<rect x="2.2" y="4.4" width="19.6" height="15.2" rx="2.2"/><path d="m2.6 7.2 9.4 5.9 9.4-5.9"/>',
 'pause': '<path d="M8.5 5v14M15.5 5v14"/>',
 'zoom': '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3M11 8.2v5.6M8.2 11h5.6"/>',
 'quote': '<path d="M9.6 5.5C6.4 6.9 4.5 9.9 4.5 13.4c0 3 1.7 5.1 4.2 5.1 2.1 0 3.7-1.5 3.7-3.6 0-2-1.4-3.4-3.3-3.4-.4 0-.8 0-1 .2.3-1.7 1.6-3.3 3.4-4.2l-1.9-2Zm9 0c-3.2 1.4-5.1 4.4-5.1 7.9 0 3 1.7 5.1 4.2 5.1 2.1 0 3.7-1.5 3.7-3.6 0-2-1.4-3.4-3.3-3.4-.4 0-.8 0-1 .2.3-1.7 1.6-3.3 3.4-4.2l-1.9-2Z"/>',
 'gift': '<rect x="2.8" y="8.2" width="18.4" height="4" rx="1"/><path d="M4.6 12.2V21h14.8v-8.8M12 8.2V21"/><path d="M12 8.2S10.6 3.2 8.1 3.2a2.5 2.5 0 0 0 0 5H12Zm0 0s1.4-5 3.9-5a2.5 2.5 0 0 1 0 5H12Z"/>',
 'package': '<path d="m12 2.4 9 4.8v9.6l-9 4.8-9-4.8V7.2l9-4.8Z"/><path d="m3.3 7.4 8.7 4.7 8.7-4.7M12 12.1v9.5"/>',
 'clock': '<circle cx="12" cy="12" r="9.2"/><path d="M12 6.8V12l3.6 2.1"/>',
 'pin': '<path d="M20.8 10.2c0 5.8-8.8 11.6-8.8 11.6s-8.8-5.8-8.8-11.6a8.8 8.8 0 1 1 17.6 0Z"/><circle cx="12" cy="10" r="3.1"/>',
 'card': '<rect x="2.2" y="5" width="19.6" height="14" rx="2.2"/><path d="M2.2 10h19.6M6 14.8h3.4"/>',
 'lock': '<rect x="4.2" y="10.4" width="15.6" height="10.8" rx="2"/><path d="M8 10.4V7.2a4 4 0 0 1 8 0v3.2"/>',
 'trash': '<path d="M3.5 6.2h17M8.5 6.2V4h7v2.2M6.2 6.2 7.3 21h9.4l1.1-14.8"/>',
 'share': '<circle cx="18" cy="5.4" r="2.8"/><circle cx="6" cy="12" r="2.8"/><circle cx="18" cy="18.6" r="2.8"/><path d="m8.5 10.7 7-4M8.5 13.3l7 4"/>',
 'info': '<circle cx="12" cy="12" r="9.2"/><path d="M12 16.4v-5M12 8.1h.01"/>',
 'alert': '<path d="M12 3.2 2.2 20.4h19.6L12 3.2Z"/><path d="M12 9.6v4.2M12 17.2h.01"/>',
 'grid': '<rect x="3.2" y="3.2" width="7.4" height="7.4" rx="1.2"/><rect x="13.4" y="3.2" width="7.4" height="7.4" rx="1.2"/><rect x="3.2" y="13.4" width="7.4" height="7.4" rx="1.2"/><rect x="13.4" y="13.4" width="7.4" height="7.4" rx="1.2"/>',
 'list': '<path d="M8.5 6.2h12M8.5 12h12M8.5 17.8h12M3.6 6.2h.01M3.6 12h.01M3.6 17.8h.01"/>',
 'eye': '<path d="M2.2 12S5.9 5.2 12 5.2 21.8 12 21.8 12 18.1 18.8 12 18.8 2.2 12 2.2 12Z"/><circle cx="12" cy="12" r="3.2"/>',
 'sort': '<path d="M7 4.2v15.6M7 19.8 4 16.8M7 19.8l3-3M17 19.8V4.2M17 4.2l-3 3M17 4.2l3 3"/>',
 'filter': '<path d="M3.2 5h17.6l-6.9 8v6.2l-3.8 1.8V13L3.2 5Z"/>',
 'external': '<path d="M14.2 3.8h6v6"/><path d="M20.2 3.8 11 13"/><path d="M18 14.2v5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-11a2 2 0 0 1 2-2h5"/>',
 'chat': '<path d="M21 11.6a7.9 7.9 0 0 1-8.4 7.9 9.5 9.5 0 0 1-2.7-.4L4 21l1.5-4.2A7.8 7.8 0 0 1 3.6 11 7.9 7.9 0 0 1 12 3.7a7.9 7.9 0 0 1 9 7.9Z"/>',
 'ruler': '<path d="m14.7 3.2 6.1 6.1L10.9 19.2 4.8 13.1 14.7 3.2Z"/><path d="m8.4 9.5 1.8 1.8M11.2 6.7 13 8.5M5.6 12.3l1.8 1.8"/>',
 'brush': '<path d="M17.6 3.4a2.6 2.6 0 0 1 3.6 3.6L11 17.2l-4.4.8.8-4.4L17.6 3.4Z"/><path d="M6.6 19.2c0 1.3-1.1 2.4-2.4 2.4H3"/>',
 'scissors': '<circle cx="6" cy="6" r="2.6"/><circle cx="6" cy="18" r="2.6"/><path d="M20 4 8.6 15.4M8.6 8.6 20 20M8.6 8.6H6M6 15.4h2.6"/>',
 'globe': '<circle cx="12" cy="12" r="9.2"/><path d="M2.8 12h18.4M12 2.8c2.4 2.6 3.6 5.7 3.6 9.2s-1.2 6.6-3.6 9.2c-2.4-2.6-3.6-5.7-3.6-9.2S9.6 5.4 12 2.8Z"/>',
 'instagram': '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.1"/><circle cx="17.3" cy="6.7" r="1.1" fill="currentColor" stroke="none"/>',
 'pinterest': '<circle cx="12" cy="12" r="9.4"/><path d="M9.9 20.2c-.6-1 .1-2.4.3-3.3l.9-3.7c-.2-.5-.3-1-.2-1.6.1-1.2 1.1-2.1 2.2-2 1 0 1.5.7 1.5 1.6 0 1.1-.6 2.6-.9 4-.2.8.2 1.5 1.1 1.5 1.6 0 2.7-2 2.7-4.3 0-1.8-1.3-3.2-3.5-3.2-2.5 0-4.1 1.8-4.1 3.8 0 .7.2 1.2.5 1.6.1.2.2.3.1.5l-.2.7c0 .2-.2.3-.4.2-1.1-.5-1.6-1.8-1.6-3.2 0-2.5 2-5.4 6.1-5.4 3.2 0 5.4 2.3 5.4 4.8 0 3.3-1.9 5.7-4.6 5.7-.9 0-1.8-.5-2.1-1.1l-.6 2.2c-.2.8-.6 1.6-1 2.2Z"/>',
 'youtube': '<rect x="2.2" y="5.2" width="19.6" height="13.6" rx="4"/><path d="m10.2 9.2 5 2.8-5 2.8V9.2Z"/>',
 'linkedin': '<rect x="3" y="3" width="18" height="18" rx="3.4"/><path d="M7.6 10.4v6.2M7.6 7.5v.1M11.4 16.6v-3.4c0-1 .6-1.8 1.6-1.8s1.5.8 1.5 1.8v3.4M11.4 16.6v-6.2"/>',
 'hand': '<path d="M9 11V5.6a1.4 1.4 0 0 1 2.8 0V11m0-.6V4.4a1.4 1.4 0 0 1 2.8 0v6m0-.6V6.2a1.4 1.4 0 0 1 2.8 0v8.4c0 3.6-2.4 6.6-6 6.6s-6-2.6-6-6v-3a1.4 1.4 0 0 1 2.6-.7L9 13"/>',
 'loom': '<path d="M3 4h18v16H3z"/><path d="M7 4v16M12 4v16M17 4v16M3 9h18M3 15h18"/>',
}

FILLED = {
 'star': '<path d="m12 2.2 3.1 6.3 6.9 1-5 4.9 1.2 6.9L12 18l-6.2 3.3L7 14.4l-5-4.9 6.9-1L12 2.2Z"/>',
 'star-half': '<path d="m12 2.2 3.1 6.3 6.9 1-5 4.9 1.2 6.9L12 18l-6.2 3.3L7 14.4l-5-4.9 6.9-1L12 2.2Zm0 0v15.8l-6.2 3.3" fill="none" stroke="currentColor" stroke-width="1.2"/>',
 'play': '<path d="M6.5 3.6v16.8L20.5 12 6.5 3.6Z"/>',
 'whatsapp': '<path d="M12.05 2.5a9.4 9.4 0 0 0-8.1 14.2L2.5 21.5l4.9-1.4a9.4 9.4 0 1 0 4.65-17.6Zm0 1.7a7.7 7.7 0 1 1-4 14.3l-.3-.2-2.9.8.8-2.8-.2-.3a7.7 7.7 0 0 1 6.6-11.8Zm-2.6 3.4c-.2 0-.5.1-.7.4-.3.3-.9 1-.9 2.3 0 1.4 1 2.7 1.1 2.9.2.2 2 3.1 4.9 4.2 2.4.9 2.9.7 3.4.7.6-.1 1.8-.7 2-1.4.3-.7.3-1.3.2-1.4-.1-.2-.3-.2-.6-.4l-1.9-.9c-.2-.1-.4-.1-.6.1l-.8 1c-.2.2-.3.2-.5.1-.3-.1-1.2-.4-2.2-1.4-.8-.7-1.3-1.5-1.5-1.8-.1-.2 0-.4.1-.5l.4-.5c.2-.2.2-.3.3-.5v-.5c-.1-.1-.6-1.5-.8-2-.2-.5-.4-.5-.6-.5h-.5Z"/>',
 'facebook': '<path d="M13.5 21.5v-7.8h2.6l.4-3h-3V8.8c0-.9.3-1.5 1.5-1.5h1.6V4.6c-.3 0-1.3-.1-2.4-.1-2.4 0-4 1.4-4 4.1v2.1H7.5v3h2.7v7.8h3.3Z"/>',
 'tiktok': '<path d="M16.2 2.5h-2.9v12.2c0 1.4-1.1 2.5-2.5 2.5s-2.5-1.1-2.5-2.5 1.1-2.5 2.5-2.5c.3 0 .5 0 .8.1V9.2c-.3 0-.5-.1-.8-.1a5.4 5.4 0 1 0 5.4 5.4V9.1c1 .7 2.3 1.1 3.6 1.1V7.3c-1.9 0-3.6-1.6-3.6-3.6V2.5Z"/>',
 'twitter': '<path d="M17.5 3h3.1l-6.8 7.8L21.8 21h-6.2l-4.9-6.4L5.1 21H2l7.3-8.3L2.4 3h6.4l4.4 5.8L17.5 3Zm-1.1 16.1h1.7L7.7 4.8H5.9l10.5 14.3Z"/>',
}

names = list(STROKE.keys()) + [k for k in FILLED if k not in STROKE]

out = ["""{%- comment -%}
  Inline SVG icon set for the Kala Katha theme. No icon fonts, no image files.
  Usage: {% render 'icon', name: 'cart' %}   |   {% render 'icon', name: 'cart', size: 28 %}
{%- endcomment -%}
{%- liquid
  assign stroke = settings.icon_weight
  if stroke == blank
    assign stroke = 1.5
  endif
  assign size = size | default: settings.icon_size | default: 22
-%}"""]
out.append('<span class="icon icon--{{ name }}" style="--icon-size: {{ size }}px" aria-hidden="true" focusable="false">')
out.append('  {%- case name -%}')
for name in names:
    if name in FILLED:
        attrs = 'fill="currentColor" stroke="none"'
        body = FILLED[name]
    else:
        attrs = 'fill="none" stroke="currentColor" stroke-width="{{ stroke }}" stroke-linecap="round" stroke-linejoin="round"'
        body = STROKE[name]
    out.append('  {%- when \'' + name + '\' -%}')
    out.append('    <svg class="icon__svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" ' + attrs + '>' + body + '</svg>')
out.append('  {%- else -%}')
out.append('    <svg class="icon__svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{{ stroke }}" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 8v8M8 12h8"/></svg>')
out.append('  {%- endcase -%}')
out.append('</span>')

(ROOT / 'snippets' / 'icon.liquid').write_text('\n'.join(out) + '\n')

# ---------------------------------------------------------------- motifs
MOTIF = {
 'lotus': '<path d="M32 46c0-8 6-14 6-14s6 6 6 14-6 14-6 14-6-6-6-14Z" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M38 32c-4-6-4-14-4-14s8 4 12 10" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M38 32c4-6 4-14 4-14s-8 4-12 10" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M14 52c6-8 14-10 14-10M62 52c-6-8-14-10-14-10" fill="none" stroke="currentColor" stroke-width="1.4"/><circle cx="38" cy="46" r="2.4" fill="currentColor"/>',
 'sun': '<circle cx="38" cy="38" r="9" fill="none" stroke="currentColor" stroke-width="1.4"/><circle cx="38" cy="38" r="3" fill="currentColor"/><g stroke="currentColor" stroke-width="1.4"><path d="M38 12v10M38 54v10M12 38h10M54 38h10M20 20l7 7M49 49l7 7M56 20l-7 7M27 49l-7 7"/></g>',
 'jali': '<g fill="none" stroke="currentColor" stroke-width="1.3"><path d="M38 14 62 38 38 62 14 38Z"/><path d="M38 26 50 38 38 50 26 38Z"/><path d="M38 14v12M38 50v12M14 38h12M50 38h12"/><circle cx="38" cy="38" r="3" fill="currentColor" stroke="none"/></g>',
 'paisley': '<path d="M40 12c14 6 18 22 10 32-7 9-20 10-27 4-6-5-6-14 0-18 5-3 11-1 12 4 1 4-3 7-6 6" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/><path d="M22 60c10 4 24 2 32-6" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><circle cx="40" cy="12" r="2" fill="currentColor"/>',
 'rule': '<path d="M4 38h24M48 38h24" stroke="currentColor" stroke-width="1.3"/><path d="m38 30 8 8-8 8-8-8 8-8Z" fill="none" stroke="currentColor" stroke-width="1.3"/><circle cx="38" cy="38" r="2.2" fill="currentColor"/>',
}
m = ["""{%- comment -%}
  Decorative hand-drawn motif used as a section divider.
  Usage: {% render 'motif', style: settings.motif_style %}
{%- endcomment -%}
{%- liquid
  assign motif = style | default: settings.motif_style | default: 'lotus'
-%}"""]
m.append('<span class="motif motif--{{ motif }}" aria-hidden="true" focusable="false">')
m.append('  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 76 76" width="100%" height="100%">')
m.append('  {%- case motif -%}')
for key, body in MOTIF.items():
    m.append('    {%- when \'' + key + '\' -%}')
    m.append('      ' + body)
m.append('    {%- else -%}')
m.append('      ' + MOTIF['lotus'])
m.append('  {%- endcase -%}')
m.append('  </svg>')
m.append('</span>')
(ROOT / 'snippets' / 'motif.liquid').write_text('\n'.join(m) + '\n')
print('wrote icon.liquid with', len(names), 'icons and motif.liquid with', len(MOTIF), 'motifs')
