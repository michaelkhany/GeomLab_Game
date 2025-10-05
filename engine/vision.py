# Fog-limited observation extraction

from settings import SIGHT_RANGE
from engine.geometry import manhattan

# Tile tags
EMPTY = "EMPTY"
GREEN = "GREEN"
RED = "RED"
PLAYER = "PLAYER"

def extractObservation(board, activePlayer, tick):
    sx, sy = activePlayer.x, activePlayer.y
    vision = []
    for y in range(board.h):
        for x in range(board.w):
            if manhattan((sx, sy), (x, y)) <= SIGHT_RANGE:
                tag, meta = classify(board, x, y)
                if tag != EMPTY:
                    item = {"x": x, "y": y, "t": tag}
                    if tag == PLAYER:
                        item["id"] = meta  # agentId
                    vision.append(item)

    obs = {
        "tick": tick,
        "self": {"id": activePlayer.agentId, "pos": {"x": sx, "y": sy}, "score": activePlayer.score},
        "vision": vision,
        "bounds": {"w": board.w, "h": board.h},
        "rules": {"sight": SIGHT_RANGE, "moveSet": ["UP", "DOWN", "LEFT", "RIGHT", "STAY"]},
        "stats": {"remainingGreens": len(board.greens)}
    }
    return obs

def classify(board, x, y):
    # Priority: players, reds, greens
    for p in board.players:
        if p.x == x and p.y == y:
            return (PLAYER, p.agentId)
    for r in board.reds:
        if r.x == x and r.y == y:
            return (RED, None)
    for g in board.greens:
        if g[0] == x and g[1] == y:
            return (GREEN, None)
    return (EMPTY, None)
