from influxdb_client import InfluxDBClient, Point, Dialect

# Initialize InfluxDB client
client = InfluxDBClient(url="http://localhost:8086",
                        token="-fCcnfJV44c7lf93x7bpqXmdg0XdifcH6FHLyKUAsgFP7rz1xifczXiMrd9XJ9NmB1jvvFPKcoOFslCH950wXQ==",
                        org="soa")

# Get a reference to the bucket
bucket = client.buckets_api().find_bucket_by_name(bucket_name="pc_specs").get()

# Define the measurement name and tags
measurement = "system_stats"

# Function to write points to InfluxDB
def write_to_influxdb(point):
    write_api = client.write_api(write_options=SYNCHRONOUS)
    write_api.write(bucket=bucket.id, org=org, record=point)
    write_api.close()
    
    
    
    
    
    # api= miWzbx0tzCP_6Q7s6nY26mF7OVQ9MaA-bPwCwz2U_JYBUZB5lEyoPpwjfMX82ns3yZ1jlLAfoAFDEGIBVIJjcw==