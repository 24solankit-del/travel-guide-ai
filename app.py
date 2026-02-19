from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/analyze_image', methods=['POST'])
def analyze_image():
    # Get the image file from the request
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    image = request.files['image']
    
    # Code to send the image to Claude AI for analysis
    # Assuming there's an API endpoint for Claude AI:
    claude_ai_url = 'https://api.claude.ai/v1/analyze'
    files = {'image': image}
    response = requests.post(claude_ai_url, files=files)

    if response.status_code != 200:
        return jsonify({'error': 'Image analysis failed'}), 500

    # Return the analysis result
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True)