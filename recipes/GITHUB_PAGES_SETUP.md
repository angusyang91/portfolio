# Quick GitHub Pages Setup Guide

## Yes, you can use GitHub Pages! Here's how:

Since GitHub Pages only serves static files, you'll need to:
1. Deploy the Flask backend separately (free options available)
2. Host the frontend on GitHub Pages
3. Connect them together

## Step-by-Step Instructions

### Step 1: Deploy Backend to Render (Free & Easy)

1. Go to [render.com](https://render.com) and sign up (free)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository: `angusyang91/portfolio`
4. Configure:
   - **Name**: `recipesnap-api` (or any name)
   - **Root Directory**: `recipes`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
5. Add Environment Variable:
   - Key: `ANTHROPIC_API_KEY`
   - Value: `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`
6. Click "Create Web Service"
7. Wait for deployment (2-3 minutes)
8. **Copy your service URL** (e.g., `https://recipesnap-api.onrender.com`)

### Step 2: Configure Frontend for GitHub Pages

1. In your local repository, create `recipes/static/config.js`:
   ```javascript
   window.API_BASE_URL = 'https://your-render-url.onrender.com';
   ```
   (Replace with your actual Render URL)

2. Test locally first:
   ```bash
   cd recipes
   python app.py
   ```
   Open `http://localhost:5000` and test that it works

### Step 3: Enable GitHub Pages

1. Go to your GitHub repository: `https://github.com/angusyang91/portfolio`
2. Click **Settings** → **Pages** (left sidebar)
3. Under "Source":
   - Select branch: `main`
   - Select folder: `/ (root)` or create a `docs` folder
4. Click **Save**
5. Your site will be live at: `https://angusyang91.github.io/portfolio/recipes/static/`

### Step 4: Update Files and Push

```bash
cd /Users/angus/Desktop/ghrepo/portfolio
git add recipes/static/config.js recipes/static/index.html recipes/static/config.example.js
git commit -m "Configure for GitHub Pages deployment"
git push origin main
```

## Alternative: Use Railway Instead of Render

1. Go to [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Select your repository
4. Add environment variable: `ANTHROPIC_API_KEY`
5. Set start command: `cd recipes && python app.py`
6. Get your URL and update `config.js`

## Troubleshooting

**CORS Errors?**
- The Flask app already has CORS enabled
- If issues persist, update `app.py`:
  ```python
  CORS(app, origins=["https://angusyang91.github.io"])
  ```

**API not working?**
- Check that your Render/Railway service is running
- Verify the URL in `config.js` is correct
- Check browser console for errors

**Frontend not loading?**
- Make sure GitHub Pages is enabled
- Check the correct folder path in Pages settings
- Wait a few minutes for changes to propagate

## Quick Test

Once deployed, test with:
- Frontend: `https://angusyang91.github.io/portfolio/recipes/static/`
- Backend API: `https://your-render-url.onrender.com/api/health`

Both should work! 🎉

