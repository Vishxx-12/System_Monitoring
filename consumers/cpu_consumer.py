import pika
import json
import time
import os
from influxdb_client import InfluxDBClient, Point, WriteOptions

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
channel.queue_declare(queue='cpu_stats')

def send_to_influxdb(cpu_stats):
    # Connect to InfluxDB
    client = InfluxDBClient(url=influxdb_config['url'], token=influxdb_config['token'], org=influxdb_config['org'])
    write_api = client.write_api(write_options=WriteOptions(batch_size=1))

    # Create a point and write it to the database
    point = Point("cpu") \
        .tag("host", influxdb_config['host']) \
        .field("cpu_percent", cpu_stats['cpu_percent']) \
        .time(time.time_ns())
    
    write_api.write(bucket=influxdb_config['bucket'], org=influxdb_config['org'], record=point)
    print("Written to InfluxDB:", point)

    # Close the client
    client.close()

def callback(ch, method, properties, body):
    cpu_stats = json.loads(body)
    print("Received CPU stats:", cpu_stats)
    send_to_influxdb(cpu_stats)

# Consume messages from the 'cpu_stats' queue
channel.basic_consume(queue='cpu_stats', on_message_callback=callback, auto_ack=True)

print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

# Close connection (This will never be reached because start_consuming() is blocking)
connection.close()
