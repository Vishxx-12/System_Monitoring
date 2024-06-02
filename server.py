from flask import Flask, request, jsonify

app = Flask(__name__)
data_store = {}

@app.route('/collect', methods=['POST'])
def collect():
    data = request.get_json()
    hostname = data.get("hostname")
    if hostname:
        data_store[hostname] = data
    return jsonify({"status": "success"})

@app.route('/stats', methods=['GET'])
def stats():
    return jsonify(data_store)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
