# =====================================================================
#  __  __ _         _ __  __
# |  \/  (_)_ _  __| |  \/  |__ _ ______
# | |\/| | | ' \/ _` | |\/| / _` |_ / -_)
# |_|  |_|_|_||_\__,_|_|  |_\__,_/__\___|   ein hackbert-projekt
# =====================================================================
#  Ein RL-Agent lernt LIVE den Weg durchs Labyrinth.
#  Etappe 6 / 6:  "Der Feinschliff"  --  jetzt darfst DU mitspielen!
#
#  Der Agent lernt wie gehabt (Q-Learning, Heatmap, Policy-Pfeile).
#  Neu ist die Steuerung -- du kannst dem Lernen live beim Zusehen
#  zuschrauben:
#
#     A      = Pause / Weiter
#     B      = Lerntempo umschalten (x1 / x4 / x16 / x64)
#     Hoch   = Policy-Pfeile ein- / ausblenden
#     Runter = alles vergessen und neu lernen (Reset)
#
#  Fertig ist das Werk. Viel Spass beim Zuschauen, wie aus Chaos
#  Koennen wird.  -- hackbert
# =====================================================================

# ---------- Welt-Geometrie ----------
GW = 8          # Spalten
GH = 6          # Zeilen
NSTATES = 48    # Anzahl Felder = GW * GH  (jedes Feld ist ein "Zustand")
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
# DX/DY sagen, wie sich Spalte/Zeile bei jeder Aktion verändern.
DX = [0, 0, -1, 1]
DY = [-1, 1, 0, 0]

# ---------- Lern-Stellschrauben (die "Hyperparameter") ----------
ALPHA = 0.3      # Lernrate: wie stark ein neuer Wert die alte Schätzung korrigiert
GAMMA = 0.9      # Discount: wie wichtig zukünftige Belohnungen sind (0=gierig, 1=weitsichtig)
EPS_START = 0.9  # Start-Neugier: anfangs zu 90% zufällig ausprobieren
EPS_MIN = 0.05   # Rest-Neugier: nie ganz aufhören zu experimentieren
EPS_DECAY = 0.992  # Neugier schrumpft pro Episode um diesen Faktor

# Belohnungen: das Herz des Lernens. Der Agent maximiert die Summe.
R_GOAL = 100.0   # Ziel erreicht -> dicke Belohnung
R_WALL = -5.0    # gegen Wand/Rand -> kleine Strafe
R_STEP = -1.0    # jeder Schritt kostet -> drängt zum kurzen Weg

MAX_STEPS = 300        # Notbremse: dauert eine Episode zu lang, brechen wir ab

# Lerntempo: so viele Lernschritte pro Bild. Mit B schaltet man durch.
SPEEDS = [1, 4, 16, 64]

# ---------- Farben (MakeCode-Arcade-Palette) ----------
COL_BG = 15      # schwarz
COL_WALL = 11    # lila  -- die Mauern
COL_GRID = 15    # schwarz -- dünne Gitterlinien
COL_GOAL = 5     # gelb
COL_AGENT = 1    # weiss -- unser Agent
COL_TEXT = 1     # weiss
COL_ARROW = 1    # weiss -- Policy-Pfeile

# Heatmap-Rampe: von kalt (blau) nach heiss (rot). Den Value eines Feldes
# bilden wir auf einen dieser Farbindizes ab.
RAMP = [8, 9, 6, 7, 5, 4, 2]   # blau, hellblau, teal, gruen, gelb, orange, rot
RAMPN = 7

# ---------- Laufzeit-Zustand ----------
agent_col = START_C
agent_row = START_R
episode = 0          # wie viele Anläufe der Agent schon hinter sich hat
step_in_ep = 0       # Schritte in der aktuellen Episode
epsilon = EPS_START  # aktuelle Experimentierfreude
best_steps = 9999    # kürzeste je gefundene Strecke zum Ziel

# Steuerung (per Tasten umschaltbar)
paused = False       # A pausiert das Lernen
show_arrows = True   # Hoch blendet die Policy-Pfeile ein/aus
speed_idx = 2        # B schaltet das Tempo (Index in SPEEDS), Start: x16


# ---------- Q-Tabelle: das Gedächtnis des Agenten ----------
# q_table[zustand][aktion] = geschätzter Wert (erwartete künftige Belohnung).
# Wichtig fürs statische Python von MakeCode: wir starten die Liste mit einem
# konkreten, typisierten Element (eine Zeile aus 4 Zahlen). Eine leere Liste []
# hätte keinen erkennbaren Typ -> Fehler "implicitly has an any type".
# Danach hängen wir die restlichen Zeilen an. Start: überall 0 -> er weiss nichts.
q_table = [[0.0, 0.0, 0.0, 0.0]]
_s = 1
while _s < NSTATES:
    q_table.append([0.0, 0.0, 0.0, 0.0])
    _s += 1


