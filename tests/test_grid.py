import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "game"))

from grid import Grid  # noqa: E402


def test_place_and_lookup():
    g = Grid(10, 5)
    assert g.place(2, 3, 2, color=1)
    assert g.brick_at(2, 3) is g.brick_at(3, 3)
    assert g.brick_at(4, 3) is None
    assert g.count() == 1


def test_no_overlap():
    g = Grid(10, 5)
    g.place(2, 0, 3, 0)
    assert not g.place(4, 0, 2, 0)  # overlaps column 4
    assert g.place(5, 0, 2, 0)


def test_out_of_bounds():
    g = Grid(10, 5)
    assert not g.place(9, 0, 2, 0)  # runs off the right edge
    assert not g.place(0, 5, 1, 0)  # below the board
    assert not g.place(-1, 0, 1, 0)


def test_remove_any_cell_of_brick():
    g = Grid(10, 5)
    g.place(0, 0, 4, 0)
    assert g.remove_at(3, 0)
    assert g.count() == 0
    assert g.can_place(0, 0, 4)


def test_undo_place_and_remove():
    g = Grid(10, 5)
    g.place(1, 1, 2, 2)
    g.remove_at(1, 1)
    assert g.undo()          # brings the brick back
    assert g.brick_at(2, 1).color == 2
    assert g.undo()          # removes it again
    assert g.count() == 0
    assert not g.undo()      # nothing left


def test_clear():
    g = Grid(10, 5)
    g.place(0, 0, 1, 0)
    g.place(5, 4, 3, 1)
    g.clear()
    assert g.count() == 0
    assert not g.undo()
