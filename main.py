# =====================================================================
#  __  __ _         _ __  __
# |  \/  (_)_ _  __| |  \/  |__ _ ______
# | |\/| | | ' \/ _` | |\/| / _` |_ / -_)
# |_|  |_|_|_||_\__,_|_|  |_\__,_/__\___|   ein hackbert-projekt
# =====================================================================
#  Ein RL-Agent lernt LIVE den Weg durchs Labyrinth.
#  Etappe 4 / 6:  "Die Heatmap"  --  jetzt wird das Wissen sichtbar!
#
#  Der Agent lernt weiter per Q-Learning (wie in Etappe 3). Neu: wir
#  faerben jedes Feld nach seinem Value ein -- das ist der beste
#  Q-Wert des Feldes, also "wie gut ist es, hier zu stehen?".
#  Kalt (blau) = weit weg / schlecht, heiss (rot) = nah am Ziel / gut.
#
#  So entsteht live ein Farbverlauf, der vom Ziel aus durchs ganze
#  Labyrinth "ausstrahlt". Genau das hat der Agent gelernt.  -- hackbert
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
STEPS_PER_FRAME = 8    # so viele Lernschritte pro Bild -> sichtbar schnelles Lernen

# ---------- Farben (MakeCode-Arcade-Palette) ----------
COL_BG = 15      # schwarz
COL_WALL = 11    # lila  -- die Mauern
COL_GRID = 15    # schwarz -- dünne Gitterlinien
COL_GOAL = 5     # gelb
COL_AGENT = 1    # weiss -- unser Agent
COL_TEXT = 1     # weiss

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


# Pro Bild gleich mehrere Lernschritte -> das Lernen geht sichtbar voran.
def on_update():
    i = 0
    while i < STEPS_PER_FRAME:
        learn_step()
        i += 1


game.on_update(on_update)


# ---------- Rendering: das ganze Spielfeld selbst malen ----------
def on_render(screen, camera):
    # HUD-Leiste oben: Episode, beste Strecke, aktuelle Neugier (in %).
    screen.fill_rect(0, 0, 160, 10, COL_BG)
    hud = "E4 Ep:" + str(episode) + " best:" + best_str()
    hud = hud + " eps:" + str(Math.round(epsilon * 100))
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
