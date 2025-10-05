# Value-based heuristic: score = greensNear - redsNear

from controllers.base_controller import BaseController
from engine.geometry import manhattan

class PentagonController(BaseController):
    def decide(self, obs):
        sx = obs["self"]["pos"]["x"]
        sy = obs["self"]["pos"]["y"]
        thoughts = []

        moves = ["UP", "DOWN", "LEFT", "RIGHT", "STAY"]
        scores = []
        for mv in moves:
            px, py = self.applyMovePreview(sx, sy, mv)
            val = self.localValue(obs, (px, py))
            scores.append((val, mv))
            thoughts.append(f"mv={mv} -> value={val:.2f}")

        scores.sort(reverse=True)
        bestVal, bestMove = scores[0]
        why = f"Maximizing local value {bestVal:.2f}"
        return {"move": bestMove, "why": why, "thoughts": thoughts}

    def applyMovePreview(self, x, y, mv):
        if mv == "UP": return (x, y - 1)
        if mv == "DOWN": return (x, y + 1)
        if mv == "LEFT": return (x - 1, y)
        if mv == "RIGHT": return (x + 1, y)
        return (x, y)

    def localValue(self, obs, pos):
        greens = [(v["x"], v["y"]) for v in obs["vision"] if v["t"] == "GREEN"]
        reds = [(v["x"], v["y"]) for v in obs["vision"] if v["t"] == "RED"]
        gScore = 0.0
        rPenalty = 0.0
        for gx, gy in greens:
            d = max(1, manhattan(pos, (gx, gy)))
            gScore += 1.2 / d
        for rx, ry in reds:
            d = max(1, manhattan(pos, (rx, ry)))
            rPenalty += 1.0 / d
        return gScore - rPenalty
