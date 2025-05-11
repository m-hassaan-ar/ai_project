# Nine Men’s Morris – Python CLI Edition with Time‑Bomb Variant

A fully‑playable command‑line implementation of **Nine Men’s Morris** that pits a human player (`O`) against an AI opponent (`X`).  In addition to the classic rules, this variant introduces **time‑bomb power‑ups** and an **undo** system, giving the ancient board game a tactical twist – all in fewer than 1 000 lines of pure Python.

> **Status:** Single‑file prototype ready for testing & feedback
> **License:** MIT
> **Python version:** 3.8 +

---

## Features

| Category        | Details                                                                                                                                                                                                              |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Gameplay        | All three phases (placement, sliding, flying) faithfully reproduced; mills are detected automatically.                                                                                                               |
| Power‑ups       | Each side gets **one time‑bomb** per match.  Arming a bomb starts a 3‑turn countdown; when it hits 0 it explodes, removing *every* adjacent piece (friend or foe) and disarming any other bombs caught in the blast. |
| AI              | Depth‑adaptive **alpha–beta pruning** with a custom heuristic that values piece count, mills, mobility and near‑mill setups citeturn0file0.                                                                       |
| Undo            | Human player may undo up to **three turns** per game (including bomb placement).                                                                                                                                     |
| Quality‑of‑life | Clear ASCII board with ANSI color‑coding for armed bombs, last‑move log, coordinate helper, and input validation.                                                                                                    |
| Zero deps       | Pure standard‑library Python—no external packages required.                                                                                                                                                          |

---

## Quick Start

```bash
# Clone / download this repository
$ git clone https://github.com/m-hassaan-ar/ai_project.git
$ cd nine‑mens‑morris-cli

# (Optional) create & activate a virtualenv
$ python -m venv .venv && source .venv/bin/activate

# Run the game
$ python main.py
```

> **Windows users:** The code clears the screen with `cls`; on Unix‑like systems it uses `clear`.  ANSI colors work natively on modern Windows 10+ terminals – enable *Virtual Terminal* processing if you’re on an older console.

---

## How to Play

### Board Coordinates

```
    A   B   C   D   E   F   G
7   ·-----------·-----------·
    |           |           |
6   |   ·-------·-------·   |
    |   |       |       |   |
5   |   |   ·---·---·   |   |
    |   |   |       |   |   |
4   ·---·---·       ·---·---·
    |   |   |       |   |   |
3   |   |   ·---·---·   |   |
    |   |       |       |   |
2   |   ·-------·-------·   |
    |           |           |
1   ·-----------·-----------·
    A   B   C   D   E   F   G
```

Each intersection has a coordinate like **A7**, **D4**, **G1**.  Type these when prompted.

### Phases & Actions

| Phase         | Trigger                                        | Allowed actions                                                 |
| ------------- | ---------------------------------------------- | --------------------------------------------------------------- |
| 1 – *Placing* | Until each side has placed 9 pieces            | **P** – place a piece on any empty point.                       |
| 2 – *Sliding* | Both sides finished placing and have >3 pieces | **M** – move one of your pieces to an **adjacent** empty point. |
| 3 – *Flying*  | A side drops to ≤3 pieces                      | **M** – move one of your pieces to **any** empty point ("fly"). |

Additional actions (any phase):

* **B** – Arm a time‑bomb on one of your pieces (once per game).
* **Undo** – After your move you may press **Y** when prompted to rewind (max 3).

Forming a *mill* (three in a row) lets you immediately remove one opponent piece that is **not** already in a mill – unless all of theirs are.

---

## File Layout

```
📦 nine‑mens‑morris-cli/
 ├─ main.py        # 🔥  All of the game logic, AI and CLI I/O
 └─ README.md        # 📖  This file
```

Feel free to split `main.py` into modules once the design stabilises (e.g. `game.py`, `ai.py`, `ui.py`).

---

## Roadmap / Ideas

* [ ] **Configurable board themes** (Unicode, colour schemes).
* [ ] **PvP network mode** using sockets.
* [ ] **Stronger AI** via iterative deepening + transposition tables.
* [ ] **Packaging**: publish to PyPI, `pip install morris-cli`.
* [ ] **CI workflow** with unit tests for mill detection & move validation.

Feel free to open an issue or PR with suggestions!

---

## Contributing

1. Fork the repo & create your feature branch (`git checkout -b feature/awesome`)
2. Commit your changes (`git commit -am 'Add awesome feature'`)
3. Push to the branch (`git push origin feature/awesome`)
4. Open a Pull Request

Please run `python -m unittest` before submitting.

---

## License

This project is licensed under the **MIT License** – see the `LICENSE` file for details.
