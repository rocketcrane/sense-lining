#!/usr/bin/env python3
"""Place a sense-lined file onto the format.md grid.

One source line is one line of type. =column starts a column.
=abstract is its own leftmost column. Does not choose breaks.

Inline marks: *italic*, [n] superscript, {c}concept{/c} lime,
{s}sentence{/s} yellow. Nested {s}…{c}…{/c}…{/s} overlays.
"""

from __future__ import annotations

import base64
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent
MARGIN = 48.0
LEADING = 14.0
COL_W = 324.0
COL_STRIDE = 350.0
MIN_GAP = COL_STRIDE - COL_W
JUT_LIMIT = 0.25 * COL_W
MAX_LINE = 324.0
FIRST_Y = 48.0

FONT_ROMAN = pymupdf.Font("times-roman")
FONT_ITALIC = pymupdf.Font("times-italic")
FONT_BOLD = pymupdf.Font("times-bold")

MASTHEAD = {
    "=title": ("bold", "bold"),
    "=subtitle": ("roman", None),
    "=authors": ("roman", None),
    "=journal": ("italic", "italic"),
}


def measure(text: str, style: str, size: float = 12.0) -> float:
    if not text:
        return 0.0
    font = {"roman": FONT_ROMAN, "italic": FONT_ITALIC, "bold": FONT_BOLD}[style]
    return font.text_length(text, fontsize=size)


@dataclass
class Span:
    text: str
    style: str
    hl: frozenset[str] = field(default_factory=frozenset)


MARK = re.compile(
    r"\{(/?)([cs])\}|\[(\d+)\]|\*([^*]+)\*|“([^”]*)”|\"([^\"]*)\""
)


def _pop_hl(stack: list[str], kind: str) -> None:
    for i in range(len(stack) - 1, -1, -1):
        if stack[i] == kind:
            stack.pop(i)
            return


def stylize(text: str, base: str = "roman") -> list[Span]:
    spans: list[Span] = []
    stack: list[str] = []
    pos = 0

    def add(t: str, style: str) -> None:
        if t:
            spans.append(Span(t, style, frozenset(stack)))

    for m in MARK.finditer(text):
        if m.start() > pos:
            add(text[pos : m.start()], base)
        if m.group(2) is not None:
            if m.group(1):
                _pop_hl(stack, m.group(2))
            else:
                stack.append(m.group(2))
        elif m.group(3) is not None:
            add(m.group(3), "super")
        elif m.group(4) is not None:
            add(m.group(4), "italic" if base == "roman" else base)
        else:
            inner = m.group(5) if m.group(5) is not None else m.group(6)
            lq, rq = ("“", "”") if m.group(5) is not None else ('"', '"')
            add(lq, base)
            if inner:
                add(inner, "italic" if base == "roman" else base)
            add(rq, base)
        pos = m.end()
    if pos < len(text):
        add(text[pos:], base)
    return [s for s in spans if s.text]


def one_span_width(s: Span) -> float:
    if s.style == "super":
        return measure(s.text, "roman", 7.0)
    return measure(s.text, s.style, 12.0)


def span_width(spans: list[Span]) -> float:
    return sum(one_span_width(s) for s in spans)


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def line_width(text: str, base: str = "roman") -> float:
    return span_width(stylize(text, base))


@dataclass
class Placed:
    x: float
    y: float
    spans: list[Span]
    whole: str | None = None
    image: Path | None = None
    img_w: float = 0.0
    img_h: float = 0.0


@dataclass
class Column:
    n: int
    y: float
    x: float
    min_next_x: float = 0.0
    occlusions: list[tuple[float, float]] = field(default_factory=list)
    items: list[Placed] = field(default_factory=list)


def image_pt(path: Path) -> tuple[float, float]:
    pix = pymupdf.Pixmap(path)
    xr = pix.xres if pix.xres else 72
    yr = pix.yres if pix.yres else 72
    return pix.width * 72.0 / xr, pix.height * 72.0 / yr


