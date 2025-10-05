# HumanController — waits for keyboard input and maps to a move

from typing import Optional, Dict, Any

KEY_TO_MOVE = {
    # Arrows
    "K_UP": "UP", "K_DOWN": "DOWN", "K_LEFT": "LEFT", "K_RIGHT": "RIGHT",
    # WASD
    "K_w": "UP", "K_s": "DOWN", "K_a": "LEFT", "K_d": "RIGHT",
}

class HumanController:
    def __init__(self):
        self._pending_move: Optional[str] = None

    def set_key(self, key_name: str):
        mv = KEY_TO_MOVE.get(key_name)
        if mv:
            self._pending_move = mv

    def has_move(self) -> bool:
        return self._pending_move is not None

    def pop_move(self) -> Optional[str]:
        mv = self._pending_move
        self._pending_move = None
        return mv

    def decide(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        The engine will call has_move() first and only call decide() when a move exists.
        """
        mv = self.pop_move() or "STAY"
        why = "Human input" if mv != "STAY" else "Waiting for human input"
        return {"move": mv, "why": why, "thoughts": []}
