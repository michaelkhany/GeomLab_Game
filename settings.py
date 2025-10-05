# GeomLab 1 — global settings

WINDOW_W = 1200
WINDOW_H = 720

GRID_W = 40
GRID_H = 24
CELL = 24  # pixel size of a grid cell

PANEL_W = 420  # right-side panel for thoughts and logs

BG_COLOR = (20, 22, 26)
GRID_COLOR = (40, 44, 52)
FOG_COLOR = (80, 80, 80, 180)  # RGBA for fog overlay

SIGHT_RANGE = 5
MAX_ROUNDS = 200

NUM_GREENS = 30
NUM_REDS = 10
RED_MOVE_PROB = 0.5  # 50% chance to move each round

SCORES = {
    "GREEN": 1,
    "RED": -1
}

FPS = 60  # render FPS
TURN_DELAY_MS = 150  # pause between individual decisions for readability

FONT_NAME = "consolas"  # fallback handled by pygame if missing
LOG_HISTORY_PER_AGENT = 120  # number of lines to keep in memory
