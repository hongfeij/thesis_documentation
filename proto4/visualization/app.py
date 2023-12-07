# Flask API endpoint to serve the emotion_state.json
import json
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/get_emotion_score')
def get_emotion_score():
    with open('../emotion_state.json', 'r') as f:
        emotion_state = json.load(f)
    return jsonify(emotion_state)

if __name__ == '__main__':
    app.run(debug=True)
