import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)
CORS(app)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Root route para i-serve ang frontend index.html
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# Catch-all route para sa static files (CSS, JS, images)
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_prompt = data.get('prompt', '').strip()

        if not user_prompt:
            return jsonify({'success': False, 'error': 'Walang ibinigay na prompt.'}), 400

        # Call Gemini API
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
        )

        if response and response.text:
            return jsonify({'success': True, 'response': response.text})
        else:
            return jsonify({'success': False, 'error': 'Empty response from model.'}), 500

    except Exception as e:
        print(f"Backend Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)