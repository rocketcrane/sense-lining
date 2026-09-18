---
name: sense-lining
description: Lays out prose as Thompson sense-lines on a Dubberly-style wide column sheet and returns one SVG plus a matching PDF. Use when laying out a paper, article, or other text typographically.
---

# sense-lining

Read [layout.md](layout.md) and [format.md](format.md) in full before you start. Those files are the rules. This file is the process.

You read the clean text and write a sense-lined file. Measuring those lines, packing the declared columns, placing figures at their measured size, emitting SVG, and making the PDF may be code. [build_sheet.py](build_sheet.py) places each line and each column as written.

Default library: PyMuPDF. Use it for PDF text, figure clips, width measurement (`Font("times-roman")` / `times-italic` / `times-bold`), and SVG → PDF (`open(stream=svg, filetype="svg").convert_to_pdf()`). Measure with that face so the PDF matches the SVG.

## Steps

1. **Look.** layout.md, then format.md, in full.
   Done when those files have been read.

2. **Text layer.** If the source is not a PDF, skip this. If it is, extract with PyMuPDF `page.get_text()`. If `get_text()` is empty on the pages, stop. Present the options below; wait. Do not clean, line, or pack.
   - On macOS: tell the user to open the PDF in Preview, choose File > Export, check Embed Text, save, and return that PDF.
   - Otherwise: OCRmyPDF is a well-known open-source tool that adds a text layer. It needs an install and takes a little longer. Offer it if the OS supports it.
   - If neither is available: you can read the page rasters. Say that this is not recommended: token-heavy and slow.
   Done when `get_text()` returns the article, or the run has stopped with those options.

3. **Clean source.** Extract to `name_clean.txt`: heads, body, figure callouts, lists, quotes. Rejoin hyphenation. Strip page furniture. Drop the bibliography; keep inline reference numbers. If the source is already clean, skip this. A text layer is not the same as clean text. Note every cleanup. Leave paragraphs intact; this file is not yet lined.
   Done when a reader of the clean file can recover the article without OCR debris or reprint wrappers.

4. **Hangline.** Decide whether an abstract column exists and what the masthead is. Set the hangline from the masthead as format.md states.
   Done when the hangline is a number.

5. **Sense lines and columns.** Read the clean file through. Write `name_lines.txt`. One line in that file is one line of type. Break where a reader pauses, per layout.md. Measure a drafted line only to see whether it fits 324 pt at the indent it will have; if it does not, rewrite it. Markers: `=title`, `=subtitle`, `=authors`, `=journal`, `=abstract`, `=column`, `=section`, `=aside`, `=subsection`, `=quote`, `=quoteattr`, `=list`, `=figure`, `*italic*`, `[n]`. Fill one column at a time. An abstract is its own leftmost column: `=abstract`, then its body (the packer sets it italic). Do not use `=section Abstract`. Masthead markers (`=title`, `=subtitle`, `=authors`, `=journal` as the piece has them) go in the title column; they do not need a `=column` before them. Start a further column when a named head in the source begins (`=column`, then `=section` for a major unit or `=aside` for a named part), or when this column is already deep and the next paragraph is a good break. Quotes, lists, and figures stay in the current column. `=subsection` only for a true subordinate that would leave a stub column.
   Done when `name_lines.txt` exists, every body line in it is a line you wrote, and each named head in the source has a column (plus overflow as needed).

6. **Figures.** At each callout, place in the text flow at the source size ratio in format.md. If the source is a PDF, clip the printed bbox from the page pixmap, not from raw image xrefs. Write the display size (printed × 12 / source body size) on the marker: `=figure 1 mental.png 376.5 162.6`. If there is no printed size, leave the size off; the packer uses the image’s native size. If the drawing cannot be recovered, omit the filename (the omit line in format.md).
   Done when every callout is either a sized image in flow or an omit line.

7. **Pack and emit.** `python3 build_sheet.py name` reads `name_lines.txt` and writes `name.svg` and `name.pdf`. One SVG; PDF is that drawing at the same point size.
   Done when the SVG’s width and height are the computed sheet size and the PDF is one page of those dimensions.

8. **Check.**
   - Every body line on the sheet is a line from `name_lines.txt`; every column on the sheet is a `=column` in that file, except the abstract column from `=abstract`.
   - Columns follow headed units in the source, plus overflow. Fill toward ~100 lines / ~2000–2700 pt high; do not hide named heads mid-column to keep the count small. Not thirty columns on a 900 pt strip.
   - No line longer than 324 pt at 12 pt.
   - Hangline titles (section, named part, Abstract) one line above the hangline; title-column hangline − 14 empty. Abstract is leftmost; title column is next.
   - Columns consecutive; no empty slot.
   - Figures not stretched to a slot width.
   - Bibliography absent; inline cues kept as 7 pt superscripts.
   - PDF type is 12 pt (7 pt on cues).
