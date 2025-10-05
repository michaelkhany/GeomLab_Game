# Renderer and UI panel

import pygame
from settings import CELL, GRID_COLOR, BG_COLOR, PANEL_W, FOG_COLOR, FONT_NAME
from engine.geometry import manhattan

def drawBoard(screen, board, activeId, fontSmall, fontMono, sightRange):
    screen.fill(BG_COLOR)

    gridWpx = board.w * CELL
    gridHpx = board.h * CELL

    # Grid
    for x in range(board.w + 1):
        pygame.draw.line(screen, GRID_COLOR, (x * CELL, 0), (x * CELL, gridHpx))
    for y in range(board.h + 1):
        pygame.draw.line(screen, GRID_COLOR, (0, y * CELL), (gridWpx, y * CELL))

    # Greens
    for (gx, gy) in board.greens:
        cx, cy = gx * CELL + CELL // 2, gy * CELL + CELL // 2
        pygame.draw.circle(screen, (60, 200, 80), (cx, cy), CELL // 3)

    # Reds
    for r in board.reds:
        cx, cy = r.x * CELL + CELL // 2, r.y * CELL + CELL // 2
        pygame.draw.circle(screen, (200, 60, 60), (cx, cy), CELL // 3)

    # Players
    for p in board.players:
        drawShape(screen, p)

    # Fog-of-war for the active player only
    ap = next(pl for pl in board.players if pl.agentId == activeId)
    fog = pygame.Surface((gridWpx, gridHpx), pygame.SRCALPHA)
    for y in range(board.h):
        for x in range(board.w):
            if manhattan((ap.x, ap.y), (x, y)) > sightRange:
                rect = pygame.Rect(x * CELL, y * CELL, CELL, CELL)
                fog.fill(FOG_COLOR, rect)
    screen.blit(fog, (0, 0))

    # Right panel background
    panelRect = pygame.Rect(gridWpx, 0, PANEL_W, gridHpx)
    pygame.draw.rect(screen, (28, 30, 34), panelRect)

def drawShape(screen, player):
    xpx = player.x * CELL
    ypx = player.y * CELL
    c = player.color
    if player.agentId == "triangle":
        pts = [(xpx + CELL // 2, ypx + 4), (xpx + 4, ypx + CELL - 4), (xpx + CELL - 4, ypx + CELL - 4)]
        pygame.draw.polygon(screen, c, pts)
    elif player.agentId == "rectangle":
        rect = pygame.Rect(xpx + 4, ypx + 6, CELL - 8, CELL - 12)
        pygame.draw.rect(screen, c, rect)
    else:
        # pentagon
        cx, cy = xpx + CELL // 2, ypx + CELL // 2
        r = CELL // 2 - 4
        pts = []
        import math
        for i in range(5):
            ang = math.radians(-90 + i * 72)
            pts.append((cx + int(r * math.cos(ang)), cy + int(r * math.sin(ang))))
        pygame.draw.polygon(screen, c, pts)

def drawPanel(screen, board, activeId, logger, fonts, tick):
    fontSmall, fontMono = fonts
    gridWpx = board.w * CELL
    x0 = gridWpx + 12
    y = 10

    # Header
    screen.blit(fontMono.render("GeomLab 1", True, (230, 230, 230)), (x0, y)); y += 26
    screen.blit(fontSmall.render(f"Tick: {tick}", True, (200, 200, 200)), (x0, y)); y += 22
    screen.blit(fontSmall.render(f"Greens left: {len(board.greens)}", True, (180, 220, 180)), (x0, y)); y += 22

    y += 6
    # Player scores
    for p in board.players:
        label = f"{p.agentId:<9}  score: {p.score}"
        color = (220, 220, 220) if p.agentId != activeId else (255, 240, 180)
        screen.blit(fontMono.render(label, True, color), (x0, y))
        y += 22

    y += 8

    # Thoughts for each agent
    for p in board.players:
        screen.blit(fontMono.render(f"[{p.agentId}] thoughts", True, (180, 180, 255)), (x0, y)); y += 22
        lines = logger.get(p.agentId)
        # Show last 6 groups per agent
        for header, msgs in list(lines)[-6:]:
            screen.blit(fontSmall.render(f"• {header}", True, (210, 210, 210)), (x0, y)); y += 18
            for m in msgs[:3]:
                screen.blit(fontSmall.render(f"  {m}", True, (170, 190, 200)), (x0, y)); y += 16
        y += 6
