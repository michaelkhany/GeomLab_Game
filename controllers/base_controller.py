# Controller base and utilities for path intent

from engine.geometry import manhattan

class BaseController:
    # Decide must return:
    # { "move": "UP|DOWN|LEFT|RIGHT|STAY", "why": str, "thoughts": [str, ...] }
    def decide(self, observation):
        raise NotImplementedError

    # Helper: find nearest visible green
    def nearestGreen(self, obs):
        sx = obs["self"]["pos"]["x"]
        sy = obs["self"]["pos"]["y"]
        greens = [(v["x"], v["y"]) for v in obs["vision"] if v["t"] == "GREEN"]
        if not greens:
            return None
        greens.sort(key=lambda g: manhattan((sx, sy), g))
        return greens[0]

    # Helper: are we threatened by adjacent red
    def redNearby(self, obs):
        sx = obs["self"]["pos"]["x"]
        sy = obs["self"]["pos"]["y"]
        reds = [(v["x"], v["y"]) for v in obs["vision"] if v["t"] == "RED"]
        for rx, ry in reds:
            if manhattan((sx, sy), (rx, ry)) <= 1:
                return True
        return False
