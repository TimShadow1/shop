from flask import Flask, render_template, jsonify, request
import json
import os

app = Flask(__name__)
ITEMS_FILE = os.path.join(os.path.dirname(__file__), '../items.json')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/items')
def get_items():
    with open(ITEMS_FILE, 'r', encoding='utf-8') as f:
        items = json.load(f)
    return jsonify(items)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
