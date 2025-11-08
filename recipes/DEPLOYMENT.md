# Deployment Guide for RecipeSnap

This guide covers different deployment options for the RecipeSnap web app.

## Option 1: GitHub Pages (Frontend Only) + Separate Backend

GitHub Pages can host the static frontend, but you'll need to deploy the Flask backend separately.

### Step 1: Deploy Flask Backend

Choose one of these platforms:

#### A. Render (Recommended - Free tier available)
1. Go to [render.com](https://render.com) and sign up
2. Create a new "Web Service"
3. Connect your GitHub repository
4. Set:
   - **Build Command**: `pip install -r recipes/requirements.txt`
   - **Start Command**: `cd recipes && python app.py`
   - **Environment Variables**: Add `ANTHROPIC_API_KEY` with your API key
5. Note the URL (e.g., `https://your-app.onrender.com`)

#### B. Railway
1. Go to [railway.app](https://railway.app) and sign up
2. Create a new project from GitHub
3. Add environment variable: `ANTHROPIC_API_KEY`
4. Set start command: `cd recipes && python app.py`
5. Note the URL

#### C. Heroku
1. Install Heroku CLI
2. Create `Procfile` in recipes folder:
   ```
   web: cd recipes && python app.py
   ```
3. Deploy: `heroku create your-app-name && git push heroku main`
4. Set environment variable: `heroku config:set ANTHROPIC_API_KEY=your_key`

### Step 2: Update Frontend for GitHub Pages

1. Create a `config.js` file in the `static` folder:
   ```javascript
   window.API_BASE_URL = 'https://your-backend-url.onrender.com';
   ```

2. Update `index.html` to load the config:
   ```html
   <script src="config.js"></script>
   <script>
   // ... rest of your code
   ```

3. Or update the API_BASE_URL directly in `index.html`:
   ```javascript
   const API_BASE_URL = 'https://your-backend-url.onrender.com';
   ```

### Step 3: Enable GitHub Pages

1. Go to your repository settings
2. Navigate to "Pages"
3. Select source branch (usually `main`)
4. Select folder: `/recipes/static` or `/ (root)` if you move files
5. Your site will be at: `https://yourusername.github.io/portfolio/recipes/static/`

**Important**: Make sure your backend has CORS enabled (already done in `app.py`).

## Option 2: Full Stack Deployment (Backend + Frontend Together)

### Vercel (Serverless Functions)

1. Install Vercel CLI: `npm i -g vercel`
2. Create `vercel.json`:
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "recipes/app.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/api/(.*)",
         "dest": "recipes/app.py"
       },
       {
         "src": "/(.*)",
         "dest": "recipes/static/$1"
       }
     ]
   }
   ```
3. Deploy: `vercel`

### Netlify

1. Create `netlify.toml`:
   ```toml
   [build]
     command = "pip install -r recipes/requirements.txt"
     publish = "recipes/static"
   
   [[redirects]]
     from = "/api/*"
     to = "/.netlify/functions/api/:splat"
     status = 200
   ```
2. Deploy via Netlify dashboard or CLI

## Option 3: Local Development

For local testing:

```bash
cd recipes
pip install -r requirements.txt
python app.py
```

Then open: `http://localhost:5000`

## CORS Configuration

The Flask app already has CORS enabled. If you deploy the frontend and backend separately, make sure:

1. Backend allows requests from your frontend domain
2. Update `app.py` if needed:
   ```python
   CORS(app, origins=["https://yourusername.github.io"])
   ```

## Environment Variables

Always keep your `ANTHROPIC_API_KEY` secure:
- Never commit `.env` files
- Use environment variables in your hosting platform
- `.env` is already in `.gitignore`

## Quick GitHub Pages Setup

1. Deploy backend to Render/Railway (get URL)
2. Update `static/index.html` line 429:
   ```javascript
   const API_BASE_URL = 'https://your-backend-url.onrender.com';
   ```
3. Push changes to GitHub
4. Enable GitHub Pages in repository settings
5. Done! 🎉

