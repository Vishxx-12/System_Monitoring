import psutil
import pika
import json
import time
import os

# Load RabbitMQ configuration from config file
with open(os.path.join(os.path.dirname(__file__), '../config/rabbitmq_config.json')) as f:
    rabbitmq_config = json.load(f)

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_config['host']))
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue='cpu_stats')

def get_cpu_stats():
    # Get CPU usage stats
    cpu_percent = psutil.cpu_percent(interval=1)
    return {'cpu_percent': cpu_percent}

def send_cpu_stats():
    cpu_stats = get_cpu_stats()
    message = json.dumps(cpu_stats)

    # Publish message to RabbitMQ
    channel.basic_publish(exchange='',
                          routing_key='cpu_stats',
                          body=message)
    print("Sent CPU stats:", message)

while True:
    send_cpu_stats()
    time.sleep(5)  # Send stats every 5 seconds

# Close connection
connection.close()
