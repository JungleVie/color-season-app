from flask import Flask, request
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
OPENAI_API_ENDPOINT = os.getenv("OPENAI_API_ENDPOINT", "https://api.openai.com/v1/chat/completions")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def hello():
    return "Hello, World!"

@app.route('/analyze', methods=["POST"])
def analyze():
    hair_color = request.form.get('hair_color')
    eye_color = request.form.get('eye_color')

    file = request.files.get('image')
    if not file or file.filename == '':
        return 'No image provided', 400

    filename = secure_filename(file.filename)
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(image_path)

    base64_image = encode_image(image_path)
    payload = build_payload(hair_color, eye_color, base64_image)

    response = requests.post(OPENAI_API_ENDPOINT, headers=get_headers(), json=payload)
    if not response.ok:
        return 'Error processing request', 500

    description = response.json()['choices'][0]['message']['content']
    return {"description": description}

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def build_payload(hair_color, eye_color, base64_image):
    return {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "system",
                "content": "Analyze the image and determine their color season."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"hair color is {hair_color} and eye color is {eye_color}. which is the color season?"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

def get_headers():
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

if __name__ == '__main__':
    app.run(debug=True)
