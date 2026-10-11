"""Brick Builder - a tiny sandbox that runs in the browser via pygbag.

Controls
  Left click   place brick          Right click  remove brick
  1-8          pick color           Mouse wheel  cycle color
  Q / E        brick width - / +    Z            undo
  C            clear board
"""

import asyncio

import pygame

from grid import Grid

VERSION = "dev"  # CI replaces this with the commit hash

CELL = 32
COLS, ROWS = 24, 16
TOOLBAR_H = 56
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL + TOOLBAR_H

BG = (28, 31, 38)
GRID_LINE = (40, 44, 53)
TEXT = (220, 224, 232)
PALETTE = [
    (214, 48, 49),   # red
    (240, 147, 43),  # orange
    (253, 203, 60),  # yellow
    (46, 160, 67),   # green
    (52, 120, 246),  # blue
    (142, 68, 173),  # purple
    (236, 240, 241), # white
    (60, 64, 72),    # dark grey
]


def shade(color, factor):
    return tuple(max(0, min(255, int(c * factor))) for c in color)


def draw_brick(surf, px, py, width, color, alpha=255):
    """Draw a brick `width` cells wide with its top-left at pixel (px, py)."""
    w, h = width * CELL, CELL
    brick = pygame.Surface((w, h + 6), pygame.SRCALPHA)
    body = pygame.Rect(0, 6, w, h)
    pygame.draw.rect(brick, (*color, alpha), body, border_radius=3)
    pygame.draw.rect(brick, (*shade(color, 0.65), alpha), body, width=2, border_radius=3)
    pygame.draw.line(brick, (*shade(color, 1.25), alpha), (3, 8), (w - 4, 8), 2)
    # studs on top
    for i in range(width):
        cx = i * CELL + CELL // 2
        stud = pygame.Rect(cx - 8, 0, 16, 9)
        pygame.draw.rect(brick, (*shade(color, 0.9), alpha), stud, border_radius=3)
        pygame.draw.rect(brick, (*shade(color, 1.2), alpha), stud.inflate(-6, -5), border_radius=2)
    surf.blit(brick, (px, py - 6))


def cell_from_mouse(pos):
    x, y = pos
    y -= TOOLBAR_H
    if y < 0:
        return None
    return x // CELL, y // CELL


def draw_toolbar(screen, font, color_idx, width, count):
    pygame.draw.rect(screen, (20, 22, 28), (0, 0, WIDTH, TOOLBAR_H))
    for i, col in enumerate(PALETTE):
        rect = pygame.Rect(12 + i * 40, 12, 32, 32)
        pygame.draw.rect(screen, col, rect, border_radius=6)
        if i == color_idx:
            pygame.draw.rect(screen, TEXT, rect.inflate(6, 6), width=2, border_radius=8)
    info = f"Width {width}  |  Bricks {count}  |  Z undo  C clear  |  v{VERSION}"
    screen.blit(font.render(info, True, TEXT), (12 + len(PALETTE) * 40 + 8, 20))


async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Brick Builder")
    font = pygame.font.Font(None, 22)
    clock = pygame.time.Clock()

    grid = Grid(COLS, ROWS)
    color_idx, brick_w = 0, 2

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                cell = cell_from_mouse(event.pos)
                if event.button == 1:
                    if cell:
                        grid.place(cell[0], cell[1], brick_w, color_idx)
                    else:  # clicked the palette
                        i = (event.pos[0] - 12) // 40
                        if 0 <= i < len(PALETTE):
                            color_idx = i
                elif event.button == 3 and cell:
                    grid.remove_at(*cell)
            elif event.type == pygame.MOUSEWHEEL:
                color_idx = (color_idx - event.y) % len(PALETTE)
            elif event.type == pygame.KEYDOWN:
                if pygame.K_1 <= event.key <= pygame.K_8:
                    color_idx = event.key - pygame.K_1
                elif event.key == pygame.K_q:
                    brick_w = max(1, brick_w - 1)
                elif event.key == pygame.K_e:
                    brick_w = min(4, brick_w + 1)
                elif event.key == pygame.K_z:
                    grid.undo()
                elif event.key == pygame.K_c:
                    grid.clear()

        # draw board
        screen.fill(BG)
        for x in range(COLS + 1):
            pygame.draw.line(screen, GRID_LINE, (x * CELL, TOOLBAR_H), (x * CELL, HEIGHT))
        for y in range(ROWS + 1):
            pygame.draw.line(screen, GRID_LINE, (0, TOOLBAR_H + y * CELL), (WIDTH, TOOLBAR_H + y * CELL))

        # draw bricks bottom row first so studs overlap the brick above nicely
        for b in sorted(grid.bricks.values(), key=lambda b: -b.y):
            draw_brick(screen, b.x * CELL, TOOLBAR_H + b.y * CELL, b.width, PALETTE[b.color])

        # ghost preview under the mouse
        cell = cell_from_mouse(pygame.mouse.get_pos())
        if cell and grid.can_place(cell[0], cell[1], brick_w):
            draw_brick(screen, cell[0] * CELL, TOOLBAR_H + cell[1] * CELL,
                       brick_w, PALETTE[color_idx], alpha=110)

        draw_toolbar(screen, font, color_idx, brick_w, grid.count())
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)  # required by pygbag: hand control back to the browser

    pygame.quit()


asyncio.run(main())
