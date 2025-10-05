# GeomLab 1

**GeomLab 1** is a modular, turn-based 2D arcade game built with **Python** and **Pygame**.

Three geometric agents compete on a fog-covered grid:
- 🟦 **Triangle** - heuristic AI.
- 🟨 **Rectangle** - powered by **Synchange LLM**, reasoning with rules and past outcomes.
- 🟪 **Pentagon** - human-controlled using keyboard input.

Players aim to collect green circles (+1) and avoid red hazards (−1).  
Each agent’s *thoughts*, *moves*, and *reasons* appear live in the side panel.

---

## 🎮 Gameplay

- 2D grid world with fog-of-war (limited sight range).
- Turn order: Triangle → Rectangle → Pentagon → NPCs.
- Red circles move slowly; greens are stationary.
- Game ends when all greens are collected or after the max rounds.
- Highest score wins.

---

## 🧠 Agent Controllers

| Agent | Control Type | Description |
|-------|---------------|-------------|
| **Triangle** | Heuristic | Moves greedily toward the nearest green, avoids nearby red. |
| **Rectangle** | Synchange LLM | Uses game rules + decision history to reason each move. Retries until valid JSON response. |
| **Pentagon** | Human | Controlled with keyboard (Arrow keys / WASD). |

Each controller is a separate class following a unified interface:
```python
decide(observation: dict) -> {"move": "UP|DOWN|LEFT|RIGHT|STAY", "why": str, "thoughts": [str]}
````

---

## ⚙️ Installation

```bash
git clone https://github.com/michaelkhany/GeomLab_Game.git
cd GeomLab_Game
python -m venv .venv
# Activate venv (Windows)
.venv\Scripts\activate
# Activate venv (Linux/Mac)
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

---

## ⌨️ Controls

* **SPACE** → Pause / Resume
* **R** → Restart
* **Arrow keys / WASD** → Move the **Pentagon** when it’s your turn

---

## 🧩 Structure

```
GeomLab_Game/
│
├── main.py
├── settings.py
├── requirements.txt
│
├── engine/
│   ├── game.py          # Main loop and logic
│   ├── board.py         # Grid state and spawns
│   ├── renderer.py      # Drawing + fog-of-war
│   ├── vision.py        # Observation extraction
│   ├── logger.py        # Thought logs
│   ├── entities.py      # Players and NPCs
│   └── geometry.py      # Math helpers
│
└── controllers/
    ├── triangle_controller.py
    ├── rectangle_controller.py   # Synchange LLM agent
    ├── human_controller.py       # Keyboard agent
    ├── base_controller.py
    └── synchange_llm.py          # API client
```

---

## 🧩 Rectangle LLM Logic

* Receives current observation and short history of its previous moves and score deltas.
* Sends a structured prompt to **Synchange LLM**.
* Retries until a valid JSON decision is received.
* Logs each move with reasoning and consequences.
* Falls back to `STAY` if all retries fail safely.

---

## 🧍 Pentagon Human Mode

* Controlled with Arrow keys or WASD.
* The game pauses automatically on the Pentagon’s turn until a move key is pressed.

---

## 🪄 Settings

All parameters (board size, sight radius, number of items, timing, etc.) are configurable in **`settings.py`**.

---

## 🪶 License

MIT License © 2025 Michael Bidollahkhani

---

## 🌐 Credits

Developed by **Michael Bidollahkhani**
University of Göttingen - Synchange Lab
[https://synchange.com](https://synchange.com)

