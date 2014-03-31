from random import randint

s = 'insert into events(event_time, data) values '
for i in xrange(10**6):
    s = s + "(%s, '{\"index\": %s}'), " % (randint(1, 10**7), randint(1, 10**12))

s = s + "(%s, '{\"index\": %s}');" % (randint(1, 10**7), randint(1, 10**12)) 

f = open('sqlbulk', 'w+')
f.write(s)
f.close()
