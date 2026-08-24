#!/bin/zsh
# Double-click to rebuild the translated pages and all three PDFs.
#
# index.html is the English page and the template. build.py generates
# sv/index.html and el/index.html from it plus i18n.json. Each page is then
# printed to a PDF sitting beside it, which is what its Download link points to.
cd "$(dirname "$0")"

chrome="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

if [[ ! -x "$chrome" ]]; then
  echo "Google Chrome not found in /Applications. Cannot generate PDFs."
  exit 1
fi

python3 build.py || { echo "build.py failed; PDFs not regenerated."; exit 1; }

pdf() {  # pdf <source html> <output pdf>
  "$chrome" --headless=new --disable-gpu --no-pdf-header-footer \
    --virtual-time-budget=20000 --print-to-pdf="$2" "file://$PWD/$1" 2>/dev/null \
    && echo "  $2"
}

echo "Generating PDFs:"
pdf "index.html"    "Ioannis-Koupidis-CV.pdf"       || exit 1
pdf "sv/index.html" "sv/Ioannis-Koupidis-CV-sv.pdf" || exit 1
pdf "el/index.html" "el/Ioannis-Koupidis-CV-el.pdf" || exit 1

echo "Done."
