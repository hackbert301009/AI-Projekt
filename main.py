# =====================================================================
#  __  __ _         _ __  __
# |  \/  (_)_ _  __| |  \/  |__ _ ______
# | |\/| | | ' \/ _` | |\/| / _` |_ / -_)
# |_|  |_|_|_||_\__,_|_|  |_\__,_/__\___|   ein hackbert-projekt
# =====================================================================
#  Ein RL-Agent lernt LIVE den Weg durchs Labyrinth.
#  Etappe 1 / 6:  "Die Welt"  --  wir bauen erstmal das Spielfeld.
#
#  Noch bewegt sich nichts. Wir zeichnen nur das Gitter, die Waende,
#  den Start (S) und das Ziel (Z). Fundament muss sitzen, dann kommt
#  der schlaue Teil.  -- hackbert
# =====================================================================

# ---------- Welt-Geometrie ----------
GW = 8          # Spalten
GH = 6          # Zeilen
CELL = 18       # Pixel pro Zelle
OX = 8          # Gitter-Offset x (Rand links)
OY = 11         # Gitter-Offset y (HUD-Leiste sitzt drueber)

START_C = 0
START_R = 5
GOAL_C = 7
GOAL_R = 0

# Waende: zwei vertikale Riegel -> erzwingen spaeter einen Schlangenpfad.
WALLS = [[2, 1], [2, 2], [2, 3], [2, 4], [5, 1], [5, 2], [5, 3], [5, 4]]

# ---------- Farben (MakeCode-Arcade-Palette) ----------
COL_BG = 15      # schwarz
COL_FLOOR = 6    # teal  -- der begehbare Boden
COL_WALL = 11    # lila  -- die Mauern
COL_GRID = 15    # schwarz -- duenne Gitterlinien
COL_START = 4    # orange
COL_GOAL = 5     # gelb
COL_TEXT = 1     # weiss


def is_wall(c, r):
    # Schaut nach, ob auf (c, r) eine Mauer steht.
    k = 0
    while k < len(WALLS):
        if WALLS[k][0] == c and WALLS[k][1] == r:
            return True
        k += 1
    return False


# ---------- Rendering: das ganze Spielfeld selbst malen ----------
def on_render(screen, camera):
    # HUD-Leiste oben
    screen.fill_rect(0, 0, 160, 10, COL_BG)
    screen.print("MindMaze  E1: die welt", 1, 1, COL_TEXT)

    # Alle Zellen durchgehen und einfaerben
    r = 0
    while r < GH:
        c = 0
        while c < GW:
            cellx = OX + c * CELL
            celly = OY + r * CELL

            if is_wall(c, r):
                screen.fill_rect(cellx, celly, CELL, CELL, COL_WALL)
            else:
                screen.fill_rect(cellx, celly, CELL, CELL, COL_FLOOR)

            # duenne Gitterlinie drumherum
            screen.draw_rect(cellx, celly, CELL, CELL, COL_GRID)
            c += 1
        r += 1

    # Start markieren (orange Feld mit "S")
    sx = OX + START_C * CELL
    sy = OY + START_R * CELL
    screen.fill_rect(sx + 1, sy + 1, CELL - 2, CELL - 2, COL_START)
    screen.print("S", sx + 6, sy + 5, COL_TEXT)

    # Ziel markieren (gelber Rahmen mit "Z")
    gx = OX + GOAL_C * CELL
    gy = OY + GOAL_R * CELL
    screen.draw_rect(gx, gy, CELL, CELL, COL_GOAL)
    screen.draw_rect(gx + 1, gy + 1, CELL - 2, CELL - 2, COL_GOAL)
    screen.print("Z", gx + 6, gy + 5, COL_TEXT)


scene.set_background_color(COL_BG)
scene.create_renderable(100, on_render)
