import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# 1. Configure Gemini using the Environment Variable we set up on Render
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("Warning: GEMINI_API_KEY environment variable not found.")

@app.route('/')
def home():
    return "Roblox-Gemini Bridge is Online!"

# 2. This creates the /api/build endpoint that Roblox will talk to
@app.route('/api/build', methods=['POST'])
def build_generation():
    try:
        # Get data sent from Roblox Studio
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing prompt in request data"}), 400
        
        user_prompt = data['prompt']
        
        # 3. Request a response from the Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(user_prompt)
        
        # 4. Send the text result back to Roblox
        return jsonify({
            "status": "success",
            "reply": response.text
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Render requires the app to listen on port 10000 by default
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