class Sheet:
    def __init__(self, figdir: Path, has_abstract: bool = False) -> None:
        self.title_n = 1 if has_abstract else 0
        self.cols: list[Column] = [Column(n=0, y=FIRST_Y, x=MARGIN)]
        if has_abstract:
            self.cols.append(Column(n=1, y=FIRST_Y, x=MARGIN + COL_STRIDE))
        self.i = self.title_n
        self.deepest = FIRST_Y
        self.hang = 0.0
        self.title_y = 0.0
        self.masthead_y = FIRST_Y
        self.figdir = figdir
        self.head_lines: list[tuple[str, str]] = []
        self.body_column_open = False
        self.next_n = 0

    def col(self) -> Column:
        return self.cols[self.i]

    def ensure_n(self, n: int) -> Column:
        while len(self.cols) <= n:
            prev = self.cols[-1]
            x = max(prev.x + COL_STRIDE, prev.min_next_x)
            self.cols.append(Column(n=len(self.cols), y=self.hang, x=x))
        return self.cols[n]

    def _shift_col(self, col: Column, new_x: float) -> None:
        if new_x <= col.x + 0.01:
            return
        delta = new_x - col.x
        col.x = new_x
        for p in col.items:
            p.x += delta

    def cascade_x(self, from_n: int) -> None:
        for k in range(from_n + 1, len(self.cols)):
            self._shift_col(self.cols[k], self.cols[k - 1].x + COL_STRIDE)

    def push_next_for_figure(self, left: Column, fig_right: float) -> None:
        required = fig_right + MIN_GAP
        left.min_next_x = max(left.min_next_x, required)
        if left.n + 1 < len(self.cols):
            self._shift_col(self.cols[left.n + 1], required)
            self.cascade_x(left.n + 1)

    def apply_figure_width(self, left: Column, img_w: float, y_top: float, type_y: float) -> None:
        fig_right = left.x + img_w
        jut = fig_right - (left.x + COL_STRIDE)
        if img_w > COL_W and jut < JUT_LIMIT:
            self.push_next_for_figure(left, fig_right)
            left.y = type_y
            return
        n = left.n
        while True:
            c = self.ensure_n(n)
            if c.x >= fig_right:
                break
            if c.x + COL_W > left.x:
                c.occlusions.append((y_top, type_y))
                if n == left.n:
                    c.y = type_y
            n += 1
            if n > left.n + 6:
                break
        left.y = type_y

    def clear_y(self, col: Column, y: float) -> float:
        for y0, y1 in sorted(col.occlusions):
            if y0 - 0.01 <= y < y1:
                y = y1
        return y

    def freeze_hang(self) -> None:
        last = self.masthead_y - LEADING
        self.hang = last + 2 * LEADING
        self.title_y = self.hang - LEADING
        for c in self.cols:
            if c.n <= self.title_n:
                c.y = self.hang

    def start_column(self) -> Column:
        if not self.body_column_open:
            self.flush_heads()
            self.body_column_open = True
            self.i = self.title_n
            self.next_n = self.title_n + 1
            c = self.cols[self.i]
            c.y = self.clear_y(c, self.hang)
            return c
        self.flush_heads()
        c = self.ensure_n(self.next_n)
        self.i = self.next_n
        self.next_n += 1
        c.y = self.clear_y(c, self.hang)
        return c

    def flush_heads(self) -> None:
        if not self.head_lines:
            return
        c = self.col()
        n = len(self.head_lines)
        for k, (kind, text) in enumerate(self.head_lines):
            y = self.title_y - LEADING * (n - 1 - k)
            if y < FIRST_Y:
                raise RuntimeError(f"heading hit top margin: {text}")
            whole = "bold" if kind == "section" else "italic"
            style = "bold" if kind == "section" else "italic"
            c.items.append(Placed(x=c.x, y=y, spans=stylize(text, style), whole=whole))
            self.deepest = max(self.deepest, y)
        self.head_lines = []
        c.y = self.clear_y(c, self.hang)

    def add_masthead(self, text: str, style: str, whole: str | None) -> None:
        c = self.cols[self.title_n]
        y = self.masthead_y
        c.items.append(Placed(x=c.x, y=y, spans=stylize(text, style), whole=whole))
        self.deepest = max(self.deepest, y)
        self.masthead_y = y + LEADING

    def add_line(self, indent: float, text: str, base: str = "roman", whole: str | None = None) -> None:
        self.flush_heads()
        c = self.col()
        y = self.clear_y(c, c.y)
        spans = stylize(text, base)
        c.items.append(Placed(x=c.x + indent, y=y, spans=spans, whole=whole))
        c.y = y + LEADING
        self.deepest = max(self.deepest, y)

    def add_blank(self) -> None:
        self.flush_heads()
        c = self.col()
        c.y = self.clear_y(c, c.y + LEADING)

    def add_subsection(self, text: str) -> None:
        self.flush_heads()
        self.add_blank()
        self.add_line(0.0, text, "italic", "italic")
        self.add_blank()

    def find_image(self, img_name: str) -> Path | None:
        for p in (self.figdir / img_name, self.figdir.parent / img_name):
            if p.is_file():
                return p
        return None

    def place_figure(
        self,
        num: int,
        img_name: str | None,
        caption_lines: list[str],
        size: tuple[float, float] | None = None,
    ) -> None:
        self.flush_heads()
        img_path = self.find_image(img_name) if img_name else None
        if not img_path:
            self.add_line(0.0, f"FIGURE {num} [diagram omitted]")
            for line in caption_lines:
                self.add_line(0.0, line, "italic", "italic")
            self.add_blank()
            return
        img_w, img_h = size if size else image_pt(img_path)
        left = self.col()
        y_top = self.clear_y(left, left.y)
        left.items.append(
            Placed(x=left.x, y=y_top, spans=[], image=img_path, img_w=img_w, img_h=img_h)
        )
        cap_y = y_top + img_h + LEADING
        for line in caption_lines:
            left.items.append(
                Placed(x=left.x, y=cap_y, spans=stylize(line, "italic"), whole="italic")
            )
            self.deepest = max(self.deepest, cap_y)
            cap_y += LEADING
        type_y = cap_y + LEADING
        self.apply_figure_width(left, img_w, y_top, type_y)
        self.i = left.n
        self.deepest = max(self.deepest, y_top + img_h, cap_y - LEADING)


