# sense-lining

![Licklider sheet](licklider.png)

A coding agent skill.

It lays out prose as Bradbury Thompson sense-lines 

on a Hugh Dubberly-style wide column sheet.


Returns an **SVG** and a matching **PDF**.


Expect this skill to take 10 minutes to process an average-length academic paper.

Many figures and images, or a lack of machine-readable text, can increase processing time.

## Use with a coding agent

1. Give the agent this directory (the repo URL, or download it).
2. Give it a source text. A PDF is fine.
3. Ask it to use this skill to lay out the text.

## Input

Any source the agent can read: PDF, web page, or already-clean text.

If a PDF has no machine-readable text, 

the agent will suggest options for creating a machine-readable text layer.

The agent produces two intermediates:

(It skips name_clean.txt if the source is already clean)

| File | What it is |
| --- | --- |
| `name_clean.txt` | Recoverable article: heads, body, figure callouts, lists, quotes. No OCR debris, page furniture, or bibliography. Inline `[n]` kept. Paragraphs intact, not yet lined. |
| `name_lines.txt` | One file line = one line of type. Markers: `=title`, `=subtitle`, `=authors`, `=journal`, `=abstract`, `=column`, `=section`, `=subsection`, `=quote`, `=quoteattr`, `=list`, `=figure`, `*italic*`, `[n]`. |

## Output

| File | What it is |
| --- | --- |
| `name.svg` | One sheet: computed width × height in points |
| `name.pdf` | That drawing, one page, same point size |


Returned document = main text + figures in the flow. No bibliography.

Inline reference numbers stay as 7 pt superscripts. Type is 12 pt. No line longer than 324 pt.
