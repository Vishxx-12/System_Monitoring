import psutil
import pika
import json
import time
import os
import socket

# Retrieve computer IP address
computer_ip = socket.gethostbyname(socket.gethostname())

# Load RabbitMQ configuration from config file
with open(os.path.join(os.path.dirname(__file__), '../config/rabbitmq_config.json')) as f:
    rabbitmq_config = json.load(f)

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_config['host']))
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue='disk_stats')

def get_disk_stats():
    # Get disk usage stats
    disk_partitions = psutil.disk_partitions(all=False)
    disk_stats = []
    for partition in disk_partitions:
        disk_usage = psutil.disk_usage(partition.mountpoint)
        disk_stats.append({
            'disk_capacity_gb': disk_usage.total / (1024**3),  # Convert to GB
            'disk_used_gb': disk_usage.used / (1024**3),  # Convert to GB
            'computer_id': computer_ip
        })
    return disk_stats

def send_disk_stats():
    disk_stats = get_disk_stats()
    for stats in disk_stats:
        message = json.dumps(stats)
        # Publish message to RabbitMQ
        channel.basic_publish(exchange='',
                              routing_key='disk_stats',
                              body=message)
        print("Sent Disk stats:", message)

while True:
    send_disk_stats()
    time.sleep(5)  # Send stats every 5 seconds

# Close connection
connection.close()