def state_of(c, r):
    # Macht aus den Koordinaten (Spalte, Zeile) eine eindeutige Zustandsnummer.
    return r * GW + c


def is_wall(c, r):
    # Schaut nach, ob auf (c, r) eine Mauer steht.
    k = 0
    while k < len(WALLS):
        if WALLS[k][0] == c and WALLS[k][1] == r:
            return True
        k += 1
    return False


def best_action(s):
    # Liefert die Aktion mit dem höchsten Q-Wert im Zustand s (die "gierige" Wahl).
    ba = 0
    bv = q_table[s][0]
    a = 1
    while a < 4:
        if q_table[s][a] > bv:
            bv = q_table[s][a]
            ba = a
        a += 1
    return ba


def max_q(s):
    # Liefert den besten Q-Wert im Zustand s (wie gut ist dieses Feld bestenfalls?).
    m = q_table[s][0]
    a = 1
    while a < 4:
        if q_table[s][a] > m:
            m = q_table[s][a]
        a += 1
    return m


def best_str():
    # Hübsche Anzeige für "best": vor dem ersten Treffer ein "-".
    if best_steps >= MAX_STEPS:
        return "-"
    return str(best_steps)


# ---------- Der eigentliche Lernschritt (Q-Learning) ----------
def learn_step():
    global agent_col, agent_row, episode, step_in_ep, epsilon, best_steps

    s = state_of(agent_col, agent_row)

    # 1) Aktion wählen -- epsilon-greedy:
    #    Mit Wahrscheinlichkeit epsilon zufällig (erkunden), sonst die
    #    aktuell beste bekannte Aktion (ausnutzen, was man schon weiss).
    if randint(0, 99) < epsilon * 100:
        a = randint(0, 3)
    else:
        a = best_action(s)

    # 2) Aktion ausführen und schauen, wo man landet.
    nc = agent_col + DX[a]
    nr = agent_row + DY[a]
    hit_wall = False
    if nc < 0 or nc >= GW or nr < 0 or nr >= GH or is_wall(nc, nr):
        nc = agent_col      # gegen Wand/Rand -> man bleibt stehen
        nr = agent_row
        hit_wall = True

    reached_goal = (nc == GOAL_C and nr == GOAL_R)

    # 3) Belohnung bestimmen.
    if reached_goal:
        reward = R_GOAL
    elif hit_wall:
        reward = R_WALL
    else:
        reward = R_STEP

    # 4) Q-Wert aktualisieren -- die Bellman-Gleichung:
    #    neuer Wert = alter Wert + ALPHA * (Belohnung + GAMMA * bester Folgewert - alter Wert)
    #    Der Klammerausdruck ist der "Lernfehler": lag die Schätzung daneben,
    #    wird kräftig korrigiert; war sie gut, kaum.
    ns = state_of(nc, nr)
    old_q = q_table[s][a]
    q_table[s][a] = old_q + ALPHA * (reward + GAMMA * max_q(ns) - old_q)

    # 5) In den neuen Zustand wechseln.
    agent_col = nc
    agent_row = nr
    step_in_ep += 1

    # 6) Episode zu Ende? (Ziel erreicht oder Notbremse) -> Bilanz & Neustart.
    if reached_goal or step_in_ep >= MAX_STEPS:
        if reached_goal and step_in_ep < best_steps:
            best_steps = step_in_ep
        episode += 1
        step_in_ep = 0
        agent_col = START_C
        agent_row = START_R
        # Neugier abkühlen: mit jeder Episode etwas weniger Zufall.
        epsilon = epsilon * EPS_DECAY
        if epsilon < EPS_MIN:
            epsilon = EPS_MIN


# Pro Bild mehrere Lernschritte -> das Lernen geht sichtbar voran.
# Ist pausiert, machen wir nichts; sonst so viele Schritte wie das Tempo sagt.
def on_update():
    if paused:
        return
    n = SPEEDS[speed_idx]
    i = 0
    while i < n:
        learn_step()
        i += 1


game.on_update(on_update)


# ---------- Eigene Linien-Funktion (Bresenham) ----------
# MakeCodes Image-Objekt hat in dieser Version weder draw_line noch set_pixel.
# fill_rect gibt es aber sicher -> ein 1x1-Rechteck IST ein einzelnes Pixel.
# Damit setzen wir die Linie Pixel fuer Pixel (klassischer Bresenham,
# funktioniert fuer waagerecht/senkrecht/diagonal).
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
        screen.fill_rect(x0, y0, 1, 1, c)   # 1x1-Rechteck = ein Pixel
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err = err - dy
            x0 = x0 + sx
        if e2 < dx:
            err = err + dx
            y0 = y0 + sy


