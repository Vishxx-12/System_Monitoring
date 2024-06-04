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
channel.queue_declare(queue='network_stats')

def get_network_stats():
    # Get network I/O stats
    io_counters = psutil.net_io_counters()
    # Get network interface stats
    if_stats = psutil.net_if_stats()
    
    network_type = "unknown"
    for iface, stats in if_stats.items():
        if stats.isup:
            if iface.startswith("eth"):
                network_type = "ethernet"
            elif iface.startswith("wlan"):
                network_type = "wifi"
            break

    return {
        'bytes_sent_mb': io_counters.bytes_sent / (1024**2),  # Convert to MB
        'bytes_recv_mb': io_counters.bytes_recv / (1024**2),  # Convert to MB
        'network_type': network_type,
        'computer_id': computer_ip
    }

def send_network_stats():
    network_stats = get_network_stats()
    message = json.dumps(network_stats)

    # Publish message to RabbitMQ
    channel.basic_publish(exchange='',
                          routing_key='network_stats',
                          body=message)
    print("Sent Network stats:", message)

while True:
    send_network_stats()
    time.sleep(5)  # Send stats every 5 seconds

# Close connection
connection.close()
