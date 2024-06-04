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
channel.queue_declare(queue='power_stats')

def get_power_stats():
    # Get battery information
    battery = psutil.sensors_battery()
    if battery is not None:
        return {
            'power_plugged': battery.power_plugged,
            'battery_percent': battery.percent if battery.percent is not None else -1,
            'computer_id': computer_ip
        }
    else:
        return {
            'power_plugged': None,
            'battery_percent': None,
            'computer_id': computer_ip
        }

def send_power_stats():
    power_stats = get_power_stats()
    message = json.dumps(power_stats)

    # Publish message to RabbitMQ
    channel.basic_publish(exchange='',
                          routing_key='power_stats',
                          body=message)
    print("Sent Power stats:", message)

while True:
    send_power_stats()
    time.sleep(5)  # Send stats every 5 seconds

# Close connection
connection.close()
