# Thoughts logger per agent

from collections import deque
from settings import LOG_HISTORY_PER_AGENT

class ThoughtsLogger:
    def __init__(self):
        self.byAgent = {}

    def ensure(self, agentId):
        if agentId not in self.byAgent:
            self.byAgent[agentId] = deque(maxlen=LOG_HISTORY_PER_AGENT)

    def append(self, agentId, header, lines):
        self.ensure(agentId)
        self.byAgent[agentId].append((header, list(lines or [])))

    def get(self, agentId):
        self.ensure(agentId)
        return list(self.byAgent[agentId])
