# Greedy green chaser with simple red avoidance

from controllers.base_controller import BaseController
from engine.geometry import manhattan

class TriangleController(BaseController):
    def decide(self, obs):
        sx = obs["self"]["pos"]["x"]
        sy = obs["self"]["pos"]["y"]

        target = self.nearestGreen(obs)
        thoughts = []

        if target:
            tx, ty = target
            thoughts.append(f"Nearest green at ({tx},{ty}) distance={manhattan((sx,sy),(tx,ty))}")
            # Avoid step if a red is adjacent and move away first
            if self.redNearby(obs):
                thoughts.append("Red nearby, performing evasive step")
                move = self.evasiveMove(obs)
                return {"move": move, "why": "Avoiding red", "thoughts": thoughts}
            move = self.stepToward(sx, sy, tx, ty)
            return {"move": move, "why": "Chasing nearest green", "thoughts": thoughts}
        else:
            thoughts.append("No green in sight, staying")
            return {"move": "STAY", "why": "Idle", "thoughts": thoughts}

    def stepToward(self, sx, sy, tx, ty):
        if abs(tx - sx) > abs(ty - sy):
            return "RIGHT" if tx > sx else "LEFT"
        else:
            return "DOWN" if ty > sy else "UP"

    def evasiveMove(self, obs):
        sx = obs["self"]["pos"]["x"]
        sy = obs["self"]["pos"]["y"]
        redCells = {(v["x"], v["y"]) for v in obs["vision"] if v["t"] == "RED"}
        candidates = [("UP", (sx, sy - 1)), ("DOWN", (sx, sy + 1)), ("LEFT", (sx - 1, sy)), ("RIGHT", (sx + 1, sy)), ("STAY", (sx, sy))]
        # pick farthest from any red
        def minDistToRed(pos):
            if not redCells:
                return 999
            return min(manhattan(pos, r) for r in redCells)
        candidates.sort(key=lambda c: -minDistToRed(c[1]))
        return candidates[0][0]
