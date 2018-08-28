# coding=utf-8

import time
import hashlib
from collections import deque

from elgoog import config


class Defender:
    def __init__(self, timestamp_interval=1800, defense_interval=3600):
        self.timestamp_interval = timestamp_interval
        self.defense_interval = defense_interval
        self.replay = set()
        self.queue = deque()

    def verify(self, query, start, timestamp, nonce, signature):
        t = int(time.time())
        while len(self.queue) > 0:
            if t - self.queue[0][0] < self.defense_interval:
                break
            self.queue.popleft()
        s = query + str(start) + str(timestamp) + str(nonce) + config.elgoog_token
        h = hashlib.sha256(s.encode('utf-8')).hexdigest()
        if h != signature:
            return False
        if abs(t - timestamp) > self.timestamp_interval:
            return False
        x = (timestamp, nonce)
        if x in self.replay:
            return False
        self.queue.append((t, x))
        self.replay.add(x)
        return True
