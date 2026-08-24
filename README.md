# CV neo

A CV on a single page, static, with no framework and no build dependencies beyond Python
and Chrome. Published on GitHub Pages in three languages:

| | Page | PDF |
|---|---|---|
| English | `/` | `Ioannis-Koupidis-CV.pdf` |
| Swedish | `/sv/` | `sv/Ioannis-Koupidis-CV-sv.pdf` |
| Greek | `/el/` | `el/Ioannis-Koupidis-CV-el.pdf` |

## Editing

`index.html` is both the English homepage and the template for the other two
languages. Shared styling and interactions live in `assets/site.css` and
`assets/site.js`.

The English project case studies live in `projects/agent-x/`,
`projects/scribe/`, and `projects/radio/`. Their screenshots are stored under
`assets/images/`.

**Edit English in `index.html`, then run:**

```
./make-pdf.command
```

That regenerates `sv/index.html` and `el/index.html` from the translation
tables, then prints all three PDFs. Skipping it leaves the translations and
every PDF stale.

`sv/` and `el/` are generated. Editing them by hand is pointless. The next
build overwrites your changes.

## Translations

`CV-el.md` and `CV-sv.md` remain the readable record for the original CV
copy. `i18n.json` contains those strings; `site-i18n.json` contains the new
portfolio homepage copy. `build.py` merges both when creating the Swedish and
Greek pages.

For original CV strings, edit the `.md` record and regenerate `i18n.json` with
`python3 extract-i18n.py`. For homepage strings, edit `site-i18n.json`
directly. Then run `./make-pdf.command`.

## Notes

Greek uses different typefaces because Fraunces and IBM Plex Mono ship no Greek
glyphs: the build substitutes EB Garamond and Noto Sans Mono for that language
only.

The sphere cursor and scroll reveals are progressive enhancements. The cursor
only activates for precise desktop pointers and is disabled when reduced motion
is requested. Project cards and language links remain ordinary links without
JavaScript.