# ---------- Policy-Pfeil: zeigt die beste Aktion eines Feldes ----------
def draw_arrow(screen: Image, cx: number, cy: number, a: number):
    # Kurzer Strich vom Zellmittelpunkt (cx, cy) in Richtung der Aktion a.
    ex = cx + DX[a] * 6
    ey = cy + DY[a] * 6
    line(screen, cx, cy, ex, ey, COL_ARROW)
    # Pfeilspitze: zwei kurze Striche von der Spitze schräg zurück.
    # (px, py) steht senkrecht zur Pfeilrichtung -> bildet das "V".
    bx = ex - DX[a] * 2
    by = ey - DY[a] * 2
    px = DY[a]
    py = DX[a]
    line(screen, ex, ey, bx + px * 2, by + py * 2, COL_ARROW)
    line(screen, ex, ey, bx - px * 2, by - py * 2, COL_ARROW)


# ---------- Rendering: das ganze Spielfeld selbst malen ----------
def on_render(screen, camera):
    # HUD-Leiste oben: Episode, beste Strecke, aktuelle Neugier (in %).
    screen.fill_rect(0, 0, 160, 10, COL_BG)
    hud = "Ep:" + str(episode) + " b:" + best_str()
    hud = hud + " e:" + str(Math.round(epsilon * 100))
    hud = hud + " x" + str(SPEEDS[speed_idx])
    if paused:
        hud = hud + " ||"
    screen.print(hud, 1, 1, COL_TEXT)

    # --- Wertebereich der Heatmap bestimmen ---
    # Wir brauchen kleinsten und groessten Value aller begehbaren Felder, um
    # die Farben relativ dazu zu skalieren (sonst waere am Anfang alles gleich).
    vmin = 0.0
    vmax = 0.0
    first = True
    r = 0
    while r < GH:
        c = 0
        while c < GW:
            if not is_wall(c, r):
                v = max_q(state_of(c, r))
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
        rng = 1.0   # noch ist alles gleich (Start) -> Division durch 0 vermeiden

    # --- Alle Zellen durchgehen und nach Value einfärben ---
    r = 0
    while r < GH:
        c = 0
        while c < GW:
            cellx = OX + c * CELL
            celly = OY + r * CELL

            if is_wall(c, r):
                screen.fill_rect(cellx, celly, CELL, CELL, COL_WALL)
            else:
                # Value (0..1 normiert) auf einen Rampen-Index abbilden.
                # Math.round rundet zur naechsten Farbstufe (int() erwartet hier
                # einen String, daher nehmen wir Math.round zum Runden von Zahlen).
                v = max_q(state_of(c, r))
                idx = Math.round((v - vmin) / rng * (RAMPN - 1))
                if idx < 0:
                    idx = 0
                if idx > RAMPN - 1:
                    idx = RAMPN - 1
                screen.fill_rect(cellx, celly, CELL, CELL, RAMP[idx])

                # Policy-Pfeil zeichnen (falls eingeblendet und nicht das Ziel).
                if show_arrows and not (c == GOAL_C and r == GOAL_R):
                    draw_arrow(screen, cellx + 9, celly + 9, best_action(state_of(c, r)))

            # dünne Gitterlinie drumherum
            screen.draw_rect(cellx, celly, CELL, CELL, COL_GRID)
            c += 1
        r += 1

    # Start markieren (nur Buchstabe "S", damit die Heatmap sichtbar bleibt)
    sx = OX + START_C * CELL
    sy = OY + START_R * CELL
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


# ---------- Hackbert-Startbildschirm ----------
# Kurzer Gruss zum Start; nach Tastendruck laeuft das Lernen los. Bewusst VOR
# der Tasten-Registrierung, damit der A-Druck zum Schliessen nicht gleich
# die Pause ausloest.
game.splash("MindMaze", "ein hackbert-projekt")


# ---------- Steuerung ----------
def toggle_pause():
    global paused
    paused = not paused


def cycle_speed():
    global speed_idx
    speed_idx = (speed_idx + 1) % len(SPEEDS)


def toggle_arrows():
    global show_arrows
    show_arrows = not show_arrows


def reset_learning():
    # Alles vergessen: Q-Tabelle auf 0, Statistik & Neugier zuruecksetzen.
    global episode, step_in_ep, epsilon, best_steps, agent_col, agent_row
    s = 0
    while s < NSTATES:
        a = 0
        while a < 4:
            q_table[s][a] = 0.0
            a += 1
        s += 1
    episode = 0
    step_in_ep = 0
    epsilon = EPS_START
    best_steps = 9999
    agent_col = START_C
    agent_row = START_R


controller.A.on_event(ControllerButtonEvent.PRESSED, toggle_pause)
controller.B.on_event(ControllerButtonEvent.PRESSED, cycle_speed)
controller.up.on_event(ControllerButtonEvent.PRESSED, toggle_arrows)
controller.down.on_event(ControllerButtonEvent.PRESSED, reset_learning)
