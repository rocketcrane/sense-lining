# Format

Line breaks and contrast are in [layout.md](layout.md). This file is the page: grid, type, SVG.

Apply every rule.

## Sheet

- One wide sheet of columns, left to right. Not a stack of letter pages.
- How many columns, and how large the sheet is, follow the text.
- Width: last type-right or last figure-right, plus 48 pt. On a rigid 350 pt stride that is `48 + 350(N − 1) + 324 + 48`. Gutters may stretch (see Figures); then the sheet is wider than that formula.
- Height: deepest baseline plus 48 pt.
- The 48 pt margin is measured to baselines, not to ink. The first masthead baseline is `y = 48`. Ascenders may sit in the top margin; descenders of the last line may sit in the bottom margin.
- Ground: white `#ffffff`. Type: `#111111`.
- No column rules, boxes, page numbers, or running headers.
- Main text and figures only. Leave the bibliography off. Keep inline reference numbers.



## Type

- Family: `Times New Roman, Times, serif`.
- Size: 12 pt on 14 pt leading. One size except footnote cues.
- Flush left, ragged right. Every line in a column shares that column's x.
- No line longer than 324 pt (27 picas). If a title overruns, break it and expand upward.
- y is a baseline. Consecutive lines are 14 pt apart. A blank line is 14 pt. Paragraphs are separated by one blank line.



## Hangline

All columns share one hangline: the first body baseline.

Set it from what actually sits above the body. Lay out the masthead (title, subtitle, authors, journal, whatever the piece has) from the top of the title column. The hangline is one blank line below that masthead: last masthead baseline + 28 pt. If a section title, expanding upward, would hit the top margin, drop the hangline until it fits.

Section titles sit one line above the hangline (hangline − 14 pt). Extra title lines expand upward. Body starts on the hangline. In the title column the hangline − 14 slot is empty; in other columns the section title occupies it.

## Columns

As many as the text needs. `x = 48 + 350n` for n = 0, 1, 2, … from the left is the minimum stride. Columns are consecutive: do not skip an n.

Reading order: left to right across columns, top to bottom within a column.

- If there is an abstract, it gets its own column (leftmost). Bold label `Abstract` one line above the hangline. Body italic, on the hangline. If there is no abstract, do not leave an empty column for one.
- Next, the title column: document title, subtitle, authors, journal as the piece has them, then first body on the hangline.
- Then further columns left to right.

Fill a column down the sheet. Start the next column when a new headed unit begins — a major section, or a named parallel part — or when this column is already deep and the next paragraph is a good break. A continuation has no repeated title; hangline − 14 is empty, like the title column.

A headed column gets its title one line above the hangline (bold for a major section, italic for a named part). Extra title lines expand upward. Body starts on the hangline. In the title column the hangline − 14 slot is empty.

A named parallel part is a source title the reader would look up (Means-Ends Analysis, Schemes for Guiding Search). Same-weight heads in the source are hangline parts even if the outline looks nested. Source heading level is not layout level.

Pull quotes, lists, figures, and epigraphs stay in the flow of the current column. Mid-column italic (`=subsection`) is the exception: a head that only makes sense under this column’s title, or a short labeled beat that would leave a stub column.

The sheet is tall. Bottoms may be ragged. The title column’s last baseline is not a depth cap; a short column is not padded. A full column is on the order of a hundred lines from the hangline. Column count follows the headed units.

### Title styles

- Document title, first line: bold roman. Subtitle: roman.
- Authors: roman. Journal / publication: italic.
- Abstract label: bold. Abstract body: italic.
- Major / top-level section: bold roman.
- Named parallel part: italic, hangline.
- Subsection (true subordinate, mid-column): italic, not bold.
- If a parent heading and its first child share a column, stack them above the hangline (parent above child). Extra lines expand up.



## Indents

Offsets from the column's x:


| Role                                     | x           |
| ---------------------------------------- | ----------- |
| Block quote (italic)                     | column + 28 |
| List marker line (dash or number)        | column + 28 |
| Wrapped dash-list line                   | column + 35 |
| Numbered-list body after the number line | column + 40 |


Quotes of more than one line are block quotes. A quote attribution, when present, stays italic and indented with the quote.

## In-line marks

Citation numbers stay in the line as superscripts:

```xml
<tspan font-size="7" dy="-4">12</tspan><tspan dy="4"></tspan>
```

A word of emphasis, an introduced term, or the title of a work is an italic span:

```xml
<tspan font-style="italic">creatively</tspan>
```

A small set of contrasting terms may be bold spans. Rare.

## Figures

Place a figure in the column where the text calls it out, in the text flow: top at the current grid line (the hangline if that column’s body has not started), x at the column left. Consecutive figures stack. Do not send a mid-column callout back up to the hangline or open an empty column pair for it.

Keep the original size relative to the type. If the source is a PDF, measure the printed figure and the body size; display size = printed size × (12 / source body size). Do not stretch every figure to a fixed width. Two column slots are 674 pt (`350 + 324`). A figure that wide spans two slots; a smaller one stays smaller.

Caption under the image, italic, at the column x, one grid step below the image. Type must not run through a figure. If a figure only covers part of a neighboring column’s height, type may sit above and below that band. Do not leave an empty column slot for a figure that is narrower than two column slots.

The 350 pt stride is a minimum. If a figure is wider than 324 pt but its jut into the next column’s type is under about a quarter of 324 pt, start that next column at the figure’s right edge plus 26 pt (the usual gutter) and keep later columns at least 350 pt apart. Type in the neighbor then runs full depth. If the jut is a quarter of the measure or more, the figure occupies that column: type skips the y-band it covers.

If the figure cannot be drawn, one line of roman body type in that column:

```
FIGURE 1 [diagram omitted]
```



## SVG

One file. `width` and `height` are the computed sheet size.

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="WIDTH" height="HEIGHT" viewBox="0 0 WIDTH HEIGHT">
  <rect width="WIDTH" height="HEIGHT" fill="#ffffff"/>
  <g font-family="Times New Roman, Times, serif" font-size="12" fill="#111111">
    <text x="48.0" y="Y" font-weight="bold">Section title</text>
    <text x="48.0" y="HANGLINE">First line of body.</text>
  </g>
</svg>
```

- Each line of type is its own `<text>` element.
- Figures are `<image>` elements in the same file (a data URI is fine).
- Put `font-weight="bold"` and `font-style="italic"` on the `<text>` when the whole line is bold or italic. Use `<tspan>` when only part of the line is.
- XML-escape `&`, `<`, and `>`.
- Keep the source's quotation marks and dashes (curly quotes, en dashes for ranges).

The PDF is this same drawing at this same point size.