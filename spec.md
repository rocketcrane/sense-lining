# Spec

Runtime typographic rules live in [layout.md](layout.md). Page, type, and SVG rules live in [format.md](format.md). Process lives in [SKILL.md](SKILL.md); it should not restate those rules.

## User journey

1. **Have text.** The user has text(s) they want to lay out typographically.
2. **Put skill into agent.** They put this skill into a coding agent.
3. **Ask to lay out.** They ask the coding agent to use this skill to lay out the text.
4. **Get SVG and PDF.** The coding agent returns an SVG and a PDF with the text laid out. The returned document is the main text and any figures inside the text. No need for the references, though the agent keeps any inline reference numbers or text.



## Persona

- **Me.** This is a prototype, used by myself.
- **Friends.** And by some of my friends to start, likely to lay out academic papers initially.



## User objects

- **Source texts.** The user has text(s) as a source. These could be any format, likely web links to text, PDFs, or raw pasted text.
- **Converted SVG and PDF.** The user then encounters the converted SVG and PDF versions of the text.



## Technical objects

- **PDF text extraction.** Efficient, effective way to get text out of PDFs that have no OCR text. May involve an OCR system, or reading the PDF with the visual part of the agent model.
- **OCR cleanup.** Further processing of extracted text, since PDF OCR text is often riddled with errors. Skip this when the given text is already clean.
- **Semantic layout.** The agent decides the sense line-breaks, what is a section, whether a passage is a list or a quote, and where a figure is called out, by applying [layout.md](layout.md). Measuring widths, packing columns, placing figures at their measured size, emitting SVG, and making the PDF may be code.
- **Output format rules.** Specified in [format.md](format.md).
- **Libraries.** PyMuPDF is the default; see [SKILL.md](SKILL.md).