def _take_masthead(lines: list[str], i: int, sheet: Sheet | None) -> int:
    style, whole = MASTHEAD[lines[i].rstrip()]
    i += 1
    text = lines[i].rstrip() if i < len(lines) else ""
    if sheet is not None:
        sheet.add_masthead(text, style, whole)
    return i + 1 if i < len(lines) else i


def parse_and_place(path: Path, sheet: Sheet) -> None:
    lines = path.read_text().splitlines()
    i = 0
    while i < len(lines):
        if lines[i].rstrip() in MASTHEAD:
            i = _take_masthead(lines, i, sheet)
        else:
            i += 1
    sheet.freeze_hang()

    i = 0
    mode = "body"
    started = False
    pending_fig: dict | None = None

    def finish_fig() -> None:
        nonlocal pending_fig
        if pending_fig is not None:
            sheet.place_figure(
                pending_fig["n"],
                pending_fig["image"],
                pending_fig["caption"],
                pending_fig["size"],
            )
            pending_fig = None

    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        if line.startswith("="):
            finish_fig()
            if line in MASTHEAD:
                i = _take_masthead(lines, i, None)
                continue
            elif line == "=body":
                pass
            elif line == "=abstract":
                sheet.i = 0
                sheet.head_lines.append(("section", "Abstract"))
                started = True
                mode = "abstract"
            elif line == "=column":
                sheet.start_column()
                started = True
                mode = "body"
            elif line.startswith("=section"):
                text = line[len("=section") :].strip()
                if not text:
                    raise RuntimeError("empty =section")
                if not started:
                    sheet.start_column()
                    started = True
                sheet.head_lines.append(("section", text))
                mode = "body"
            elif line.startswith("=aside"):
                text = line[len("=aside") :].strip()
                if not started:
                    sheet.start_column()
                    started = True
                sheet.head_lines.append(("aside", text))
                mode = "body"
            elif line.startswith("=subsection"):
                sheet.add_subsection(line[len("=subsection") :].strip())
                mode = "body"
            elif line == "=quote":
                mode = "quote"
            elif line == "=quoteattr":
                mode = "quoteattr"
            elif line == "=list":
                mode = "list"
            elif line.startswith("=figure "):
                rest = line[len("=figure ") :].strip().split()
                pending_fig = {
                    "n": int(rest[0]),
                    "image": rest[1] if len(rest) > 1 else None,
                    "size": (float(rest[2]), float(rest[3])) if len(rest) >= 4 else None,
                    "caption": [],
                }
                mode = "caption"
            else:
                raise ValueError(f"unknown marker {line}")
            i += 1
            continue

        if not line.strip():
            finish_fig()
            if started:
                sheet.add_blank()
            if mode != "abstract":
                mode = "body"
            i += 1
            continue

        if not started:
            raise RuntimeError(f"body before =column: {line}")

        if pending_fig is not None and mode == "caption":
            pending_fig["caption"].append(line.strip())
            i += 1
            continue

        if mode == "quote":
            sheet.add_line(28.0, line.strip(), "italic", "italic")
        elif mode == "quoteattr":
            sheet.add_line(28.0, line.strip(), "italic", "italic")
            mode = "body"
        elif mode == "list":
            if line.startswith("  "):
                sheet.add_line(35.0, line.strip())
            else:
                text = line.strip()
                if not text.startswith("–"):
                    text = "– " + text
                sheet.add_line(28.0, text)
        elif mode == "abstract":
            sheet.add_line(0.0, line.strip(), "italic", "italic")
        else:
            sheet.add_line(0.0, line.strip())
        i += 1

    finish_fig()
    sheet.flush_heads()


