"""Pure game logic for the brick builder. No pygame here, so it's easy to test."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Brick:
    x: int        # left column
    y: int        # row (0 = top)
    width: int    # in studs / cells
    color: int    # index into the palette


class Grid:
    def __init__(self, cols: int, rows: int):
        self.cols = cols
        self.rows = rows
        self.cells = [[None] * cols for _ in range(rows)]  # brick id or None
        self.bricks: dict[int, Brick] = {}
        self._next_id = 1
        self._history: list[tuple[str, int, Brick]] = []

    # --- queries -----------------------------------------------------
    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.cols and 0 <= y < self.rows

    def brick_at(self, x: int, y: int):
        if not self.in_bounds(x, y):
            return None
        bid = self.cells[y][x]
        return self.bricks.get(bid) if bid else None

    def can_place(self, x: int, y: int, width: int) -> bool:
        if width < 1 or not self.in_bounds(x, y) or not self.in_bounds(x + width - 1, y):
            return False
        return all(self.cells[y][x + i] is None for i in range(width))

    # --- edits -------------------------------------------------------
    def _put(self, bid: int, brick: Brick):
        self.bricks[bid] = brick
        for i in range(brick.width):
            self.cells[brick.y][brick.x + i] = bid

    def _take(self, bid: int) -> Brick:
        brick = self.bricks.pop(bid)
        for i in range(brick.width):
            self.cells[brick.y][brick.x + i] = None
        return brick

    def place(self, x: int, y: int, width: int, color: int) -> bool:
        if not self.can_place(x, y, width):
            return False
        bid = self._next_id
        self._next_id += 1
        brick = Brick(x, y, width, color)
        self._put(bid, brick)
        self._history.append(("place", bid, brick))
        return True

    def remove_at(self, x: int, y: int) -> bool:
        if not self.in_bounds(x, y) or self.cells[y][x] is None:
            return False
        bid = self.cells[y][x]
        brick = self._take(bid)
        self._history.append(("remove", bid, brick))
        return True

    def undo(self) -> bool:
        if not self._history:
            return False
        action, bid, brick = self._history.pop()
        if action == "place":
            self._take(bid)
        else:
            self._put(bid, brick)
        return True

    def clear(self):
        self.cells = [[None] * self.cols for _ in range(self.rows)]
        self.bricks.clear()
        self._history.clear()

    def count(self) -> int:
        return len(self.bricks)
