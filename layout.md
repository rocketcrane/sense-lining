# How to lay out text typographically

Read this in full before laying out any text. Apply every rule that bears on the piece.

## Contrast: the fundamental operation in typography

The basic rule is that we can measure the "fitness" of a piece of typography by the degree of congruence of its visual structure with its semantic structure — that is, by the fitness of the typographer's form with the author's content.

The visual structure of a 2D image derives from the operation of contrast — the separation of a visual element (or set of elements) from another element (or other set of elements) by means of a visual distinction (a visible difference). Psychology has named the result the "pop-out effect." For example, a yellow flower pops-out from a green field of leaves.

While the operation of contrast separates one set of letters from another, it simultaneously groups the letters within each set, too. So: the operation of contrast at once both divides and connects.

The first basic contrast is between foreground and background, also described as figure-ground or form-counterform or positive-negative. For example, text separates from its substrate, i.e., black letters contrast with a white page or screen, etc. The degree of contrast matters, too, e.g. see accessibility standards.

Within a line of text, all the letters contrast with the background and form a group (the line) by similarity of size, form, and alignment. Some letters are separated and grouped into words by addition of spaces. And a small set of letters may also contrast with the rest, e.g.,

> Now is not the time.
>
> Now is not the time.
>
> Now is *not* the time.
>
> Now is **not** the time.
>
> Now is NOT the time.
>
> Now is not the time.
>
> Now is not the time.
>
> Now is not the time.

Contrasts might pile up (though that tends to make a bit of a circus), e.g.,

> Now is ***NOT*** the time.

The structures of all the examples above are isomorphic; i.e., in each line, the word (set of letters) "not" pops-out by virtue of contrasting with the remaining letters in the line. And the lines separate from each other by both alignment and distance; and the letters separate from the ground by contrast of value (darkness). (The degree of pop-out differs somewhat, mainly with color value and boldness, but the degree does not matter much, until the composition includes other elements.)

In typography, contrast has three main sources:

- the form (shape + color) of the letters in blocks of text
e.g., Roman and Italic letters form separate groups, likewise regular and bold, black and red, larger and smaller. Moving and blinking can be a type of contrast, too.
- the spatial arrangement of blocks of text
e.g., near and far letters form separate groups and aligned letters also connect (e.g., baseline aligned or flush-left lines). A simple word space is enough to form groups.
- and ancillary marks, such as backgrounds, rules (lines), asterisks, etc., which link or separate blocks of text.

Our perceptual system "parses" a 2D field according to contrasts, separating and grouping elements into sets and sub-sets and sub-sub-sets, etc. These nested sets form a tree or a graph or a muddle. We can compare the type's structure (form) with the text's structure (content). Ideally, the type's structure reinforces the text's structure — rather than contradicting or obscuring it.

In practice, both the form and the content may be ambiguous or contradictory. That is, blocks of text might be in overlapping sets, for example, PL**AY SO**CCER, which can read as both "PLAY SOCCER" and "AYSO" (for American Youth Soccer Organization). E**ART**H is a similar double reading; "earth without art is just 'eh'." These examples take advantage of ambiguity to play with the words and amuse the reader. That's a good case. More often, contradictions confuse and distract readers.

The education of a typographer is learning to use contrast, paying attention to details (to small contrasts), and then avoiding (or removing) accidental (unwanted) contrasts.

Based on these principles, we might create a machine (or algorithm) that can create typography — or at least respectably complete Emil Ruder's exercises.

However, a first step might be to create a machine that can lay out text sensibly, that is, according to the structure of the content.

## Breaking lines of text for sense

In 1979, Bradbury Thompson published the Washburn College Bible, a lectern version of the King James Bible, meant for reading passages aloud during a church service. In order to facilitate the reading process, Thompson broke each line of text for sense — by hand — in each of ~1,800 pages, with 2 columns per page, and ~50 lines per column, a total of perhaps 180,000 lines.

Subsequently, he published a smaller, home edition. All the text is the same font, same size, same color: Sabon Antiqua (a modern version of Garamond) regular, 11 point body on 12.5 points of leading, black, flush left, ragged right. Lines are up to 50 characters in length (< 36 picas or 432 points). Italics are used for the names of the books and folios, but not in the text. And the words LORD, LORD GOD, JEHOVAH, and God's words to Moses, I AM THAT I AM and I AM, appear with an initial cap followed by small-caps. Chapters are separated by a line break. (Some verses are separated by a line break, though others are not; the pattern is unclear.) Each column starts with a new chapter or verse; chapters may run over, but not verses.

Thompson's rules for breaking lines were never published. The goal, as he explained, was to break each line where a reader might pause — i.e., at the end of a clause or thought.

Similarly, semantic chunks should not be broken arbitrarily; phrases should be maintained, i.e.,

- Adjective phrase, e.g., "very happy"
- Noun phrases, e.g., "the big red dog"
- Verb phrases, e.g., "is running"
- Adverb phrase, e.g., "very quickly"
- Prepositional phrase, e.g., "on the lawn"

For example, the sentence

> I am very happy that the big red dog is running very quickly on the lawn.

It makes no sense to break lines in the middle of a phrase, e.g.:

> I am very
> happy that the big red
> dog is running very
> quickly on the lawn.

From the lines in Thompson's bible, these rules:

- Each line begins flush left.
- A line may not exceed 36 picas; if it does, it must be broken into clauses or other semantic chunks, indicated by
  - a comma, parenthesis, bracket, brace, or similar
  - a conjunction, such as
    - and, or, nor
    - but, yet, for, so
    - because, although, since, unless, while
  - a word indicating an additional thought, such as
    - which, that (that is,)
    - for example, such as
  - a preposition, such as
    - in, on, at, under, between
    - before, after, during, until
    - to, into, through, across
  - an adverb, such as
    - then, next, later
    - subsequently, thereafter, meanwhile
    - therefore, thus, consequently
    - formerly, once
- The following punctuation marks force a new line (i.e., no text on a line follows, except a quotation mark or footnote):
  - period
  - semi-colon
  - colon
  - question mark
  - exclamation mark
- Text on a line may follow a comma.
- The text of a quote should start on a new line.
- Very rarely will there be a reason to have only one word on a line.



Let's rely on Thompson's heuristics, with a few adjustments.

- The font is Times, 12/14, FL/RR, < 27 picas, 324 pts.; only one size.
- Paragraphs should be re-broken by sense too, and separated by one line space.
- Include the original authors, the source, and the date.

- Quotes should be set in italics.
- Quotes of more than one line might be called out in blocks, with a 28 pt indent.
- Long lists should be considered for setting off as lists with a 28 pt indent and a return after each item — if the contents are central to the paper's topic. This decision requires judgement.
- Abstracts, key words, and similar meta-data (i.e., not the main text) should be set in italics, so that they contrast with the main text.
- Each section should have its own column.
- Especially long sections should be broken at sensible points.
- Section titles should appear one line above the hangline for columns.
- Section titles that are more than one line should expand upwards.

