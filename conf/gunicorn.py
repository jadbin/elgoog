# coding=utf-8

import os
from os.path import join

import multiprocessing

bind = '0.0.0.0:5931'

workers = multiprocessing.cpu_count()
worker_class = 'gevent'

pidfile = join(os.environ['ELGOOG_PID_DIR'], 'elgoog-' + os.environ['ELGOOG_ID_STRING'] + '.pid')
accesslog = join(os.environ['ELGOOG_LOG_DIR'], 'elgoog-' + os.environ['ELGOOG_ID_STRING'] + '.access.log')
errorlog = join(os.environ['ELGOOG_LOG_DIR'], 'elgoog-' + os.environ['ELGOOG_ID_STRING'] + '.error.log')
