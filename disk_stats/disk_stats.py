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
channel.queue_declare(queue='disk_stats')    

def get_disk_stats():
    disk_partitions = [partition._asdict() for partition in psutil.disk_partitions()]

    # Get disk usage for each partition and convert to dictionary
    disk_usage = {partition['device']: psutil.disk_usage(partition['mountpoint'])._asdict() for partition in disk_partitions}

    # Get disk IO stats and convert to dictionary
    disk_io = psutil.disk_io_counters()._asdict()

    return {
        "disk_partitions": disk_partitions,
        "disk_usage": disk_usage,
        "disk_io": disk_io,
    }
    
    
    
def send_disk_stats():
    disk_stats = get_disk_stats()
    message = json.dumps(disk_stats)

    # Publish message to RabbitMQ
    channel.basic_publish(exchange='',
                          routing_key='disk_stats',
                          body=message)
    print("Sent disk stats:", message)

while True:
    send_disk_stats()
    time.sleep(5)  # Send stats every 5 seconds

# Close connection
connection.close()