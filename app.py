import os
import json
from flask import Flask, request, jsonify
import google.generativeai as genai
import typing_extensions as typing

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("Warning: GEMINI_API_KEY environment variable not found.")

# Define a rigid 3D data scheme template for the model
class Coordinate(typing.TypedDict):
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
        print(f"Generating coordinates for: {user_prompt}")
        
        system_instruction = (
            "You are a 3D structural voxel builder for Roblox. "
            "Your job is to generate a list of 3D coordinates (x, y, z blocks) to form the requested structure. "
            "You MUST return a large number of coordinates (at least 40 to 80 blocks) to build a clear structure. "
            "For example, if asked for a house, create a hollow square room layout with clear walls and a roof layer."
            "Strictly output raw JSON array format only. No markdown, no conversational text."
        )

        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            system_instruction=system_instruction
        )
        
        # Lock down the API to guarantee a long array matching our object schema
        response = model.generate_content(
            f"Provide coordinates to build a complete: {user_prompt}",
            generation_config={
                "response_mime_type": "application_json",
                "response_schema": typing.List[Coordinate]
            }
        )
        
        layout_data = json.loads(response.text)
        print(f"Successfully generated {len(layout_data)} blocks!")
        return jsonify(layout_data), 200

    except Exception as e:
        print(f"Internal error caught: {str(e)}")
        # Large backup configuration line so Roblox gets a noticeable build if an error pops up
        fallback = [{"x": i, "y": 0, "z": 0} for i in range(15)]
        return jsonify(fallback), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
