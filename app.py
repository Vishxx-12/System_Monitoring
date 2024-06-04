from flask import Flask, render_template, jsonify
from influxdb_client import InfluxDBClient, QueryApi
import json
import os

app = Flask(__name__)

# Load InfluxDB configuration from config file
with open(os.path.join(os.path.dirname(__file__), 'config/influxdb_config.json')) as f:
    influxdb_config = json.load(f)

# Connect to InfluxDB
client = InfluxDBClient(url=influxdb_config['url'], token=influxdb_config['token'], org=influxdb_config['org'])
query_api = client.query_api()

def get_stats_from_influxdb():
    query = f'from(bucket: "{influxdb_config["bucket"]}") |> range(start: -1h)'
    result = query_api.query(org=influxdb_config['org'], query=query)
    stats = []
    for table in result:
        for record in table.records:
            stats.append({
                'time': record.get_time(),
                'host': record.get_value_by_key('host'),
                'metric': record.get_measurement(),
                'value': record.get_value(),
                'type': record.get_field()
            })
    return stats

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def api_stats():
    stats = get_stats_from_influxdb()
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True)
