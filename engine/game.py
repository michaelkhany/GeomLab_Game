# Core game loop and turn system

import random
import pygame
from settings import *
from engine.board import Board
from engine.renderer import drawBoard, drawPanel
from engine.vision import extractObservation
from engine.entities import Player
from engine.logger import ThoughtsLogger

# Controllers
from controllers.triangle_controller import TriangleController
from controllers.rectangle_controller import RectangleController   # now LLM
from controllers.human_controller import HumanController           # human pentagon

class Game:
    def __init__(self):
        pygame.init()
        totalW = GRID_W * CELL + PANEL_W
        totalH = GRID_H * CELL
        self.screen = pygame.display.set_mode((totalW, totalH))
        pygame.display.set_caption("GeomLab 1")
        self.clock = pygame.time.Clock()
        self.fontSmall = pygame.font.SysFont(FONT_NAME, 16)
        self.fontMono = pygame.font.SysFont(FONT_NAME, 20)

        self.logger = ThoughtsLogger()
        self.tick = 0
        self.paused = False

        self.board = Board(GRID_W, GRID_H, SCORES)
        rng = self.board.rng

        # Controllers
        triCtrl = TriangleController()
        recCtrl = RectangleController()   # ← Synchange LLM agent
        penCtrl = HumanController()       # ← Human

        # Players
        tri = Player("triangle", (90, 190, 255), triCtrl)
        rec = Player("rectangle", (255, 200, 90), recCtrl)
        pen = Player("pentagon", (180, 120, 255), penCtrl)

        # Spawn players
        self.board.addPlayer(tri, 2, 2)
        self.board.addPlayer(rec, GRID_W - 3, 2)
        self.board.addPlayer(pen, 2, GRID_H - 3)

        self.board.spawnGreens(NUM_GREENS)
        self.board.spawnReds(NUM_REDS)

        self.turnOrder = [tri, rec, pen]
        self.activeIdx = 0

        self.redRng = random.Random(999)

    def gameEnded(self):
        return len(self.board.greens) == 0 or self.tick >= MAX_ROUNDS

    def npcPhase(self):
        for r in self.board.reds:
            r.tryMove(self.board, self.redRng, RED_MOVE_PROB)

    def stepTurn(self):
        p = self.turnOrder[self.activeIdx]

        # If human turn and no move yet -> wait
        from controllers.human_controller import HumanController
        if isinstance(p.controller, HumanController) and not p.controller.has_move():
            return  # do not advance; render continues until keypress

        obs = extractObservation(self.board, p, self.tick)
        decision = p.controller.decide(obs)

        move = decision.get("move", "STAY")
        why = decision.get("why", "")
        thoughts = decision.get("thoughts", [])

        # Validate move
        validMoves = {"UP","DOWN","LEFT","RIGHT","STAY"}
        if move not in validMoves:
            thoughts = list(thoughts) + [f"Invalid move '{move}', switching to STAY"]
            move = "STAY"

        # Apply + compute outcome
        prevScore = p.score
        p.applyMove(self.board, move)
        delta = p.score - prevScore

        # Allow agent to learn from outcome
        if hasattr(p.controller, "postOutcome"):
            try:
                p.controller.postOutcome(self.tick, decision, delta)
            except Exception as e:
                # don't crash the game if an agent fails to log
                pass

        # Log thoughts
        header = f"move={move} | why={why} | Δscore={delta:+d}"
        self.logger.append(p.agentId, header, thoughts)

        # Next turn
        self.activeIdx = (self.activeIdx + 1) % len(self.turnOrder)
        if self.activeIdx == 0:
            self.npcPhase()
            self.tick += 1

    def render(self):
        activeId = self.turnOrder[self.activeIdx].agentId
        drawBoard(self.screen, self.board, activeId, self.fontSmall, self.fontMono, SIGHT_RANGE)
        drawPanel(self.screen, self.board, activeId, self.logger, (self.fontSmall, self.fontMono), self.tick)
        pygame.display.flip()

    def run(self):
        running = True
        lastTurnStamp = pygame.time.get_ticks()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r:
                        running = False
                    else:
                        # Route keys to HumanController
                        p = next(pl for pl in self.turnOrder if pl.agentId == "pentagon")
                        key_name = pygame.key.name(event.key)
                        # Normalize pygame key names to our map
                        canonical = {
                            "up":"K_UP","down":"K_DOWN","left":"K_LEFT","right":"K_RIGHT",
                            "w":"K_w","a":"K_a","s":"K_s","d":"K_d"
                        }.get(key_name, None)
                        if canonical:
                            p.controller.set_key(canonical)

            now = pygame.time.get_ticks()
            if not self.paused and not self.gameEnded():
                # simple pacing: one decision per TURN_DELAY_MS
                if now - lastTurnStamp >= TURN_DELAY_MS:
                    self.stepTurn()
                    lastTurnStamp = now

            self.render()
            self.clock.tick(FPS)

        pygame.quit()
