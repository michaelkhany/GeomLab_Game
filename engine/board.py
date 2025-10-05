# Board state and random spawning

import random
from engine.entities import Player, RedNPC

class Board:
    def __init__(self, w, h, scoreValues):
        self.w = w
        self.h = h
        self.scoreValues = scoreValues
        self.players = []
        self.greens = set()
        self.reds = []
        self.rng = random.Random(42)

    def addPlayer(self, player, x, y):
        player.x, player.y = x, y
        self.players.append(player)

    def spawnGreens(self, n):
        placed = 0
        while placed < n:
            x = self.rng.randrange(self.w)
            y = self.rng.randrange(self.h)
            if (x, y) not in self.greens and not any(p.x == x and p.y == y for p in self.players):
                self.greens.add((x, y))
                placed += 1

    def spawnReds(self, n):
        for _ in range(n):
            x = self.rng.randrange(self.w)
            y = self.rng.randrange(self.h)
            # avoid direct spawn on players or greens if possible
            if any(p.x == x and p.y == y for p in self.players):
                continue
            self.reds.append(RedNPC(x, y))
