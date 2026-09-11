---
name: thompson-dubberly-layout
description: Lays out prose as Thompson sense-lines on a Dubberly-style wide column sheet and returns one SVG plus a matching PDF. Use when laying out a paper, article, or other text typographically.
---

# Thompson–Dubberly layout

Read [layout.md](layout.md) and [format.md](format.md) in full before you start. Those files are the rules. This file is the process.

Sense-breaking is yours. Measuring widths, packing columns, placing figures at their measured size, emitting SVG, and making the PDF may be code.

Default library: PyMuPDF. Use it for PDF text, figure clips, width measurement (`Font("times-roman")` / `times-italic` / `times-bold`), and SVG → PDF (`open(stream=svg, filetype="svg").convert_to_pdf()`). Measure with that face so the PDF matches the SVG.

## Steps

1. **Read the rules.** layout.md, then format.md, in full.
   Done when both files have been read.

2. **Clean source.** Extract to a paragraph file: heads, body, figure callouts, lists, quotes. Rejoin hyphenation. Strip page furniture. Drop the bibliography; keep inline reference numbers. If the source is already clean, skip this. A text layer is not the same as clean text. Note every cleanup.
   Done when a reader of the clean file can recover the article without OCR debris or reprint wrappers.

3. **Hangline and columns.** Decide whether an abstract column exists, what the masthead is, and where sections split. Set the hangline from the masthead as format.md states.
   Done when every column has a role and the hangline is a number.

4. **Sense lines.** Break for sense per layout.md. A width helper may propose breaks at the pause points; you still own every line. Fix any line over 324 pt and any one-word line.
   Done when no line overruns the measure and no line is a single word without a reason.

5. **Figures.** At each callout, place in the text flow at the source size ratio in format.md. If the source is a PDF, clip the printed bbox from the page pixmap, not from raw image xrefs. If there is no printed size, leave the figure at its native size relative to the type. If the drawing cannot be recovered, the omit line in format.md.
   Done when every callout is either a sized image in flow or an omit line.

6. **Pack and emit.** Consecutive columns, shared depth per format.md. One SVG; PDF is that drawing at the same point size.
   Done when the SVG’s width and height are the computed sheet size and the PDF is one page of those dimensions.

7. **Check.**
   - No line longer than 324 pt at 12 pt.
   - Section titles (and Abstract, if any) one line above the hangline; title-column hangline − 14 empty.
   - Columns consecutive; no empty slot.
   - Figures not stretched to a slot width.
   - Bibliography absent; inline cues kept as 7 pt superscripts.
   - PDF type is 12 pt (7 pt on cues).
