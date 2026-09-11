#!/usr/bin/env bash
set -e

echo "=== Building Mastering Antigravity Book ==="

echo "[1/2] Compiling LaTeX to PDF..."
pdflatex -interaction=nonstopmode mastering_antigravity.tex > /dev/null
pdflatex -interaction=nonstopmode mastering_antigravity.tex > /dev/null
echo "✓ Generated mastering_antigravity.pdf ($(du -h mastering_antigravity.pdf | cut -f1))"

echo "[2/2] Compiling EPUB with Pandoc..."
pandoc -s -o mastering_antigravity.epub \
  --epub-cover-image=images/cover.jpg \
  --css=epub_style.css \
  --toc --toc-depth=2 \
  book.md
echo "✓ Generated mastering_antigravity.epub ($(du -h mastering_antigravity.epub | cut -f1))"

echo "=== Build Complete! ==="
ls -lh mastering_antigravity.pdf mastering_antigravity.epub
