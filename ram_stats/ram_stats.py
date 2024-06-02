import psutil
import pika
import os
import time
import json


with open(os.path.join(os.path.dirname(__file__), '../config/rabbitmq_config.json')) as f:
    rabbitmq_config = json.load(f)
    
connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_config['host']))
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue='mem_stats')   


def get_memory_stats():
    # Get virtual memory stats and convert to dictionary
    virtual_memory = psutil.virtual_memory()._asdict()

    # Get swap memory stats and convert to dictionary
    swap_memory = psutil.swap_memory()._asdict()

    return {
        "virtual_memory": virtual_memory,
        "swap_memory": swap_memory,
    }
    
    
def send_memory_stats():
    ram_stats = get_memory_stats()
    message = json.dumps(ram_stats)

    # Publish message to RabbitMQ
    channel.basic_publish(exchange='',
                          routing_key='mem_stats',
                          body=message)
    print("Sent memory stats:", message)

while True:
    send_memory_stats()
    time.sleep(5)  # Send stats every 5 seconds

# Close connection
connection.close()