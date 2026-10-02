#!/usr/bin/env python3
"""Draw aligned ASCII boxes-and-arrows diagrams (wiki-design decision 0011).

Hand-spaced boxes drift; place everything by column and row instead, print, and paste the
result into a ```text block. Boxes use + - | corners, arrows are plain text such as `--- 50 --->`.

    from diagram import Canvas              # run from tools/, or add it to sys.path
    c = Canvas(78)                          # width in columns (notes allow 80)
    c.put(0, 0, "ONCE PER CALL")            # text at column x, row y
    c.box(0, 1, 19, 3, ["input"])           # box at x, y, width, height with inner lines
    c.put(19, 2, "--- 64 --->")             # arrow, labelled with what moves and its size
    c.box(30, 1, 40, 3, ["model"])
    c.vline(10, 4, 6); c.put(10, 6, "v")    # vertical arrow
    print(c.render())

`tools/wiki.py check` then verifies the box edges line up (DIAGRAM error).
"""


class Canvas:
    def __init__(self, width=78):
        self.width, self.cells = width, {}

    def put(self, x, y, text):
        for i, ch in enumerate(text):
            self.cells[(x + i, y)] = ch

    def box(self, x, y, w, h, lines=()):
        self.put(x, y, "+" + "-" * (w - 2) + "+")
        self.put(x, y + h - 1, "+" + "-" * (w - 2) + "+")
        for j in range(1, h - 1):
            self.put(x, y + j, "|" + " " * (w - 2) + "|")
        for j, line in enumerate(lines):
            self.put(x + 2, y + 1 + j, line)

    def vline(self, x, y0, y1, ch="|"):
        for y in range(y0, y1):
            self.put(x, y, ch)

    def render(self):
        rows = max(y for _, y in self.cells) + 1
        return "\n".join("".join(self.cells.get((x, y), " ") for x in range(self.width)).rstrip() for y in range(rows))


if __name__ == "__main__":
    c = Canvas(40)
    c.box(0, 0, 12, 3, ["input"])
    c.put(12, 1, "-- 64 -->")
    c.box(21, 0, 12, 3, ["model"])
    print(c.render())
