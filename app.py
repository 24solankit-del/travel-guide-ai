from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import anthropic
import base64
import os
from pathlib import Path

app = Flask(__name__, static_folder='static', template_folder='templates')

# Configuration
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_image_media_type(filename):
    """Get the media type based on file extension."""
    extension = Path(filename).suffix.lower()
    media_type_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    return media_type_map.get(extension, 'image/jpeg')

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    """API endpoint to analyze an image."""
    try:
        # Check if file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Unsupported file format. Allowed: JPG, PNG, GIF, WEBP'}), 400
        
        # Read the file directly from memory
        file_content = file.read()
        
        # Check file size
        if len(file_content) > MAX_FILE_SIZE:
            return jsonify({'error': 'File is too large. Maximum size is 20MB'}), 400
        
        # Encode the image
        image_data = base64.standard_b64encode(file_content).decode('utf-8')
        media_type = get_image_media_type(file.filename)
        
        # Initialize the Anthropic client
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            return jsonify({'error': 'API key not configured'}), 500
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # Create the prompt
        system_prompt = """You are an expert travel guide and historian. When provided with an image of a place, you should:

1. Identify the location/landmark shown in the image
2. Provide detailed historical background information
3. Explain the cultural significance
4. Share interesting facts and anecdotes
5. Mention key historical periods or events related to the place
6. Suggest best times to visit and nearby attractions
7. Provide information about architecture/design if relevant

Format your response in a clear, engaging manner with proper sections and markdown formatting."""

        user_message = """Please analyze this image and provide comprehensive historical information about the place shown. 
Include sections for:
- Location/Landmark Name
- Historical Background
- Key Historical Events
- Cultural Significance
- Interesting Facts
- Best Time to Visit
- Nearby Attractions"""

        # Call the Claude API
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": user_message
                        }
                    ],
                }
            ],
        )
        
        return jsonify({
            'success': True,
            'analysis': message.content[0].text
        })
    
    except Exception as e:
        return jsonify({'error': f'Error analyzing image: {str(e)}'}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return jsonify({'error': 'File is too large. Maximum size is 20MB'}), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    app.run(debug=False)