HL_FILL = {
    "s": ("#ffe44d", 0.58),
    "c": ("#9aff00", 0.55),
}
HL_BOX = {
    "s": (-11.4, 14.4),
    "c": (-10.2, 12.6),
}


def highlight_svg(p: Placed) -> list[str]:
    parts: list[str] = []
    for kind in ("s", "c"):
        if not any(kind in s.hl for s in p.spans):
            continue
        fill, op = HL_FILL[kind]
        dy, h = HL_BOX[kind]
        x = p.x
        run_x: float | None = None
        run_w = 0.0

        def flush() -> None:
            nonlocal run_x, run_w
            if run_x is None or run_w <= 0:
                run_x = None
                run_w = 0.0
                return
            parts.append(
                f'    <rect x="{run_x - 1.2:.1f}" y="{p.y + dy:.1f}" '
                f'width="{run_w + 2.4:.1f}" height="{h:.1f}" '
                f'rx="1.2" fill="{fill}" fill-opacity="{op}"/>'
            )
            run_x = None
            run_w = 0.0

        for s in p.spans:
            w = one_span_width(s)
            if kind in s.hl:
                if run_x is None:
                    run_x = x
                    run_w = w
                else:
                    run_w += w
            else:
                flush()
            x += w
        flush()
    return parts


def svg_text(p: Placed) -> str:
    attrs = [f'x="{p.x:.1f}"', f'y="{p.y:.1f}"']
    if p.whole == "bold":
        attrs.append('font-weight="bold"')
    if p.whole == "italic":
        attrs.append('font-style="italic"')
    inner: list[str] = []
    if p.whole and not any(s.style == "super" for s in p.spans):
        inner.append(esc("".join(s.text for s in p.spans)))
    else:
        for s in p.spans:
            t = esc(s.text)
            if s.style == "italic":
                inner.append(f'<tspan font-style="italic">{t}</tspan>')
            elif s.style == "bold":
                inner.append(f'<tspan font-weight="bold">{t}</tspan>')
            elif s.style == "super":
                inner.append(
                    f'<tspan font-size="7" dy="-4">{t}</tspan><tspan dy="4"></tspan>'
                )
            else:
                inner.append(t)
    return f'    <text {" ".join(attrs)}>{"".join(inner)}</text>'


def sheet_width(cols: list[Column]) -> float:
    right = max(c.x + COL_W for c in cols)
    for c in cols:
        for p in c.items:
            if p.image:
                right = max(right, p.x + p.img_w)
    return right + MARGIN


def emit_svg(cols: list[Column], deepest: float) -> str:
    width = sheet_width(cols)
    height = deepest + MARGIN
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.1f}" height="{height:.1f}" viewBox="0 0 {width:.1f} {height:.1f}">',
        f'  <rect width="{width:.1f}" height="{height:.1f}" fill="#ffffff"/>',
        '  <g font-family="Times New Roman, Times, serif" font-size="12" fill="#111111">',
    ]
    for col in cols:
        for p in col.items:
            if p.image:
                b64 = base64.b64encode(p.image.read_bytes()).decode("ascii")
                parts.append(
                    f'    <image x="{p.x:.1f}" y="{p.y:.1f}" width="{p.img_w:.1f}" '
                    f'height="{p.img_h:.1f}" href="data:image/png;base64,{b64}"/>'
                )
            else:
                parts.extend(highlight_svg(p))
                parts.append(svg_text(p))
    parts.append("  </g>")
    parts.append("</svg>")
    parts.append("")
    return "\n".join(parts)


