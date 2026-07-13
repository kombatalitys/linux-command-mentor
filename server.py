import os
from flask import Flask, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

# This will grab your key safely from the cloud platform's dashboard later
API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route('/explain', methods=['POST'])
def explain_command():
    # Grab the JSON data sent from your Tkinter app
    data = request.json or {}
    user_input = data.get('command', '').strip()
    
    if not user_input:
        return jsonify({'error': 'No command provided'}), 400

    if not API_KEY:
        return jsonify({'error': 'Server configuration error: Missing API Key'}), 500

    try:
        # Initialize Gemini inside the request
        client = genai.Client(api_key=API_KEY)
        
        config = types.GenerateContentConfig(
            system_instruction=(
                "You are a friendly Linux mentor. The user will give you a command. "
                "Explain what it means in plain, simple English in 2 sentences max. "
                "If it's a dangerous command like rm -rf, warn them strongly."
            ),
            temperature=0.3
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_input,
            config=config
        )
        
        # Send the text back to the desktop app
        return jsonify({'explanation': response.text})
        
    except Exception as e:
        return jsonify({'error': f'Failed to reach AI: {str(e)}'}), 500

if __name__ == '__main__':
    # Runs the server locally on port 5000 for testing
    app.run(debug=True, port=5000)