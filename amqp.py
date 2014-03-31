#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
Send message to AMQP queue.
"""

import pika
import sys
import json
import re

def parse_args():
    args = sys.argv[1:]
    
    keyval = filter(lambda x: re.match(r'[a-zA-Z0-9\-_]+=.*', x) is not None, args)
    commands = filter(lambda x: re.match(r'[a-zA-Z0-9\-_]+=.*', x) is None, args)

    if len(commands) < 1 or len(commands) > 2:
        raise Exception, "Too much or not enough command arguments are passed."

    if len(commands) == 1:
        host = 'localhost'
        queue = commands[0]
    elif len(commands) == 2:
        host = commands[0]
        queue = commands[1]

    message = {}
    for kv in keyval:
        key, value = re.findall(r'([a-zA-Z0-9\-_]+)=(.*)', kv)[0]
        if value.startswith('{') or value.startswith('['):
            value = json.loads(value.replace("'", '"'))
        elif re.match(r'^-?[0-9]+$', value):
            value = int(value)
        elif re.match(r'^-?[0-9]+\.[0-9]+$', value):
            value = float(value)
        
        message[key] = value

    return (host, queue, message)



def send():

    host, queue, message = parse_args()
    message = json.dumps(message)

    print ' [*] Host ', host
    print ' [*] Queue ', queue
    print ' [*] Message ', message
    
    connection = pika.BlockingConnection(pika.ConnectionParameters( host=host))
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_publish(exchange='', 
                            routing_key=queue, 
                            body=message,  
                            properties=pika.BasicProperties(
                                delivery_mode = 2, # make message persistent
                           ))
    connection.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "amqp.py [host] <queue_name> key1=val1 key2=val2..."
        exit()
    send()
