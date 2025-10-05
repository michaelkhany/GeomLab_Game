# RectangleController — Synchange LLM agent with decision history and validation

import json
import re
from typing import List, Dict, Any, Optional, Tuple
from controllers.base_controller import BaseController
from controllers.synchange_llm import SynchangeLLM

VALID_MOVES = {"UP","DOWN","LEFT","RIGHT","STAY"}

def extract_json(text: str) -> Optional[dict]:
    """Extract the first valid JSON object from a string (supports code blocks)."""
    # Try fenced code block ```json … ```
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.DOTALL|re.IGNORECASE)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # Fallback: first {...} blob
    m = re.search(r"(\{.*\})", text, flags=re.DOTALL)
    if m:
        blob = m.group(1)
        # balance braces conservatively
        try:
            return json.loads(blob)
        except Exception:
            # last resort: strip trailing explanations
            try:
                end = blob.rfind("}")
                return json.loads(blob[:end+1])
            except Exception:
                return None
    return None

def is_valid_decision(d: dict) -> Tuple[bool, str]:
    if not isinstance(d, dict):
        return (False, "Decision is not a JSON object.")
    mv = d.get("move")
    if mv not in VALID_MOVES:
        return (False, f"Invalid move '{mv}'.")
    if not isinstance(d.get("why",""), str):
        return (False, "Field 'why' must be a string.")
    th = d.get("thoughts", [])
    if not isinstance(th, list) or not all(isinstance(x, str) for x in th):
        return (False, "Field 'thoughts' must be a list of strings.")
    return (True, "")

class RectangleController(BaseController):
    """
    Synchange LLM-driven controller.
    Keeps an internal short history of (tick, move, deltaScore, summary).
    """
    def __init__(self, model: str = "meta_llama70b", access_id: str = "trial_version",
                 api_url: str = "https://synchange.com/sync.php", sender: str = "GeomLab1",
                 service_name: str = "meta_llama70b",
                 api_retries: int = 3, timeout: int = 10,
                 agent_retries: int = 3, history_max: int = 30):
        self.llm = SynchangeLLM(
            model=model, api_url=api_url, sender=sender,
            retries=api_retries, timeout=timeout,
            access_id=access_id, server_name=service_name
        )
        self.history: List[Dict[str, Any]] = []
        self.agent_retries = agent_retries
        self.history_max = history_max

    def decide(self, obs: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self.build_prompt(obs)
        parsed: Optional[dict] = None
        reasons = []

        for attempt in range(1, self.agent_retries + 1):
            raw = self.llm.send_request(prompt)
            parsed = extract_json(raw) if isinstance(raw, str) else None
            if not parsed:
                reasons.append(f"Attempt {attempt}: could not parse JSON.")
                continue
            ok, msg = is_valid_decision(parsed)
            if ok:
                break
            reasons.append(f"Attempt {attempt}: {msg}")
            # Add corrective hint for next try
            prompt += (
                f"\n\nPrevious attempt had an issue: {msg}. "
                f"Return ONLY a strict JSON object like "
                '{"move":"UP|DOWN|LEFT|RIGHT|STAY","why":"...","thoughts":["...","..."]}.'
            )

        if not parsed or not is_valid_decision(parsed)[0]:
            # Safe fallback
            fallback = {"move":"STAY","why":"LLM failed to produce valid decision","thoughts":reasons[:3]}
            return fallback

        return parsed

    def postOutcome(self, tick: int, decision: Dict[str, Any], delta_score: int):
        """Engine calls this after applying our move so we can learn/log."""
        entry = {
            "tick": tick,
            "move": decision.get("move"),
            "delta": int(delta_score),
            "why": decision.get("why","")
        }
        self.history.append(entry)
        if len(self.history) > self.history_max:
            self.history = self.history[-self.history_max:]

    # ---------- Prompt shaping ----------
    def build_prompt(self, obs: Dict[str, Any]) -> str:
        """
        Compact, deterministic prompt. The model must output ONLY the JSON decision.
        """
        rules = (
            "- You play as RECTANGLE.\n"
            "- Movement is turn-based on a 2D grid. Legal moves: UP, DOWN, LEFT, RIGHT, STAY.\n"
            "- Objective: collect GREEN circles (+1). Avoid RED circles (−1).\n"
            "- Vision is limited to Manhattan radius = {sight}.\n"
            "- The game ends when all greens are taken or after {max_rounds} rounds.\n"
            "- Output MUST be a single JSON object with keys: move, why, thoughts.\n"
            "- 'move' must be exactly one of: UP, DOWN, LEFT, RIGHT, STAY.\n"
            "- Be concise in 'why'; include 1–3 short 'thoughts'.\n"
        ).format(sight=obs["rules"]["sight"], max_rounds=200)

        obs_summary = self.summarize_obs(obs)
        hist_summary = self.summarize_history(10)

        return (
            "SYSTEM:\n"
            "You are a game-playing agent making a single move decision.\n"
            "Return ONLY a valid JSON object — no extra text, no code fences.\n\n"
            f"RULES:\n{rules}\n"
            f"OBSERVATION:\n{obs_summary}\n"
            f"HISTORY (last turns):\n{hist_summary}\n\n"
            'Return JSON like {"move":"UP","why":"...","thoughts":["..."]}'
        )

    def summarize_obs(self, obs: Dict[str, Any]) -> str:
        me = obs["self"]
        vis = obs["vision"]
        greens = [(v["x"], v["y"]) for v in vis if v["t"] == "GREEN"]
        reds   = [(v["x"], v["y"]) for v in vis if v["t"] == "RED"]
        players= [(v.get("id"), v["x"], v["y"]) for v in vis if v["t"] == "PLAYER" and v.get("id")!="rectangle"]
        return (
            f"tick={obs['tick']}, self=({me['pos']['x']},{me['pos']['y']}), "
            f"score={me['score']}, greens={greens[:6]}, reds={reds[:6]}, "
            f"otherPlayers={players[:3]}, bounds={obs['bounds']}"
        )

    def summarize_history(self, n: int) -> str:
        if not self.history:
            return "(empty)"
        last = self.history[-n:]
        return "; ".join([f"[t{h['tick']}] {h['move']} (Δ{h['delta']})"
                          for h in last])
