from scheduler.core import Scheduler
from scheduler.storage.ram import RBTreeStorage
from scheduler.storage.persist import DBPersistStorage
from time import time
from random import randint

N = 100

scheduler = Scheduler(ram_storage=RBTreeStorage(), persist_storage=DBPersistStorage('mysql://root:1@localhost/liketools'))

start = time()

print "Start restoring..."
scheduler.restore()
print "Restored..."

print "Restoring takes ", (time() - start), " seconds"


s = 0.0
for i in xrange(N):
    start = time()

    events = scheduler.get_events(randint(0, int(start)))

    s = time() - s

print "Average get_events() duratios is ", (s/N), "seconds"
