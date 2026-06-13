# =====================================================================
#  __  __ _         _ __  __
# |  \/  (_)_ _  __| |  \/  |__ _ ______
# | |\/| | | ' \/ _` | |\/| / _` |_ / -_)
# |_|  |_|_|_||_\__,_|_|  |_\__,_/__\___|   ein hackbert-projekt
# =====================================================================
#  Ausbau: WETTRENNEN, TUNING & LOGO
#
#  Mehrere RL-Agenten mit je EIGENEM Gehirn (Q-Tabelle) rennen
#  gleichzeitig durchs Labyrinth - wer findet zuerst den kurzen Weg?
#  Jeder ist unterschiedlich neugierig. Alle Lern-Parameter lassen
#  sich live einstellen, und du kannst zwischen mehreren Ansichten
#  umschalten.
#
#  STEUERUNG
#    Titel:        A = Start          Menu = Einstellungen
#    Lauf:         A = Pause          B   = Tempo (x1/x4/x16/x64)
#                  Hoch = Ansicht     Runter = Reset
#                  Links/Rechts = Fokus-Agent (dessen Heatmap man sieht)
#                  Menu = Einstellungen
#    Einstellung:  Hoch/Runter = waehlen   Links/Rechts = aendern
#                  A oder Menu = uebernehmen & neu starten
#  -- hackbert
# =====================================================================

# ---------- Welt-Geometrie ----------
GW = 8
GH = 6
NSTATES = 48
CELL = 18
OX = 8
OY = 11

START_C = 0
START_R = 5
GOAL_C = 7
GOAL_R = 0

# Wände: zwei vertikale Riegel -> erzwingen einen Schlangenpfad.
WALLS = [[2, 1], [2, 2], [2, 3], [2, 4], [5, 1], [5, 2], [5, 3], [5, 4]]

# ---------- Aktionen: 0=hoch  1=runter  2=links  3=rechts ----------
DX = [0, 0, -1, 1]
DY = [-1, 1, 0, 0]

# ---------- feste Lern-Werte ----------
EPS_MIN = 0.05
R_GOAL = 100.0
R_WALL = -5.0
R_STEP = -1.0
MAX_STEPS = 300

SPEEDS = [1, 4, 16, 64]   # Lernschritte pro Bild (Tempo)

# ---------- Mehrspieler ----------
MAX_AGENTS = 4
AGENT_COLS = [1, 2, 4, 9]          # weiss, rot, orange, cyan
LETTERS = ["A", "B", "C", "D"]
AG_EPS0 = [0.5, 0.9, 0.7, 0.95]    # Start-Neugier je Agent (Individualitaet)

# ---------- Farben ----------
COL_BG = 15
COL_WALL = 11
COL_GRID = 15
COL_GOAL = 5
COL_TEXT = 1
COL_ARROW = 1
COL_FLOOR = 6
COL_FOCUS = 1
HOOD = 11        # Kapuzen-Farbe (passt zum Wand-Lila)

# Heatmap-Rampe: kalt (blau) -> heiss (rot)
RAMP = [8, 9, 6, 7, 5, 4, 2]
RAMPN = 7

# ---------- Zustaende der App ----------
ST_TITLE = 0
ST_RUN = 1
ST_SETTINGS = 2

# ---------- Einstellbare Parameter (Menue) ----------
set_names = ["Agenten", "Alpha", "Gamma", "Decay", "Tempo"]
set_val = [2.0, 0.3, 0.9, 0.992, 2.0]
set_min = [1.0, 0.05, 0.5, 0.9, 0.0]
set_max = [4.0, 0.95, 0.99, 0.999, 3.0]
set_step = [1.0, 0.05, 0.05, 0.002, 1.0]
NSET = 5

# ---------- veraenderliche Globals ----------
g_alpha = 0.3
g_gamma = 0.9
g_decay = 0.992
n_agents = 2
speed_idx = 2
paused = False
view_mode = 0       # 0=Heatmap+Pfeile 1=Pfeile 2=nur Rennen 3=nur Heatmap
focus = 0           # welcher Agent gerade visualisiert wird
sel = 0             # Auswahl im Einstellungs-Menue
app_state = ST_TITLE

