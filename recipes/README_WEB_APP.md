# RecipeSnap Web App

A beautiful web interface for the RecipeSnap recipe extractor. Extract clean, formatted recipes from any recipe website with a modern, user-friendly UI.

## Features

- 🎨 Modern, responsive web interface
- ⚡ Real-time recipe extraction
- 📱 Mobile-friendly design
- 🏷️ Automatic recipe tagging (cuisine, ingredients, cooking method, meal type)
- ✨ Clean, formatted recipe display
- 🔗 Quick example URLs to test

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or with the `--break-system-packages` flag if needed:

```bash
pip install -r requirements.txt --break-system-packages
```

### 2. Set Up API Key

Make sure you have your Anthropic API key set in a `.env` file:

```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

### 3. Run the Web App

```bash
python app.py
```

The app will start on `http://localhost:5000`

Open your browser and navigate to:
```
http://localhost:5000/static/index.html
```

Or you can access the API directly at:
```
http://localhost:5000/api/extract
```

## Usage

1. Open the web interface in your browser
2. Paste a recipe URL into the input field
3. Click "Extract Recipe" or press Enter
4. Wait a few seconds for the extraction to complete
5. View the beautifully formatted recipe with ingredients, directions, and tags

## API Endpoints

### POST `/api/extract`

Extract a recipe from a URL.

**Request:**
```json
{
  "url": "https://madewithlau.com/recipes/beef-chow-fun"
}
```

**Response:**
```json
{
  "success": true,
  "recipe": {
    "title": "Beef Chow Fun",
    "ingredients": [...],
    "directions": [...],
    "cooking_time": "30 minutes",
    "servings": "4 servings",
    "tags": {...},
    "source_url": "..."
  },
  "error": null
}
```

### GET `/api/health`

Check if the API is running and the extractor is ready.

**Response:**
```json
{
  "status": "healthy",
  "extractor_ready": true
}
```

## Project Structure

```
recipes/
├── app.py                 # Flask API server
├── recipe_extractor.py    # Core extraction logic
├── static/
│   └── index.html        # Web UI
├── requirements.txt      # Python dependencies
└── README.md            # Original README
```

## Troubleshooting

### Port Already in Use

If port 5000 is already in use, you can change it:

```bash
PORT=5001 python app.py
```

### CORS Issues

The app includes CORS support, but if you encounter issues, make sure `flask-cors` is installed.

### API Key Not Found

Make sure your `.env` file exists and contains:
```
ANTHROPIC_API_KEY=sk-ant-...
```

## Development

To run in debug mode:

```bash
FLASK_DEBUG=true python app.py
```

## Next Steps

- Add recipe saving/export functionality
- Add recipe history
- Add user accounts
- Add recipe collections
- Deploy to production

