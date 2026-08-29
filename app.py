import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

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
        data = request.get_json() or {}
        user_prompt = data.get('prompt', '').strip()
        course_name = data.get('course', 'General Academics')

        if not user_prompt:
            return jsonify({'success': False, 'error': 'Walang ibinigay na prompt.'}), 400

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return jsonify({'success': False, 'error': 'Nawawala ang GEMINI_API_KEY sa Environment Variables.'}), 500

        # Initialize ang Gemini Client sa loob ng request para sa Vercel serverless environment
        client = genai.Client(api_key=api_key)

        # Contextual prompt para sa kurso ng estudyante
        prompt_with_context = (
            f"You are EduMind AI, a helpful, encouraging, and accurate study assistant for a student enrolled in {course_name}.\n"
            f"Answer the user's question clearly, thoroughly, and avoid generic repetition.\n\n"
            f"User Question: {user_prompt}"
        )

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_with_context,
        )

        if response and response.text:
            return jsonify({'success': True, 'response': response.text})
        else:
            return jsonify({'success': False, 'error': 'Walang nakuha na response mula sa AI model.'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