# ---------- Zustand je Agent (parallele Listen) ----------
ag_col = [START_C, START_C, START_C, START_C]
ag_row = [START_R, START_R, START_R, START_R]
ag_step = [0, 0, 0, 0]
ag_ep = [0, 0, 0, 0]
ag_best = [9999, 9999, 9999, 9999]
ag_eps = [0.5, 0.9, 0.7, 0.95]


# ---------- Q-Tabellen: pro Agent eine eigene ----------
def build_qtable():
    # Frische 48x4-Tabelle. Start mit typisiertem Element (sonst "any type").
    t = [[0.0, 0.0, 0.0, 0.0]]
    s = 1
    while s < NSTATES:
        t.append([0.0, 0.0, 0.0, 0.0])
        s += 1
    return t


q_tables = [build_qtable()]
_t = 1
while _t < MAX_AGENTS:
    q_tables.append(build_qtable())
    _t += 1


def is_wall(c, r):
    k = 0
    while k < len(WALLS):
        if WALLS[k][0] == c and WALLS[k][1] == r:
            return True
        k += 1
    return False


def best_action(ti, s):
    # Beste Aktion in Zustand s laut Tabelle ti (Agent ti).
    ba = 0
    bv = q_tables[ti][s][0]
    a = 1
    while a < 4:
        if q_tables[ti][s][a] > bv:
            bv = q_tables[ti][s][a]
            ba = a
        a += 1
    return ba


def max_q(ti, s):
    m = q_tables[ti][s][0]
    a = 1
    while a < 4:
        if q_tables[ti][s][a] > m:
            m = q_tables[ti][s][a]
        a += 1
    return m


def best_or_dash(b):
    if b >= MAX_STEPS:
        return "-"
    return str(b)


def set_disp(i):
    # Anzeige-Text eines Einstellungs-Wertes.
    if i == 0:
        return str(Math.round(set_val[0]))
    if i == 4:
        return "x" + str(SPEEDS[Math.round(set_val[4])])
    return str(set_val[i])


def reset_agents():
    # Alle Gehirne leeren, Positionen/Statistik/Neugier zuruecksetzen.
    global focus
    i = 0
    while i < MAX_AGENTS:
        s = 0
        while s < NSTATES:
            a = 0
            while a < 4:
                q_tables[i][s][a] = 0.0
                a += 1
            s += 1
        ag_col[i] = START_C
        ag_row[i] = START_R
        ag_step[i] = 0
        ag_ep[i] = 0
        ag_best[i] = 9999
        ag_eps[i] = AG_EPS0[i]
        i += 1
    if focus >= n_agents:
        focus = 0


def apply_settings():
    # Menue-Werte uebernehmen und neu starten.
    global g_alpha, g_gamma, g_decay, n_agents, speed_idx
    n_agents = Math.round(set_val[0])
    g_alpha = set_val[1]
    g_gamma = set_val[2]
    g_decay = set_val[3]
    speed_idx = Math.round(set_val[4])
    reset_agents()


def change_setting(delta):
    # Ausgewaehlten Wert um einen Schritt aendern (geclamped & gerundet).
    v = set_val[sel] + delta * set_step[sel]
    if v < set_min[sel]:
        v = set_min[sel]
    if v > set_max[sel]:
        v = set_max[sel]
    set_val[sel] = Math.round(v * 1000) / 1000


