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
            return jsonify({"error": "Missing prompt in request data"}), 400
        
        user_prompt = data['prompt']
        
        # System instructions force Gemini to only output raw data coordinates
        system_instruction = (
            "You are a Roblox structural builder compiler. "
            "The user will give you an object to build (e.g., 'house', 'castle'). "
            "You MUST return a valid JSON array of objects, where each object has 'x', 'y', and 'z' coordinates. "
            "Example format for a simple 2-block structure: [{\"x\": 0, \"y\": 0, \"z\": 0}, {\"x\": 0, \"y\": 1, \"z\": 0}]. "
            "Do NOT include markdown syntax, do NOT wrap it in ```json blocks, and do NOT include conversational text. Output raw JSON data only."
        )

        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            system_instruction=system_instruction
        )
        
        # Tell the API explicitly to structure its output as JSON
        response = model.generate_content(
            user_prompt,
            generation_config={"response_mime_type": "application_json"}
        )
        
        # Parse the text data from Gemini back into clean JSON for Roblox
        cleaned_layout = json.loads(response.text)
        
        # Return the clean block array directly to your Roblox script
        return jsonify(cleaned_layout), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
