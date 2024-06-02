from influxdb_client import InfluxDBClient, Point, Dialect

# Initialize InfluxDB client
client = InfluxDBClient(url="http://localhost:8086",
                        token="YOUR_TOKEN",
                        org="YOUR_ORGANIZATION")

# Get a reference to the bucket
bucket = client.buckets_api().find_bucket_by_name(bucket_name="YOUR_BUCKET_NAME").get()

# Define the measurement name and tags
measurement = "system_stats"

# Function to write points to InfluxDB
def write_to_influxdb(point):
    write_api = client.write_api(write_options=SYNCHRONOUS)
    write_api.write(bucket=bucket.id, org=org, record=point)
    write_api.close()