# ---------- Ein Q-Learning-Schritt fuer Agent i ----------
def learn_step(i):
    s = ag_row[i] * GW + ag_col[i]

    # epsilon-greedy
    if randint(0, 99) < ag_eps[i] * 100:
        a = randint(0, 3)
    else:
        a = best_action(i, s)

    nc = ag_col[i] + DX[a]
    nr = ag_row[i] + DY[a]
    hit_wall = False
    if nc < 0 or nc >= GW or nr < 0 or nr >= GH or is_wall(nc, nr):
        nc = ag_col[i]
        nr = ag_row[i]
        hit_wall = True

    reached_goal = (nc == GOAL_C and nr == GOAL_R)
    if reached_goal:
        reward = R_GOAL
    elif hit_wall:
        reward = R_WALL
    else:
        reward = R_STEP

    ns = nr * GW + nc
    old_q = q_tables[i][s][a]
    q_tables[i][s][a] = old_q + g_alpha * (reward + g_gamma * max_q(i, ns) - old_q)

    ag_col[i] = nc
    ag_row[i] = nr
    ag_step[i] = ag_step[i] + 1

    if reached_goal or ag_step[i] >= MAX_STEPS:
        if reached_goal and ag_step[i] < ag_best[i]:
            ag_best[i] = ag_step[i]
        ag_ep[i] = ag_ep[i] + 1
        ag_step[i] = 0
        ag_col[i] = START_C
        ag_row[i] = START_R
        ag_eps[i] = ag_eps[i] * g_decay
        if ag_eps[i] < EPS_MIN:
            ag_eps[i] = EPS_MIN


def on_update():
    if app_state != ST_RUN:
        return
    if paused:
        return
    n = SPEEDS[speed_idx]
    k = 0
    while k < n:
        i = 0
        while i < n_agents:
            learn_step(i)
            i += 1
        k += 1


game.on_update(on_update)


