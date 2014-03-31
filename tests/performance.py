# -*- coding: utf8 -*-

from scheduler.core import Scheduler
from time import time
from scheduler.storage.ram import SimpleListStorage, RBTreeStorage
from scheduler.storage.persist import FakePersistStorage
from scheduler.storage.persist import DBPersistStorage
from random import randint
from time import time

fake = FakePersistStorage()
db_persist = DBPersistStorage('mysql://root:1@localhost/liketools_scheduler')
if not db_persist.initiated():
    db_persist.init()

scheduler = Scheduler(ram_storage=RBTreeStorage(), persist_storage=FakePersistStorage())#db_persist)
#scheduler.restore()

min_time = int(time())
max_time = min_time + min_time / 2;
delay = min_time / 2;

for i in xrange(10**3):
    scheduler.add(delay_time=randint(0, delay), index=i)

s = 0.0
N = 100
for i in xrange(N):
    print i, " iteration..."
    t = time()

    events = scheduler.get_events()
    del events

    s = s + time() - t

print s/N
