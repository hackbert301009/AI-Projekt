# 🧠 MindMaze — ein RL-Agent lernt live das Labyrinth

> Ein **hackbert-Projekt** für MakeCode Arcade (Python).
> Schau einer künstlichen Intelligenz beim Lernen zu — in echtzeit, auf einem Retro-Bildschirm.

Ein Agent steht unten links (**S**), das Ziel wartet oben rechts (**Z**), dazwischen zwei
fiese Wand-Riegel. Per **tabularem Q-Learning** (ε-greedy) tastet sich der Agent Episode
für Episode an den optimalen Weg heran. Seine gelernte **Value-Funktion** wird als
Heatmap (kalt → heiß) eingefärbt, seine **Strategie** als Pfeile pro Feld dargestellt.

Kein Trainingsdatensatz, keine Cloud — die ganze Intelligenz entsteht direkt auf dem Gerät.

## 🎮 Steuerung (ab Etappe 6)

| Taste | Wirkung |
|-------|---------|
| **A** | Pause / Weiter |
| **B** | Lerntempo umschalten |
| **↑** | Policy-Pfeile ein / aus |
| **↓** | Zurücksetzen & neu lernen |

## 🗺️ Etappenplan

Das Projekt wächst in nachvollziehbaren, einzeln testbaren Etappen:

1. **Die Welt** ✅ — Gitter, Wände, Start & Ziel
2. **Der Wanderer** ✅ — Agent bewegt sich zufällig, Kollision, Reset am Ziel
3. **Das Gehirn** — Q-Tabelle, ε-greedy, Lernregel
4. **Die Heatmap** — Value-Funktion als Farbverlauf
5. **Die Strategie** — Policy-Pfeile pro Feld
6. **Der Feinschliff** — Steuerung, HUD, Politur

## ✏️ Dieses Projekt in MakeCode bearbeiten

* öffne [https://arcade.makecode.com/](https://arcade.makecode.com/)
* **Importieren** → **Importiere URL**
* **https://github.com/hackbert301009/AI-Projekt** einfügen und importieren
* mit dem **GitHub-Symbol** (unten links) holst du neue Etappen per **„Änderungen abrufen"**

## 🧩 Als Erweiterung verwenden

Dieses Repository kann als **Erweiterung** in MakeCode hinzugefügt werden:

* öffne [https://arcade.makecode.com/](https://arcade.makecode.com/)
* **Neues Projekt** → unter dem Zahnrad-Menü auf **Erweiterungen**
* nach **https://github.com/hackbert301009/AI-Projekt** suchen und importieren

---

#### Metadaten (verwendet für Suche, Rendering)

* for PXT/arcade
<script src="https://makecode.com/gh-pages-embed.js"></script><script>makeCodeRender("{{ site.makecode.home_url }}", "{{ site.github.owner_name }}/{{ site.github.repository_name }}");</script>
