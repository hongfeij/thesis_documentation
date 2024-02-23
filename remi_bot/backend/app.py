from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import conversation
import os
from flask import render_template
import uuid

name = ""

app = Flask(__name__)
CORS(app)  # Handle Cross-Origin Resource Sharing for frontend communication

@app.route('/init_chat', methods=['POST'])
def init_chat():
    global name
    data = request.json
    name = data.get('name')
    conversation.init_chat(name)
    return jsonify({'message': f'Chat started with {name}'}), 200


@app.route('/send_text', methods=['POST'])
def send_text():
    global name
    data = request.json
    text = data.get('text')
    
    unique_filename = f"response_{uuid.uuid4()}.mp3"
    response_text = conversation.chat(name, text, unique_filename)
    
    audio_url = request.host_url + 'audio/' + unique_filename
    
    return jsonify({'response_text': response_text, 'mp3_url': audio_url}), 200

@app.route('/audio/<filename>', methods=['GET'])
def serve_audio(filename):
    directory_path = os.path.dirname(os.path.realpath(__file__))
    return send_from_directory(directory_path, filename)

# @app.route('/')
# def home():
#     return render_template('chat_interface.html')

if __name__ == '__main__':
    app.run(debug=True)
