# coding=utf-8

import time
from collections import deque


class MemCache:
    def __init__(self, expired_time=300):
        self.expired_time = expired_time
        self.queue = deque()
        self.cache = {}

    def get(self, query, start):
        self._check()
        k = (query, start)
        if k in self.cache:
            return self.cache[k]

    def update(self, query, start, resp):
        self._check()
        k = (query, start)
        if k not in self.cache:
            t = int(time.time())
            self.cache[k] = resp
            self.queue.append((t, k))

    def _check(self):
        t = int(time.time())
        while len(self.queue) > 0:
            if t - self.queue[0][0] < self.expired_time:
                break
            _, k = self.queue.popleft()
            if k in self.cache:
                del self.cache[k]
