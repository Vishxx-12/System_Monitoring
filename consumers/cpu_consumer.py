import pika
import json

def consume_messages_from_rabbitmq(queue_name):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)

    def callback(ch, method, properties, body):
        # Deserialize the JSON string back into a Python dictionary
        message = json.loads(body.decode())
        
        # Convert the message to an InfluxDB point
        point = Point(measurement).field("value", message["cpu_usage"])
        
        # Write the point to InfluxDB
        write_to_influxdb(point)

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print(f"Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()