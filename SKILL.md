---
name: thompson-dubberly-layout
description: Lays out prose as Thompson sense-lines on a Dubberly-style wide column sheet and returns one SVG plus a matching PDF. Use when laying out a paper, article, or other text typographically.
---

# Thompson–Dubberly layout

Read [layout.md](layout.md) and [format.md](format.md) in full before you start. Those files are the rules. This file is the process.

You read the clean text and write a sense-lined file. Measuring those lines, packing the declared columns, placing figures at their measured size, emitting SVG, and making the PDF may be code. [build_sheet.py](build_sheet.py) places each line and each column as written.

Default library: PyMuPDF. Use it for PDF text, figure clips, width measurement (`Font("times-roman")` / `times-italic` / `times-bold`), and SVG → PDF (`open(stream=svg, filetype="svg").convert_to_pdf()`). Measure with that face so the PDF matches the SVG.

## Steps

1. **Look.** layout.md, then format.md, in full. Then [Boundary_Objects.pdf](Boundary_Objects.pdf) for column density.
   Done when those files have been read.

2. **Clean source.** Extract to `name_clean.txt`: heads, body, figure callouts, lists, quotes. Rejoin hyphenation. Strip page furniture. Drop the bibliography; keep inline reference numbers. If the source is already clean, skip this. A text layer is not the same as clean text. Note every cleanup. Leave paragraphs intact; this file is not yet lined.
   Done when a reader of the clean file can recover the article without OCR debris or reprint wrappers.

3. **Hangline.** Decide whether an abstract column exists and what the masthead is. Set the hangline from the masthead as format.md states.
   Done when the hangline is a number.

4. **Sense lines and columns.** Read the clean file through. Write `name_lines.txt`. One line in that file is one line of type. Break where a reader pauses, per layout.md. Measure a drafted line only to see whether it fits 324 pt at the indent it will have; if it does not, rewrite it. Markers: `=title`, `=authors`, `=journal`, `=column`, `=section`, `=subsection`, `=quote`, `=quoteattr`, `=list`, `=figure`, `*italic*`, `[n]`. Fill one column at a time. Start a column when a hangline heading begins, or when this column is already deep and the next paragraph is a good break. Asides, quotes, lists, and figures stay in the current column (`=subsection` in the flow).
   Done when `name_lines.txt` exists, every body line in it is a line you wrote, and `=column` is infrequent — teens of columns on a tall sheet, not a new column every few lines.

5. **Figures.** At each callout, place in the text flow at the source size ratio in format.md. If the source is a PDF, clip the printed bbox from the page pixmap, not from raw image xrefs. If there is no printed size, leave the figure at its native size relative to the type. If the drawing cannot be recovered, the omit line in format.md.
   Done when every callout is either a sized image in flow or an omit line.

6. **Pack and emit.** `python3 build_sheet.py name`. One SVG; PDF is that drawing at the same point size.
   Done when the SVG’s width and height are the computed sheet size and the PDF is one page of those dimensions.

7. **Check.**
   - Every body line on the sheet is a line from `name_lines.txt`; every column on the sheet is a `=column` in that file.
   - Teens of columns on a tall sheet (on the order of [Boundary_Objects.pdf](Boundary_Objects.pdf), ~2000–2700 pt high), not thirty columns on a 900 pt strip.
   - No line longer than 324 pt at 12 pt.
   - Section titles (and Abstract, if any) one line above the hangline; title-column hangline − 14 empty.
   - Columns consecutive; no empty slot.
   - Figures not stretched to a slot width.
   - Bibliography absent; inline cues kept as 7 pt superscripts.
   - PDF type is 12 pt (7 pt on cues).
