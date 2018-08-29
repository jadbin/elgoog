# coding=utf-8

import time
import hashlib

from elgoog import config


class Defender:
    def __init__(self, timestamp_interval=600):
        self.timestamp_interval = timestamp_interval

    def verify(self, query, page, timestamp, nonce, signature):
        t = int(time.time())
        s = query + str(page) + str(timestamp) + str(nonce) + config.elgoog_token
        h = hashlib.sha256(s.encode('utf-8')).hexdigest()
        if h != signature:
            return False, 'Bad signature'
        if abs(t - timestamp) > self.timestamp_interval:
            return False, 'Bad timestamp, timestamp={}, local timestamp={}'.format(timestamp, t)
        return True, ''
