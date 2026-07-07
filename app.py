import os
import json
from flask import Flask, request, jsonify
import google.generativeai as genai
import typing # Built-in module for standard structures like List
import typing_extensions as typing_ext # Used explicitly for TypedDict schema rules

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("Warning: GEMINI_API_KEY environment variable not found.")

# Define the data schema using extensions
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
            "You are an advanced 3D structural voxel builder for Roblox. "
            "Your job is to generate a detailed list of 3D coordinates (x, y, z blocks) to build the requested shape. "
            "You must return a large layout containing between 30 and 60 coordinate points. "
            "For a house, generate walls, an entry gap, and a flat roof layer by varying x, y, and z numbers."
        )

        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            system_instruction=system_instruction
        )
        
        # Enforce strict layout constraints using Python's core typing structures
        response = model.generate_content(
            f"Provide an array of blocks to construct a: {user_prompt}",
            generation_config={
                "response_mime_type": "application_json",
                "response_schema": typing.List[Coordinate]
            }
        )
        
        # Parse the output array directly
        layout_data = json.loads(response.text)
        return jsonify(layout_data), 200

    except Exception as e:
        print(f"Internal backend crash caught: {str(e)}")
        # Noticeable stair pattern fallback to alert us if it still hits an exception
        fallback_stairs = [{"x": i, "y": i, "z": 0} for i in range(10)]
        return jsonify(fallback_stairs), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
