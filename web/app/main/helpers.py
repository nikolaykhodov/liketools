# -*- coding: utf8 -*-


from django.conf import settings
import pika
import json

def send_to_scheduler(message):
    """
    Send message about posting 
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters( host=settings.RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=settings.SCHEDULER_QUEUE, durable=True)
    channel.basic_publish(exchange='', 
                            routing_key=settings.SCHEDULER_QUEUE, 
                            body=json.dumps(message),  
                            properties=pika.BasicProperties(
                                delivery_mode = 2, # make message persistent
                           ))
    connection.close()

