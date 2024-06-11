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
channel.queue_declare(queue='ram_stats')

def get_ram_stats():
    # Get RAM usage stats
    virtual_memory = psutil.virtual_memory()
    used_memory_gb = (virtual_memory.total - virtual_memory.available) / (1024**3)  # Convert to GB
    available_memory_gb = virtual_memory.available / (1024**3)  # Convert to GB
    return {
        'used_memory_gb': used_memory_gb,
        'available_memory_gb': available_memory_gb,
        'computer_id': computer_ip
    }

def send_ram_stats():
    ram_stats = get_ram_stats()
    message = json.dumps(ram_stats)

    # Publish message to RabbitMQ
    channel.basic_publish(exchange='',
                          routing_key='ram_stats',
                          body=message)
    print("Sent RAM stats:", message)

while True:
    send_ram_stats()
    time.sleep(5)  # Send stats every 5 seconds

# Close connection
connection.close()
