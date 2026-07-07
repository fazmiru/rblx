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
        block_count = data.get('block_count', 40) 
        print(f"Generating 3D structure for '{user_prompt}' using exactly {block_count} blocks.")
        
        system_instruction = (
            f"You are an expert 3D structural voxel placement compiler for Roblox.\n"
            f"CRITICAL RULE 1: You MUST return a valid JSON array containing EXACTLY {block_count} coordinate objects.\n"
            f"CRITICAL RULE 2: The structure MUST BE fully 3D. Do NOT place all blocks on a flat line or flat wall plane. You must vary 'x', 'y', and 'z'.\n"
            f"Each object must use lowercase keys 'x', 'y', and 'z' with integer values.\n"
            f"Example format layout: [{{'x':0,'y':0,'z':0}}, {{'x':1,'y':0,'z':1}}].\n\n"
            f"How to build the requested '{user_prompt}':\n"
            f"- If a 'house': Build a hollow 3D box shell. Use blocks to make a perimeter square foundation layout (e.g., x from 0 to 4, z from 0 to 4), then stack walls upward by incrementing y, and put a flat layer of remaining blocks on top for the roof.\n"
            f"- If a 'ship': Build a hollow 3D boat hull. Use coordinates to outline a pointed base, widen it out as y goes higher, and leave the interior empty.\n"
            f"- For any other item: Always branch out across the width (x), height (y), and depth (z) to make a solid or hollow 3D shape.\n\n"
            f"Provide ONLY the raw JSON list data array. Do not include markdown wraps or conversational text."
        )

        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            system_instruction=system_instruction
        )
        
        response = model.generate_content(
            f"Map out a fully 3D blueprint array using exactly {block_count} elements for a: {user_prompt}"
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
        # 3D cube fallback outline frame if the engine errors out
        fallback_3d = []
        for y in range(3):
            for x in range(3):
                for z in range(3):
                    if len(fallback_3d) < block_count:
                        fallback_3d.append({"x": x, "y": y, "z": z})
        return jsonify(fallback_3d), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
