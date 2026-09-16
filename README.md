# Thompson–Dubberly layout

A coding-agent skill that lays out prose as Thompson sense-lines on a Dubberly-style wide column sheet and returns **one SVG** and a matching **PDF**.

The process is [SKILL.md](SKILL.md). Typographic rules are [layout.md](layout.md). Page, type, and SVG rules are [format.md](format.md). The packer is [build_sheet.py](build_sheet.py).

## Do other people need another folder?

No, if they clone this repo and tell the agent to follow `SKILL.md`. Keep the files together: the skill, `layout.md`, `format.md`, `build_sheet.py`, and `Boundary_Objects.pdf`.

Yes, if they want the agent to **discover** the skill without being told:

- Cursor project skill: copy the skill files into `.cursor/skills/thompson-dubberly-layout/`
- Cursor personal skill (all projects): `~/.cursor/skills/thompson-dubberly-layout/`
- Other agents: their own skills directory, same contents, or `@SKILL.md` in the prompt

Do not put only `SKILL.md` in that folder. The agent must still read the sibling files from this repo.

## Use with a coding agent

1. Give the agent this directory (clone, or point it at the skill files).
2. Give it a source (PDF, URL, or pasted text).
3. Ask it to use this skill to lay out the text, e.g. `Use thompson-dubberly-layout on this paper.`
4. Take the SVG and PDF it writes.

Python 3 and PyMuPDF (`pip install pymupdf`) for packing and PDF.

Column density: `Boundary_Objects.pdf`.

## Input

Any source the agent can read: PDF, web page, or already-clean text.

The agent produces two intermediates (skip clean if the source is already clean):

| File | What it is |
| --- | --- |
| `name_clean.txt` | Recoverable article: heads, body, figure callouts, lists, quotes. No OCR debris, page furniture, or bibliography. Inline `[n]` kept. Paragraphs intact, not yet lined. |
| `name_lines.txt` | One file line = one line of type. Markers: `=title`, `=authors`, `=journal`, `=column`, `=section`, `=subsection`, `=quote`, `=quoteattr`, `=list`, `=figure`, `*italic*`, `[n]`. |

## Output

| File | What it is |
| --- | --- |
| `name.svg` | One sheet: computed width × height in points |
| `name.pdf` | That drawing, one page, same point size |

Returned document = main text + figures in the flow. No bibliography. Inline reference numbers stay as 7 pt superscripts. Type is 12 pt. No line longer than 324 pt.
