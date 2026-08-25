#!/usr/bin/env python3
"""Generate sv/index.html and el/index.html from index.html + i18n.json.

index.html is both the published English page and the template. Edit English
there, then run this. Nothing writes back to index.html.

Translation strings come from i18n.json, which is extracted from CV-el.md and
CV-sv.md by extract-i18n.py, plus site-i18n.json for the portfolio homepage.
"""

import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LANGS = ('sv', 'el')

PDF = {'en': 'Ioannis-Koupidis-CV.pdf',
       'sv': 'Ioannis-Koupidis-CV-sv.pdf',
       'el': 'Ioannis-Koupidis-CV-el.pdf'}

# Relative hrefs differ per language because each page sits at a different depth.
HREFS = {'en': ('./', 'sv/', 'el/'),
         'sv': ('../', './', '../el/'),
         'el': ('../', '../sv/', './')}

METADATA = {
    'en': {
        'description': 'Founder and Product Manager student at Hyper Island with thirteen years of experience building and running complex services in Swedish healthcare.',
        'title': 'Ioannis Koupidis · Product Manager',
        'url': 'https://ioanniskp.github.io/CV-neo/',
        'locale': 'en_SE',
    },
    'sv': {
        'description': 'Grundare och student på programmet Product Manager vid Hyper Island, med tretton års erfarenhet av att bygga och driva komplexa tjänster inom svensk vård.',
        'title': 'Ioannis Koupidis · Product Manager',
        'url': 'https://ioanniskp.github.io/CV-neo/sv/',
        'locale': 'sv_SE',
    },
    'el': {
        'description': 'Ιδρυτής και σπουδαστής στο πρόγραμμα Product Manager του Hyper Island, με δεκατρία χρόνια εμπειρίας στη δημιουργία και λειτουργία πολύπλοκων υπηρεσιών στη σουηδική υγεία.',
        'title': 'Ioannis Koupidis · Product Manager',
        'url': 'https://ioanniskp.github.io/CV-neo/el/',
        'locale': 'el_GR',
    },
}

FONTS_EL = ('<link href="https://fonts.googleapis.com/css2?'
            'family=Literata:ital,opsz,wght@0,7..72,200..900;1,7..72,200..900'
            '&family=IBM+Plex+Mono:wght@400;500'
            '&family=Inter:wght@400;500;600'
            '&family=Noto+Sans+Mono:wght@400;500&display=swap" rel="stylesheet">')

# Fraunces and IBM Plex Mono have no Greek glyphs. Verified against Google
# Fonts: neither ships a greek subset, while Inter and Literata both do.
STYLE_EL = """
<style>
  /* Fraunces and IBM Plex Mono do not include Greek glyphs. */
  .hero-title,.case-title,.section-title,.case-section h2,.statement,
  .project-info h3,.experience-card h3,.metric strong,.footer-title{
    font-family:'Literata',Georgia,serif;
    font-optical-sizing:auto;
    font-weight:460;
  }
  .brand,.primary-nav a,.header-tools,.timeline-label,.eyebrow,.project-kicker,
  .text-link,.language-switch,.experience-card>.metric-note,.capabilities-list{
    font-family:'Noto Sans Mono',ui-monospace,monospace;
  }
  @media print{
    body{font-size:8.5pt;line-height:1.23}
    .hero-title{font-size:20.5pt}
    .hero-support{font-size:9.2pt}
    .section-title,.statement{font-size:15pt}
    .project-card,.principle,.experience-card{padding:1.8mm 0}
    .experience-card>.metric-note{font-size:6.6pt;line-height:1.2}
    .compact-list{font-size:8.2pt}
  }
</style>
"""


def langs_block(lang):
    en, sv, el = HREFS[lang]
    def a(code, href, hreflang):
        cur = ' aria-current="page"' if code.lower() == lang else ''
        return f'<a href="{href}" hreflang="{hreflang}"{cur}>{code}</a>'
    sep = '<span class="sep" aria-hidden="true">/</span>'
    return a('EN', en, 'en') + sep + a('SV', sv, 'sv') + sep + a('EL', el, 'el')


def translate_text_nodes(src, table, lang):
    """Replace whole text nodes whose trimmed content matches a known string.

    Whole-node matching only: a partial match would corrupt strings that happen
    to contain a shorter one.
    """
    parts = re.split(r'(<[^>]+>)', src)
    hits = 0
    for i, part in enumerate(parts):
        if part.startswith('<') or not part.strip():
            continue
        stripped = part.strip()
        key = html.unescape(stripped)
        entry = table.get(key)
        if entry and entry.get(lang):
            parts[i] = part.replace(stripped, html.escape(entry[lang], quote=False), 1)
            hits += 1
    return ''.join(parts), hits


def build(lang, table):
    src = open(os.path.join(HERE, 'index.html'), encoding='utf-8').read()

    out, hits = translate_text_nodes(src, table, lang)

    # language switcher
    out = re.sub(r'<!--LANGS-->.*?<!--/LANGS-->',
                 lambda m: '<!--LANGS-->' + langs_block(lang) + '<!--/LANGS-->',
                 out, flags=re.S)

    out = out.replace('<html lang="en">', '<html lang="%s">' % lang)
    out = out.replace('href="%s"' % PDF['en'], 'href="%s"' % PDF[lang])
    out = out.replace('href="assets/', 'href="../assets/')
    out = out.replace('src="assets/', 'src="../assets/')
    out = out.replace('href="projects/', 'href="../projects/')

    # Metadata lives in attributes, so the whole text node translation pass
    # cannot reach it. Replace only the known English values in known tags.
    base_meta = METADATA['en']
    lang_meta = METADATA[lang]
    metadata_tags = (
        ('<meta name="description" content="{}">', 'description'),
        ('<link rel="canonical" href="{}">', 'url'),
        ('<meta property="og:title" content="{}">', 'title'),
        ('<meta property="og:description" content="{}">', 'description'),
        ('<meta property="og:url" content="{}">', 'url'),
        ('<meta property="og:locale" content="{}">', 'locale'),
        ('<meta name="twitter:title" content="{}">', 'title'),
        ('<meta name="twitter:description" content="{}">', 'description'),
    )
    for tag, key in metadata_tags:
        out = out.replace(tag.format(base_meta[key]),
                          tag.format(lang_meta[key]))

    if lang == 'el':
        out = re.sub(r'<link href="https://fonts\.googleapis\.com/css2\?[^"]*" rel="stylesheet">',
                     FONTS_EL, out)
        out = out.replace('</head>', STYLE_EL + '</head>')
    d = os.path.join(HERE, lang)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(out)
    return hits


def main():
    table = json.load(open(os.path.join(HERE, 'i18n.json'), encoding='utf-8'))
    site_table = json.load(open(os.path.join(HERE, 'site-i18n.json'), encoding='utf-8'))
    table.update(site_table)

    total = len(table)
    for lang in LANGS:
        hits = build(lang, table)
        print('%s/index.html  %d strings replaced (of %d known)' % (lang, hits, total))
    print('English page untouched.')


if __name__ == '__main__':
    sys.exit(main())
