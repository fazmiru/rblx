import os
import json
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("Error: GEMINI_API_KEY environment variable is missing on Render!")

@app.route('/')
def home():
    return "Roblox-Gemini Bridge is Online!"

@app.route('/api/build', methods=['POST'])
def build_generation():
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "No prompt sent from Roblox"}), 400
        
        user_prompt = data['prompt']
        
        system_instruction = (
            "You are a Roblox building generator. The user wants to build something. "
            "You must return a valid JSON array of coordinate objects. "
            "Example layout format: [{\"x\":0,\"y\":0,\"z\":0}, {\"x\":1,\"y\":0,\"z\":0}]. "
            "Generate at least 15-20 distinct coordinates to make a recognizable shape. "
            "Output the raw JSON array data only. No markdown, no backticks."
        )

        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            system_instruction=system_instruction
        )
        
        response = model.generate_content(
            f"Generate structural coordinates to build a: {user_prompt}"
        )
        
        # Clean up text if Gemini wrapped it in markdown code blocks
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        
        # Convert string to clean JSON list data
        coordinate_list = json.loads(clean_text)
        return jsonify(coordinate_list), 200

    except Exception as e:
        print(f"Server Error: {str(e)}")
        # Return the actual error message straight to Roblox output so we can see it!
        return jsonify([{"x": 0, "y": 0, "z": 0}, {"error_log": str(e)}]), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
