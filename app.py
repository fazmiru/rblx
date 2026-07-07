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
            return jsonify([{"x": 0, "y": 0, "z": 0}]), 200
        
        user_prompt = data['prompt']
        
        # Crystal clear instructions on key casing
        system_instruction = (
            "You are an advanced 3D voxel compiler for Roblox. "
            "The user will provide a structure name (e.g., 'house', 'castle', 'pyramid'). "
            "You must return a large, complex, and highly detailed JSON array of coordinate objects. "
            "Each object must have 'x', 'y', and 'z' integer offsets. "
            "CRITICAL: Do NOT return just 2 or 3 blocks. For a 'house', you must generate a full layout "
            "including 4 walls, a door opening, and a roof layer—spanning at least 30 to 60 distinct coordinate points. "
            "Vary the x, y, and z numbers so they form an actual hollow room shell. "
            "Strictly output raw JSON array format only. No markdown, no conversational text."
        )

        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            system_instruction=system_instruction
        )
        
        # Enforce strict application_json structure from the model
        response = model.generate_content(
            f"Build a simple layout for: {user_prompt}",
            generation_config={"response_mime_type": "application_json"}
        )
        
        # Load string safely into list object
        layout_data = json.loads(response.text)
        return jsonify(layout_data), 200

    except Exception as e:
        print(f"Internal error caught: {str(e)}")
        # If anything format-wise misbehaves, send a standard 3-block line fallback
        return jsonify([{"x": 0, "y": 0, "z": 0}, {"x": 1, "y": 0, "z": 0}, {"x": 2, "y": 0, "z": 0}]), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
