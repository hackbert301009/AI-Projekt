# =====================================================================
#  __  __ _         _ __  __
# |  \/  (_)_ _  __| |  \/  |__ _ ______
# | |\/| | | ' \/ _` | |\/| / _` |_ / -_)
# |_|  |_|_|_||_\__,_|_|  |_\__,_/__\___|   ein hackbert-projekt
# =====================================================================
#  Ein RL-Agent lernt LIVE den Weg durchs Labyrinth.
#  Etappe 2 / 6:  "Der Wanderer"  --  jetzt bewegt sich was.
#
#  Der Held latscht noch völlig planlos durch die Gegend (reiner
#  Zufall, kein Gehirn). Aber: er hält sich an die Wände, mogelt
#  nicht durch Mauern und feiert jeden Zufallstreffer am Ziel.
#  Das Lernen kommt in Etappe 3.  -- hackbert
# =====================================================================

# ---------- Welt-Geometrie ----------
GW = 8          # Spalten
GH = 6          # Zeilen
CELL = 18       # Pixel pro Zelle
OX = 8          # Gitter-Offset x (Rand links)
OY = 11         # Gitter-Offset y (HUD-Leiste sitzt drüber)

START_C = 0
START_R = 5
GOAL_C = 7
GOAL_R = 0

# Wände: zwei vertikale Riegel -> erzwingen einen Schlangenpfad.
WALLS = [[2, 1], [2, 2], [2, 3], [2, 4], [5, 1], [5, 2], [5, 3], [5, 4]]

# ---------- Aktionen: 0=hoch  1=runter  2=links  3=rechts ----------
DX = [0, 0, -1, 1]
DY = [-1, 1, 0, 0]

# ---------- Farben (MakeCode-Arcade-Palette) ----------
COL_BG = 15      # schwarz
COL_FLOOR = 6    # teal  -- der begehbare Boden
COL_WALL = 11    # lila  -- die Mauern
COL_GRID = 15    # schwarz -- dünne Gitterlinien
COL_START = 4    # orange
COL_GOAL = 5     # gelb
COL_AGENT = 1    # weiss -- unser Wanderer
COL_TEXT = 1     # weiss

# ---------- Laufzeit-Zustand ----------
agent_col = START_C
agent_row = START_R
steps = 0        # Schritte in der aktuellen Runde
arrivals = 0     # wie oft das Ziel (zufällig) erreicht wurde


def is_wall(c, r):
    # Schaut nach, ob auf (c, r) eine Mauer steht.
    k = 0
    while k < len(WALLS):
        if WALLS[k][0] == c and WALLS[k][1] == r:
            return True
        k += 1
    return False


# ---------- Bewegung: ein Zufallsschritt ----------
def wander_step():
    global agent_col, agent_row, steps, arrivals

    a = randint(0, 3)
    nc = agent_col + DX[a]
    nr = agent_row + DY[a]

    # gegen Wand oder Rand gelaufen? -> stehen bleiben
    if nc < 0 or nc >= GW or nr < 0 or nr >= GH or is_wall(nc, nr):
        return

    agent_col = nc
    agent_row = nr
    steps += 1

    # Ziel zufällig getroffen -> feiern und zurück auf Los
    if agent_col == GOAL_C and agent_row == GOAL_R:
        arrivals += 1
        steps = 0
        agent_col = START_C
        agent_row = START_R


# alle 120 ms ein Schritt -> man kann dem Wanderer beim Irren zusehen
game.on_update_interval(120, wander_step)


# ---------- Rendering: das ganze Spielfeld selbst malen ----------
def on_render(screen, camera):
    # HUD-Leiste oben
    screen.fill_rect(0, 0, 160, 10, COL_BG)
    screen.print("E2 wanderer  Treffer:" + str(arrivals), 1, 1, COL_TEXT)

    # Alle Zellen durchgehen und einfärben
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

            # dünne Gitterlinie drumherum
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

    # Agent zeichnen (weisses Kästchen mit schwarzem Rand)
    ax = OX + agent_col * CELL + 9
    ay = OY + agent_row * CELL + 9
    screen.fill_rect(ax - 3, ay - 3, 6, 6, COL_AGENT)
    screen.draw_rect(ax - 3, ay - 3, 6, 6, COL_BG)


scene.set_background_color(COL_BG)
scene.create_renderable(100, on_render)
