import os
import json
import re
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
            return jsonify([{"x": 0, "y": 0, "z": 0}]), 400
        
        user_prompt = data['prompt']
        # Default to 40 if Roblox fails to send the count for some reason
        block_count = data.get('block_count', 40) 
        print(f"Generating a {user_prompt} using exactly {block_count} blocks.")
        
        system_instruction = (
            f"You are a 3D structural voxel placement compiler for Roblox.\n"
            f"CRITICAL RULE: You MUST return a valid JSON array containing EXACTLY {block_count} coordinate objects. No more, no less.\n"
            f"Each object inside the array must contain lowercase keys 'x', 'y', and 'z' with integer values.\n"
            f"Example format layout: [{{'x':0,'y':0,'z':0}}, {{'x':1,'y':0,'z':0}}].\n"
            f"Distribute all {block_count} blocks evenly across 3D space to construct a recognizable structural shell of a: '{user_prompt}'.\n"
            f"For a house, create walls and a roof layer. For a ship, shape a hollow hull.\n"
            f"Provide ONLY the raw JSON list data array. Do not include markdown wraps or conversational text."
        )

        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            system_instruction=system_instruction
        )
        
        response = model.generate_content(
            f"Map out a blueprint array using exactly {block_count} elements for a: {user_prompt}"
        )
        
        raw_text = response.text.strip()
        match = re.search(r'\[\s*\{.*\}\s*\]', raw_text, re.DOTALL)
        if match:
            clean_json = match.group(0)
        else:
            clean_json = raw_text.replace("```json", "").replace("```", "").strip()

        layout_data = json.loads(clean_json)
        return jsonify(layout_data), 200

    except Exception as e:
        print(f"Internal Error Caught: {str(e)}")
        # Dynamic fallback box loop that uses whatever the block count request was
        fallback_box = [{"x": i % 10, "y": i // 10, "z": 0} for i in range(block_count)]
        return jsonify(fallback_box), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