def audit(cols: list[Column], hang: float) -> None:
    over = []
    singles = []
    for col in cols:
        for p in col.items:
            if p.image:
                continue
            w = span_width(p.spans)
            limit = MAX_LINE - (p.x - col.x)
            if w > limit + 0.05:
                over.append((col.n, p.y, w, "".join(s.text for s in p.spans)))
            plain = "".join(s.text for s in p.spans).strip()
            if plain and len(plain.split()) == 1 and not plain.startswith("FIGURE") and p.whole != "bold":
                singles.append((col.n, p.y, plain))
    print(f"columns {len(cols)}  hang {hang:.1f}  overlong {len(over)}  one-word {len(singles)}")
    for row in over:
        print(" OVER", row[0], f"{row[2]:.1f}", row[3])
    for row in singles:
        print(" ONE ", row[0], row[2])


def resolve_lines(name: str) -> Path:
    p = Path(name)
    if p.is_file():
        return p.resolve()
    stem = p.name.removesuffix("_lines.txt").removesuffix(".txt")
    for c in (Path(f"{stem}_lines.txt"), ROOT / f"{stem}_lines.txt"):
        if c.is_file():
            return c.resolve()
    raise SystemExit(f"no lines file for {name}")


def output_stem(lines_path: Path) -> str:
    s = lines_path.stem
    return s[: -len("_lines")] if s.endswith("_lines") else s


def main(name: str) -> None:
    lines_path = resolve_lines(name)
    figdir = lines_path.parent / "figures"
    if not figdir.is_dir():
        figdir = lines_path.parent
    has_abs = any(l.rstrip() == "=abstract" for l in lines_path.read_text().splitlines())
    sheet = Sheet(figdir, has_abstract=has_abs)
    parse_and_place(lines_path, sheet)
    stem = output_stem(lines_path)
    svg_path = lines_path.with_name(stem + ".svg")
    pdf_path = lines_path.with_name(stem + ".pdf")
    audit(sheet.cols, sheet.hang)
    svg = emit_svg(sheet.cols, sheet.deepest)
    svg_path.write_text(svg)
    print("wrote", svg_path, "bytes", svg_path.stat().st_size)
    doc = pymupdf.open(stream=svg.encode("utf-8"), filetype="svg")
    pdf_path.write_bytes(doc.convert_to_pdf())
    print(
        "wrote",
        pdf_path,
        "bytes",
        pdf_path.stat().st_size,
        "page",
        doc[0].rect,
        "deepest",
        f"{sheet.deepest:.1f}",
    )


def _plain(p: Placed) -> str:
    return "".join(s.text for s in p.spans)


def _check() -> None:
    import tempfile

    td = Path(tempfile.mkdtemp())
    preprint = td / "preprint_lines.txt"
    preprint.write_text("=title\nHello\n=authors\nA. A\n\n=column\nBody line here.\n")
    sheet = Sheet(td)
    parse_and_place(preprint, sheet)
    assert sheet.hang == 90.0, sheet.hang
    assert len(sheet.cols) == 1
    paper = td / "paper_lines.txt"
    paper.write_text(
        "=abstract\nWe show a thing.\n\n"
        "=title\nThe Paper\n=authors\nA. Academic\n=journal\narXiv 2026\n\n"
        "=column\nOpening sentence.\n"
        "=column\n=section Next\nMore.\n"
    )
    sheet = Sheet(td, has_abstract=True)
    parse_and_place(paper, sheet)
    assert sheet.hang == 104.0, sheet.hang
    assert sheet.title_n == 1
    assert len(sheet.cols) == 3
    assert _plain(sheet.cols[0].items[0]) == "Abstract"
    assert sheet.cols[0].items[0].y == sheet.title_y
    assert sheet.cols[0].items[0].whole == "bold"
    assert sheet.cols[0].items[1].whole == "italic"
    assert _plain(sheet.cols[1].items[0]) == "The Paper"
    assert sheet.cols[1].items[0].y == FIRST_Y
    assert not any(abs(it.y - sheet.title_y) < 0.01 for it in sheet.cols[1].items)
    print("ok")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "width":
        base = sys.argv[2]
        text = " ".join(sys.argv[3:])
        print(f"{line_width(text, base):.2f}  {text}")
        sys.exit(0)
    names = sys.argv[1:]
    if not names:
        sys.exit("usage: build_sheet.py NAME ...")
    if names == ["--check"]:
        _check()
        sys.exit(0)
    for name in names:
        main(name)
