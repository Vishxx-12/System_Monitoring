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
    # Get network usage stats
    network_stats = psutil.net_if_stats()
    formatted_stats = []
    for interface, stats in network_stats.items():
        if stats.isup:
            formatted_stats.append({
                'network_type': 'WiFi' if 'wireless' in interface.lower() else 'Ethernet',
                'interface_name': interface,
                'bytes_sent_mb': stats.bytes_sent / (1024**2),  # Convert to MB
                'bytes_recv_mb': stats.bytes_recv / (1024**2),  # Convert to MB
                'packets_sent': stats.packets_sent,
                'packets_recv': stats.packets_recv,
                'computer_id': computer_ip
            })
    return formatted_stats

def send_network_stats():
    network_stats = get_network_stats()
    for stats in network_stats:
        message = json.dumps(stats)
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
