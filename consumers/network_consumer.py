import pika
import json
import time
import os
from influxdb_client import InfluxDBClient, Point, WriteOptions
import socket

# Load RabbitMQ configuration from config file
with open(os.path.join(os.path.dirname(__file__), '../config/rabbitmq_config.json')) as f:
    rabbitmq_config = json.load(f)

# Load InfluxDB configuration from config file
with open(os.path.join(os.path.dirname(__file__), '../config/influxdb_config.json')) as f:
    influxdb_config = json.load(f)

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_config['host']))
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue='network_stats')

def send_to_influxdb(network_stats):
    # Connect to InfluxDB
    client = InfluxDBClient(url=influxdb_config['url'], token=influxdb_config['token'], org=influxdb_config['org'])
    write_api = client.write_api(write_options=WriteOptions(batch_size=1))

    # Create a point and write it to the database
    for stats in network_stats:
        point = Point("network") \
            .tag("host", stats['computer_id']) \
            .field("network_type", stats['network_type']) \
            .field("interface_name", stats['interface_name']) \
            .field("bytes_sent_mb", stats['bytes_sent_mb']) \
            .field("bytes_recv_mb", stats['bytes_recv_mb']) \
            .field("packets_sent", stats['packets_sent']) \
            .field("packets_recv", stats['packets_recv']) \
            .time(time.time_ns())
        
        write_api.write(bucket=influxdb_config['bucket'], org=influxdb_config['org'], record=point)
        print("Written to InfluxDB:", point)

    # Close the client
    client.close()

def callback(ch, method, properties, body):
    network_stats = json.loads(body)
    print("Received Network stats from", network_stats['computer_id'], ":", network_stats)
    send_to_influxdb([network_stats])

# Consume messages from the 'network_stats' queue
channel.basic_consume(queue='network_stats', on_message_callback=callback, auto_ack=True)

print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

# Close connection (This will never be reached because start_consuming() is blocking)
connection.close()
