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
channel.queue_declare(queue='net_stats')    


def get_network_stats():
    # Get network interfaces and convert to dictionary
    net_if_addrs = {interface: [addr._asdict() for addr in addrs] for interface, addrs in psutil.net_if_addrs().items()}

    # Get network stats per interface and convert to dictionary
    net_io = psutil.net_io_counters(pernic=True)
    net_io = {interface: stats._asdict() for interface, stats in net_io.items()}

    return {
        "net_if_addrs": net_if_addrs,
        "net_io": net_io,
    }
    
    
    
    
def send_network_stats():
    net_stats = get_network_stats()
    message = json.dumps(net_stats)

    # Publish message to RabbitMQ
    channel.basic_publish(exchange='',
                          routing_key='net_stats',
                          body=message)
    print("Sent network stats:", message)

while True:
    send_network_stats()
    time.sleep(5)  # Send stats every 5 seconds

# Close connection
connection.close()