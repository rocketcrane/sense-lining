#!/usr/bin/env python3
"""Place a sense-lined file onto the format.md grid.

One source line is one line of type. =column starts a column.
Does not choose breaks.
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

PAPERS = {
    "meadows": {
        "lines": ROOT / "meadows_lines.txt",
        "figdir": ROOT / "figures",
        "svg": ROOT / "meadows.svg",
        "pdf": ROOT / "meadows.pdf",
        "scale": 12.0 / 11.0,
        "figs": {
            "fig1.png": (330.0, 65.0),
            "fig2.png": (174.0, 63.0),
            "fig3.png": (328.0, 101.0),
            "fig4.png": (330.0, 116.0),
            "fig5.png": (328.0, 69.0),
            "fig6.png": (270.0, 171.0),
            "fig7.png": (318.0, 394.0),
            "fig8.png": (214.0, 257.0),
            "fig9.png": (336.0, 182.0),
            "fig10.png": (342.0, 132.0),
            "fig11.png": (320.0, 195.0),
            "fig12.png": (206.0, 122.0),
            "fig13.png": (327.0, 190.0),
            "fig14.png": (212.0, 133.0),
        },
    },
    "licklider": {
        "lines": ROOT / "licklider_lines.txt",
        "figdir": ROOT / "figures",
        "svg": ROOT / "licklider.svg",
        "pdf": ROOT / "licklider.pdf",
        "scale": 12.0 / 10.7932,
        "figs": {
            "mental.png": (338.7, 146.2),
            "meeting.png": (298.6, 224.2),
            "arousal.png": (337.5, 107.8),
            "dialog.png": (293.7, 126.5),
            "filibuster.png": (339.9, 174.7),
            "oliver.png": (204.3, 179.5),
        },
    },
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


def stylize(text: str, base: str = "roman") -> list[Span]:
    spans: list[Span] = []
    pattern = re.compile(r"\[(\d+)\]|\*([^*]+)\*|“([^”]*)”|\"([^\"]*)\"")
    pos = 0
    for m in pattern.finditer(text):
        if m.start() > pos:
            spans.append(Span(text[pos : m.start()], base))
        if m.group(1) is not None:
            spans.append(Span(m.group(1), "super"))
        elif m.group(2) is not None:
            spans.append(Span(m.group(2), "italic" if base == "roman" else base))
        else:
            inner = m.group(3) if m.group(3) is not None else m.group(4)
            lq, rq = ("“", "”") if m.group(3) is not None else ('"', '"')
            spans.append(Span(lq, base))
            if inner:
                spans.append(Span(inner, "italic" if base == "roman" else base))
            spans.append(Span(rq, base))
        pos = m.end()
    if pos < len(text):
        spans.append(Span(text[pos:], base))
    return [s for s in spans if s.text]


def span_width(spans: list[Span]) -> float:
    w = 0.0
    for s in spans:
        if s.style == "super":
            w += measure(s.text, "roman", 7.0)
        else:
            w += measure(s.text, s.style, 12.0)
    return w


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


class Sheet:
    def __init__(self, figdir: Path, fig_print: dict, fig_scale: float) -> None:
        self.cols: list[Column] = [Column(n=0, y=FIRST_Y, x=MARGIN)]
        self.i = 0
        self.deepest = FIRST_Y
        self.hang = 0.0
        self.title_y = 0.0
        self.masthead_y = FIRST_Y
        self.figdir = figdir
        self.fig_print = fig_print
        self.fig_scale = fig_scale
        self.head_lines: list[tuple[str, str]] = []
        self.body_column_open = False
        self.next_n = 0  # (kind, text) stacked at next column start

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
        self.cols[0].y = self.hang

    def start_column(self) -> Column:
        if self.hang < 1:
            raise RuntimeError("=column before masthead")
        if not self.body_column_open:
            self.body_column_open = True
            self.i = 0
            self.next_n = 1
            c = self.cols[0]
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
        c = self.cols[0]
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

    def place_figure(self, num: int, img_name: str | None, caption_lines: list[str]) -> None:
        self.flush_heads()
        img_path = self.figdir / img_name if img_name else None
        if not (img_path and img_path.exists() and img_name in self.fig_print):
            self.add_line(0.0, f"FIGURE {num} [diagram omitted]")
            for line in caption_lines:
                self.add_line(0.0, line, "italic", "italic")
            self.add_blank()
            return
        print_w, print_h = self.fig_print[img_name]
        img_w = print_w * self.fig_scale
        img_h = print_h * self.fig_scale
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


def parse_and_place(path: Path, sheet: Sheet) -> None:
    lines = path.read_text().splitlines()
    i = 0
    mode = "body"
    hang_ready = False
    started = False
    pending_fig: dict | None = None

    def finish_fig() -> None:
        nonlocal pending_fig
        if pending_fig is not None:
            sheet.place_figure(pending_fig["n"], pending_fig["image"], pending_fig["caption"])
            pending_fig = None

    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        if line.startswith("="):
            finish_fig()
            if line == "=title":
                i += 1
                sheet.add_masthead(lines[i].rstrip(), "bold", "bold")
            elif line == "=subtitle":
                i += 1
                sheet.add_masthead(lines[i].rstrip(), "roman", None)
            elif line == "=authors":
                i += 1
                sheet.add_masthead(lines[i].rstrip(), "roman", None)
            elif line == "=journal":
                i += 1
                sheet.add_masthead(lines[i].rstrip(), "italic", "italic")
                sheet.freeze_hang()
                hang_ready = True
            elif line == "=body":
                pass
            elif line == "=column":
                if not hang_ready:
                    raise RuntimeError("=column before journal/masthead")
                finish_fig()
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
                rest = line[len("=figure ") :].strip().split(None, 1)
                pending_fig = {
                    "n": int(rest[0]),
                    "image": rest[1] if len(rest) > 1 else None,
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
        else:
            sheet.add_line(0.0, line.strip())
        i += 1

    finish_fig()
    sheet.flush_heads()


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


def main(name: str) -> None:
    cfg = PAPERS[name]
    sheet = Sheet(cfg["figdir"], cfg["figs"], cfg["scale"])
    parse_and_place(cfg["lines"], sheet)
    audit(sheet.cols, sheet.hang)
    svg = emit_svg(sheet.cols, sheet.deepest)
    cfg["svg"].write_text(svg)
    print("wrote", cfg["svg"], "bytes", cfg["svg"].stat().st_size)
    doc = pymupdf.open(stream=svg.encode("utf-8"), filetype="svg")
    cfg["pdf"].write_bytes(doc.convert_to_pdf())
    print(
        "wrote",
        cfg["pdf"],
        "bytes",
        cfg["pdf"].stat().st_size,
        "page",
        doc[0].rect,
        "deepest",
        f"{sheet.deepest:.1f}",
    )


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "width":
        base = sys.argv[2]
        text = " ".join(sys.argv[3:])
        print(f"{line_width(text, base):.2f}  {text}")
        sys.exit(0)
    names = sys.argv[1:] or ["meadows", "licklider"]
    for name in names:
        main(name)
