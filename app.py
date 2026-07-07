import os
import json
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("Warning: GEMINI_API_KEY environment variable not found.")

@app.route('/')
def home():
    return "Roblox-Gemini Bridge is Online!"

@app.route('/api/build', methods=['POST'])
def build_generation():
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify([{"x": 0, "y": 0, "z": 0}]), 200 # Fallback safety
        
        user_prompt = data['prompt']
        print(f"Received prompt from Roblox: {user_prompt}")
        
        system_instruction = (
            "You are a raw data generator for a block builder. "
            "You must strictly output a valid JSON array of objects representing coordinates. "
            "Each object inside the list must have 'x', 'y', and 'z' keys representing offsets. "
            "Example: [{\"x\": 0, \"y\": 0, \"z\": 0}, {\"x\": 1, \"y\": 0, \"z\": 0}]. "
            "Do not include text commentary or backticks."
        )

        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            system_instruction=system_instruction
        )
        
        response = model.generate_content(
            user_prompt,
            generation_config={"response_mime_type": "application_json"}
        )
        
        # Safe JSON parsing
        try:
            cleaned_layout = json.loads(response.text)
            # Make sure it's actually a list/array
            if isinstance(cleaned_layout, list):
                return jsonify(cleaned_layout), 200
            else:
                return jsonify([cleaned_layout]), 200
        except Exception as json_err:
            print(f"JSON Parsing Error: {json_err}. Raw output was: {response.text}")
            # Fallback block configuration so Roblox gets valid data no matter what
            return jsonify([{"x": 0, "y": 0, "z": 0}, {"x": 0, "y": 1, "z": 0}]), 200

    except Exception as e:
        print(f"Global server error: {str(e)}")
        # Ultimate backup array to ensure HTTP 200 success
        return jsonify([{"x": 0, "y": 0, "z": 0}]), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
