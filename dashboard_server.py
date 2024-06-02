from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def dashboard():
    response = requests.get('http://localhost:5000/stats')
    data = response.json()
    return render_template('dashboard.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