# ---------- eigene Linien-Funktion (Bresenham, per fill_rect) ----------
def line(screen: Image, x0: number, y0: number, x1: number, y1: number, c: number):
    dx = x1 - x0
    if dx < 0:
        dx = -dx
    dy = y1 - y0
    if dy < 0:
        dy = -dy
    sx = 1
    if x0 > x1:
        sx = -1
    sy = 1
    if y0 > y1:
        sy = -1
    err = dx - dy
    while True:
        screen.fill_rect(x0, y0, 1, 1, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err = err - dy
            x0 = x0 + sx
        if e2 < dx:
            err = err + dx
            y0 = y0 + sy


def draw_arrow(screen: Image, cx: number, cy: number, a: number):
    ex = cx + DX[a] * 6
    ey = cy + DY[a] * 6
    line(screen, cx, cy, ex, ey, COL_ARROW)
    bx = ex - DX[a] * 2
    by = ey - DY[a] * 2
    px = DY[a]
    py = DX[a]
    line(screen, ex, ey, bx + px * 2, by + py * 2, COL_ARROW)
    line(screen, ex, ey, bx - px * 2, by - py * 2, COL_ARROW)


def print_bold(screen: Image, txt: string, x: number, y: number, c: number):
    # "Fetter" Text: zweimal leicht versetzt drucken.
    screen.print(txt, x, y, c)
    screen.print(txt, x + 1, y, c)
    screen.print(txt, x, y + 1, c)


def draw_hacker(screen: Image, ox: number, oy: number):
    # Kleiner Hacker in Kapuze (Pixel-Art).
    screen.fill_rect(ox + 8, oy + 0, 14, 4, HOOD)     # Kapuzen-Krone
    screen.fill_rect(ox + 4, oy + 4, 22, 4, HOOD)     # obere Kante
    screen.fill_rect(ox + 2, oy + 8, 6, 14, HOOD)     # linke Kapuzenseite
    screen.fill_rect(ox + 22, oy + 8, 6, 14, HOOD)    # rechte Kapuzenseite
    screen.fill_rect(ox + 6, oy + 20, 18, 3, HOOD)    # Kinnband (Gesicht bleibt dunkel)
    screen.fill_rect(ox + 10, oy + 12, 3, 2, 9)       # linkes Auge (leuchtet)
    screen.fill_rect(ox + 17, oy + 12, 3, 2, 9)       # rechtes Auge
    screen.fill_rect(ox + 0, oy + 23, 30, 18, HOOD)   # Schultern / Hoodie
    screen.fill_rect(ox + 14, oy + 23, 2, 18, COL_BG)  # Reissverschluss
    screen.fill_rect(ox + 4, oy + 36, 22, 2, 9)       # Laptop-Glow
    screen.fill_rect(ox + 4, oy + 38, 22, 6, 8)       # Laptop


def draw_sad(screen: Image, ex: number, ey: number):
    # Trauriger Emoji.
    screen.fill_rect(ex + 3, ey, 10, 16, 5)
    screen.fill_rect(ex, ey + 3, 16, 10, 5)
    screen.fill_rect(ex + 1, ey + 1, 14, 14, 5)
    screen.fill_rect(ex + 4, ey + 5, 2, 2, 15)        # Augen
    screen.fill_rect(ex + 10, ey + 5, 2, 2, 15)
    line(screen, ex + 4, ey + 13, ex + 6, ey + 11, 15)  # haengender Mund
    line(screen, ex + 6, ey + 11, ex + 9, ey + 11, 15)
    line(screen, ex + 9, ey + 11, ex + 11, ey + 13, 15)
    screen.fill_rect(ex + 12, ey + 8, 1, 3, 9)        # Traene


def draw_run_hud(screen: Image):
    # Pro Agent: Buchstabe + beste Strecke, in Agentenfarbe.
    x = 1
    i = 0
    while i < n_agents:
        lbl = LETTERS[i] + best_or_dash(ag_best[i])
        screen.print(lbl, x, 1, AGENT_COLS[i])
        x = x + len(lbl) * 6 + 3
        i += 1
    info = "x" + str(SPEEDS[speed_idx])
    if paused:
        info = info + " ||"
    screen.print(info, x, 1, COL_TEXT)


# ---------- Rendering ----------
def on_render(screen, camera):
    # ===== Titelbildschirm =====
    if app_state == ST_TITLE:
        screen.fill_rect(0, 0, 160, 120, COL_BG)
        draw_hacker(screen, 14, 18)
        print_bold(screen, "HACKBERT", 56, 26, 9)
        draw_sad(screen, 120, 24)
        screen.print("ki-labyrinth", 56, 42, 1)
        screen.print("ein hackbert-projekt", 22, 78, 13)
        screen.print("A = Start", 22, 94, 5)
        screen.print("Menu = Einstellungen", 22, 104, 1)
        return

    # ===== Einstellungs-Menue =====
    if app_state == ST_SETTINGS:
        screen.fill_rect(0, 0, 160, 120, COL_BG)
        print_bold(screen, "EINSTELLUNGEN", 28, 4, 5)
        i = 0
        y = 24
        while i < NSET:
            col = 1
            if i == sel:
                col = 5
                screen.print(">", 8, y, 5)
            screen.print(set_names[i] + ": " + set_disp(i), 18, y, col)
            i += 1
            y = y + 14
        screen.print("L/R aendern  Hoch/Runter waehlen", 2, 100, 13)
        screen.print("A oder Menu = uebernehmen", 2, 110, 1)
        return

    # ===== Lauf: Labyrinth + Agenten =====
    screen.fill_rect(0, 0, 160, 10, COL_BG)
    draw_run_hud(screen)

    show_heat = (view_mode == 0 or view_mode == 3)
    show_arr = (view_mode == 0 or view_mode == 1)

    # Wertebereich der Heatmap (vom Fokus-Agenten)
    vmin = 0.0
    vmax = 0.0
    if show_heat:
        first = True
        r = 0
        while r < GH:
            c = 0
            while c < GW:
                if not is_wall(c, r):
                    v = max_q(focus, r * GW + c)
                    if first:
                        vmin = v
                        vmax = v
                        first = False
                    else:
                        if v < vmin:
                            vmin = v
                        if v > vmax:
                            vmax = v
                c += 1
            r += 1
    rng = vmax - vmin
    if rng <= 0:
        rng = 1.0

    # Zellen zeichnen
    r = 0
    while r < GH:
        c = 0
        while c < GW:
            cellx = OX + c * CELL
            celly = OY + r * CELL

            if is_wall(c, r):
                screen.fill_rect(cellx, celly, CELL, CELL, COL_WALL)
            else:
                if show_heat:
                    v = max_q(focus, r * GW + c)
                    idx = Math.round((v - vmin) / rng * (RAMPN - 1))
                    if idx < 0:
                        idx = 0
                    if idx > RAMPN - 1:
                        idx = RAMPN - 1
                    screen.fill_rect(cellx, celly, CELL, CELL, RAMP[idx])
                else:
                    screen.fill_rect(cellx, celly, CELL, CELL, COL_FLOOR)

                if show_arr and not (c == GOAL_C and r == GOAL_R):
                    draw_arrow(screen, cellx + 9, celly + 9, best_action(focus, r * GW + c))

            screen.draw_rect(cellx, celly, CELL, CELL, COL_GRID)
            c += 1
        r += 1

    # Start & Ziel
    sx = OX + START_C * CELL
    sy = OY + START_R * CELL
    screen.print("S", sx + 6, sy + 5, COL_TEXT)
    gx = OX + GOAL_C * CELL
    gy = OY + GOAL_R * CELL
    screen.draw_rect(gx, gy, CELL, CELL, COL_GOAL)
    screen.draw_rect(gx + 1, gy + 1, CELL - 2, CELL - 2, COL_GOAL)
    screen.print("Z", gx + 6, gy + 5, COL_TEXT)

    # Agenten zeichnen (Fokus bekommt einen weissen Ring)
    i = 0
    while i < n_agents:
        ax = OX + ag_col[i] * CELL + 9
        ay = OY + ag_row[i] * CELL + 9
        screen.fill_rect(ax - 3, ay - 3, 6, 6, AGENT_COLS[i])
        screen.draw_rect(ax - 3, ay - 3, 6, 6, COL_BG)
        if i == focus:
            screen.draw_rect(ax - 5, ay - 5, 10, 10, COL_FOCUS)
        i += 1


scene.set_background_color(COL_BG)
scene.create_renderable(100, on_render)


# ---------- Steuerung (haengt vom App-Zustand ab) ----------
def press_a():
    global app_state, paused
    if app_state == ST_TITLE:
        app_state = ST_RUN
    elif app_state == ST_RUN:
        paused = not paused
    else:
        apply_settings()
        app_state = ST_RUN


def press_b():
    global speed_idx
    if app_state == ST_RUN:
        speed_idx = (speed_idx + 1) % len(SPEEDS)


def press_up():
    global view_mode, sel
    if app_state == ST_RUN:
        view_mode = (view_mode + 1) % 4
    elif app_state == ST_SETTINGS:
        sel = (sel - 1 + NSET) % NSET


def press_down():
    global sel
    if app_state == ST_RUN:
        reset_agents()
    elif app_state == ST_SETTINGS:
        sel = (sel + 1) % NSET


def press_left():
    global focus
    if app_state == ST_RUN:
        focus = (focus - 1 + n_agents) % n_agents
    elif app_state == ST_SETTINGS:
        change_setting(-1)


def press_right():
    global focus
    if app_state == ST_RUN:
        focus = (focus + 1) % n_agents
    elif app_state == ST_SETTINGS:
        change_setting(1)


def press_menu():
    global app_state, sel
    if app_state == ST_SETTINGS:
        apply_settings()
        app_state = ST_RUN
    else:
        sel = 0
        app_state = ST_SETTINGS


controller.A.on_event(ControllerButtonEvent.PRESSED, press_a)
controller.B.on_event(ControllerButtonEvent.PRESSED, press_b)
controller.up.on_event(ControllerButtonEvent.PRESSED, press_up)
controller.down.on_event(ControllerButtonEvent.PRESSED, press_down)
controller.left.on_event(ControllerButtonEvent.PRESSED, press_left)
controller.right.on_event(ControllerButtonEvent.PRESSED, press_right)
controller.menu.on_event(ControllerButtonEvent.PRESSED, press_menu)


# Startaufstellung
reset_agents()
