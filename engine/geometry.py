# Utility geometry helpers

def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v

DIRS = {
    "UP":    (0, -1),
    "DOWN":  (0, 1),
    "LEFT":  (-1, 0),
    "RIGHT": (1, 0),
    "STAY":  (0, 0)
}

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
