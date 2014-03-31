# -*- coding: utf8 -*-

import os
import logging

DEBUG = os.environ.get('ENABLE_DEBUG') == '1'
if DEBUG:
    logging.critical(" [*] Work in debugging mode")

RABBITMQ_HOST = 'localhost'
POSTING_QUEUE = 'posting_queue'
SCHEDULER_QUEUE = 'scheduler_queue'

if os.environ.get('DEVELOPMENT') == '1':
    SCHEDULER_DB_PERSISTENT_STORAGE = 'mysql+mysqldb://root:1@localhost/liketools'
else:
    SCHEDULER_DB_PERSISTENT_STORAGE = 'mysql+mysqldb://liketools:MWzC8hbfIMxXlhq29n@localhost/liketools'

POOL_RECYCLE = 3600
POOL_SIZE = 5

SCHEDULER_RAM_STORAGE = 'scheduler.storage.ram.RBTreeStorage'
SCHEDULER_PERSISTENT_STORAGE = 'scheduler.storage.persist.DBPersistStorage'

ANTIGATE_KEY = 'b4c46602aafcf103637de3a7aef033dd'

CAPTCHA_ATTEMPTS_DELAY = 5.0
CAPTCHA_ATTEMPTS = 4

POSTING_DELAY = 5.0
