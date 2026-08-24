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

FONTS_EL = ('<link href="https://fonts.googleapis.com/css2?'
            'family=EB+Garamond:ital,wght@0,400..800;1,400..800'
            '&family=IBM+Plex+Mono:wght@400;500'
            '&family=Inter:wght@400;500;600'
            '&family=Noto+Sans+Mono:wght@400;500&display=swap" rel="stylesheet">')

# Fraunces and IBM Plex Mono have no Greek glyphs. Verified against Google
# Fonts: neither ships a greek subset, while Inter and EB Garamond both do.
# EB Garamond draws lighter than Fraunces, so weights are lifted to hold a
# comparable ink density.
STYLE_EL = """
<style>
  /* Fraunces and IBM Plex Mono do not include Greek glyphs. */
  .hero-copy h1,.case-title,.section-title,.case-section h2,.statement,
  .project-info h3,.experience-card h3,.footer-title{
    font-family:'EB Garamond',Georgia,serif;
    font-weight:540;
  }
  .brand,.primary-nav a,.header-tools,.timeline-label,.eyebrow,.project-kicker,
  .text-link,.language-switch{
    font-family:'Noto Sans Mono',ui-monospace,monospace;
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


def alternates(lang):
    en, sv, el = HREFS[lang]
    return ('\n<link rel="alternate" hreflang="en" href="%s">'
            '\n<link rel="alternate" hreflang="sv" href="%s">'
            '\n<link rel="alternate" hreflang="el" href="%s">' % (en, sv, el))


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

    if lang == 'el':
        out = re.sub(r'<link href="https://fonts\.googleapis\.com/css2\?[^"]*" rel="stylesheet">',
                     FONTS_EL, out)
        out = out.replace('</head>', STYLE_EL + '</head>')
    out = out.replace('</head>', alternates(lang) + '\n</head>')

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
