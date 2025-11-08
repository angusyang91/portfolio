"""
Flask API server for RecipeSnap - Recipe Extractor
Provides REST API endpoints for recipe extraction
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from recipe_extractor import RecipeExtractor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for frontend

# Initialize recipe extractor
try:
    extractor = RecipeExtractor()
except ValueError as e:
    print(f"Warning: {e}")
    extractor = None


@app.route('/')
def index():
    """Serve the main web interface"""
    return send_from_directory('static', 'index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'extractor_ready': extractor is not None
    })


@app.route('/api/extract', methods=['POST'])
def extract_recipe():
    """
    Extract recipe from URL
    
    Request body:
    {
        "url": "https://example.com/recipe"
    }
    
    Returns:
    {
        "success": true,
        "recipe": {...},
        "error": null
    }
    """
    if extractor is None:
        return jsonify({
            'success': False,
            'error': 'Recipe extractor not initialized. Please check ANTHROPIC_API_KEY environment variable.',
            'recipe': None
        }), 500
    
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: url',
                'recipe': None
            }), 400
        
        url = data['url'].strip()
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL cannot be empty',
                'recipe': None
            }), 400
        
        # Extract recipe
        recipe = extractor.extract_recipe(url)
        
        return jsonify({
            'success': True,
            'recipe': recipe,
            'error': None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'recipe': None
        }), 500


@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint with sample data"""
    return jsonify({
        'success': True,
        'message': 'API is working!',
        'extractor_ready': extractor is not None
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)

