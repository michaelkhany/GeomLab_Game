# Entities for players and NPCs

from engine.geometry import DIRS, clamp

class Player:
    # AgentId examples: "triangle", "rectangle", "pentagon"
    def __init__(self, agentId, color, controller):
        self.agentId = agentId
        self.color = color
        self.controller = controller
        self.x = 0
        self.y = 0
        self.score = 0

    def applyMove(self, board, move):
        dx, dy = DIRS.get(move, (0, 0))
        nx = clamp(self.x + dx, 0, board.w - 1)
        ny = clamp(self.y + dy, 0, board.h - 1)

        # If a player already occupies nx,ny, we allow moves because turns are sequential
        self.x, self.y = nx, ny

        # Resolve pickups and hazards
        # Greens
        if (self.x, self.y) in board.greens:
            board.greens.remove((self.x, self.y))
            self.score += board.scoreValues["GREEN"]

        # Reds
        for r in board.reds:
            if r.x == self.x and r.y == self.y:
                self.score += board.scoreValues["RED"]
                break

class RedNPC:
    def __init__(self, x, y, color=(200, 50, 50)):
        self.x = x
        self.y = y
        self.color = color

    def tryMove(self, board, rng, moveProb=0.5):
        # 50% chance to move by default
        if rng.random() > moveProb:
            return
        dirs = [(0,1),(0,-1),(1,0),(-1,0),(0,0)]
        rng.shuffle(dirs)
        for dx, dy in dirs:
            nx = min(max(self.x + dx, 0), board.w - 1)
            ny = min(max(self.y + dy, 0), board.h - 1)
            # allow overlap with reds, avoid leaving board
            self.x, self.y = nx, ny
            break
