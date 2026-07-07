import os
import json
from flask import Flask, request, jsonify
import google.generativeai as genai
import typing 
import typing_extensions as typing_ext 

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("Warning: GEMINI_API_KEY environment variable not found.")

class Coordinate(typing_ext.TypedDict):
    x: int
    y: int
    z: int

@app.route('/')
def home():
    return "Roblox-Gemini Bridge is Online!"

@app.route('/api/build', methods=['POST'])
def build_generation():
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify([{"x": 0, "y": 0, "z": 0}]), 400
        
        user_prompt = data['prompt']
        print(f"Generating structure grid for: {user_prompt}")
        
        system_instruction = (
            "You are a 3D building coordinate generator. "
            "Generate a valid JSON array of coordinate objects to build the user's item. "
            "You must provide a large, comprehensive layout using 30 to 60 distinct blocks. "
            "For a house, generate walls (varying x and z while incrementing y) and a flat roof layer."
        )

        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            system_instruction=system_instruction
        )
        
        # Keep the prompt simple and clean so the schema engine doesn't trip up
        response = model.generate_content(
            user_prompt,
            generation_config={
                "response_mime_type": "application_json",
                "response_schema": typing.List[Coordinate]
            }
        )
        
        layout_data = json.loads(response.text)
        return jsonify(layout_data), 200

    except Exception as e:
        print(f"Internal backend crash caught: {str(e)}")
        # A completely unique spiral backup pattern so we know if the API call itself fails
        fallback_spiral = [{"x": i, "y": 0, "z": i} for i in range(8)]
        return jsonify(fallback_spiral), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
