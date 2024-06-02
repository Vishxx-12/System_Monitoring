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
channel.queue_declare(queue='power_stats')   


def get_sensors_stats():
    # Check if sensors_battery is available
    battery = psutil.sensors_battery()
    battery_stats = battery._asdict() if battery else None
    
    
    boot_time = psutil.boot_time()
    uptime = time.time() - boot_time

    # psutil does not support temperature sensors on all platforms
    # You might need to use third-party libraries for advanced sensors monitoring


    return {
        "battery": battery_stats,
        "uptime_seconds": uptime,
        # "temperatures": temperatures, # Uncomment if temperature data is available
    }
    





def send_power_stats():
    pow_stats = get_sensors_stats()
    message = json.dumps(pow_stats)

    # Publish message to RabbitMQ
    channel.basic_publish(exchange='',
                          routing_key='net_stats',
                          body=message)
    print("Sent network stats:", message)

while True:
    send_power_stats()
    time.sleep(5)  # Send stats every 5 seconds

# Close connection
connection.close()