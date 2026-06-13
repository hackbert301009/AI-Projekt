# 🧠 MindMaze — ein RL-Agent lernt live das Labyrinth

> Ein **hackbert-Projekt** für MakeCode Arcade (Python).
> Schau einer künstlichen Intelligenz beim Lernen zu — in echtzeit, auf einem Retro-Bildschirm.

Mehrere Agenten starten unten links (**S**), das Ziel wartet oben rechts (**Z**), dazwischen
zwei fiese Wand-Riegel. Jeder Agent hat sein **eigenes Gehirn** (Q-Tabelle) und ist
unterschiedlich neugierig — ein **Wettrennen** ums schnellste Lernen. Per **tabularem
Q-Learning** (ε-greedy) tastet sich jeder Episode für Episode an den optimalen Weg heran.
Die gelernte **Value-Funktion** des Fokus-Agenten wird als Heatmap (kalt → heiß) eingefärbt,
seine **Strategie** als Pfeile pro Feld dargestellt.

Kein Trainingsdatensatz, keine Cloud — die ganze Intelligenz entsteht direkt auf dem Gerät.

## 🎮 Steuerung

**Titelbildschirm:** **A** = Start · **Menu** = Einstellungen

**Im Lauf:**

| Taste | Wirkung |
|-------|---------|
| **A** | Pause / Weiter |
| **B** | Lerntempo umschalten (x1 / x4 / x16 / x64) |
| **↑** | Ansicht wechseln (Heatmap+Pfeile / Pfeile / nur Rennen / nur Heatmap) |
| **↓** | Alles zurücksetzen & neu lernen |
| **← / →** | Fokus-Agent wechseln (dessen Heatmap/Pfeile gezeigt werden) |
| **Menu** | Einstellungen öffnen |

**Einstellungen:** **↑/↓** wählen · **←/→** ändern · **A**/**Menu** = übernehmen & neu starten

Einstellbar: **Anzahl Agenten** (1–4), **Alpha** (Lernrate), **Gamma** (Discount),
**Decay** (Neugier-Abkühlung) und **Tempo**.

## 🗺️ Etappenplan

Das Projekt wächst in nachvollziehbaren, einzeln testbaren Etappen:

1. **Die Welt** ✅ — Gitter, Wände, Start & Ziel
2. **Der Wanderer** ✅ — Agent bewegt sich zufällig, Kollision, Reset am Ziel
3. **Das Gehirn** ✅ — Q-Tabelle, ε-greedy, Lernregel
4. **Die Heatmap** ✅ — Value-Funktion als Farbverlauf
5. **Die Strategie** ✅ — Policy-Pfeile pro Feld
6. **Der Feinschliff** ✅ — Steuerung, HUD, Politur
7. **Der Ausbau** ✅ — Wettrennen (mehrere eigene Gehirne), Live-Tuning, Ansichts-Modi, Logo-Startbildschirm

🎉 **Alle Etappen fertig!**

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
