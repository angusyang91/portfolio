# RecipeSnap - Recipe Extractor

This is the core recipe extraction component for RecipeSnap. It scrapes recipe websites and uses AI to extract clean, formatted recipe data.

## What This Does

- Takes any recipe URL
- Scrapes the webpage content
- Uses Claude AI to extract:
  - Recipe title
  - Ingredients (cleaned and standardized)
  - Step-by-step directions
  - Cooking time and servings
  - Automatic tags (cuisine, main ingredient, cooking method, meal type)
- Returns clean JSON data

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install with the `--break-system-packages` flag if needed:

```bash
pip install -r requirements.txt --break-system-packages
```

### 2. Set Up Your API Key

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Get your Anthropic API key:
   - Go to https://console.anthropic.com/
   - Sign in or create an account
   - Navigate to API Keys
   - Create a new API key

3. Edit the `.env` file and add your API key:
   ```
   ANTHROPIC_API_KEY=your_actual_api_key_here
   ```

### 3. Test It Out

Run the test script:

```bash
python test_extractor.py
```

This will extract a recipe from Made with Lau (beef chow fun by default).

## How to Test Different Recipes

Edit `test_extractor.py` and change the `recipe_url` variable to any recipe URL you want to test:

```python
recipe_url = "https://madewithlau.com/recipes/beef-chow-fun"
```

Some good test URLs:
- Made with Lau: https://madewithlau.com/recipes/beef-chow-fun
- Serious Eats: https://www.seriouseats.com/the-best-chili-recipe
- The Woks of Life: https://thewoksoflife.com/chinese-broccoli-beef/
- AllRecipes: https://www.allrecipes.com/recipe/23600/worlds-best-lasagna/
- Budget Bytes: https://www.budgetbytes.com/easy-fried-rice/

## What Gets Extracted

The extractor returns a JSON object with this structure:

```json
{
  "title": "Beef Chow Fun",
  "ingredients": [
    "1 lb beef sirloin, thinly sliced",
    "1 lb fresh rice noodles",
    "2 tablespoons soy sauce",
    ...
  ],
  "directions": [
    "Step 1: Marinate the beef with soy sauce for 15 minutes",
    "Step 2: Heat wok over high heat with oil",
    ...
  ],
  "cooking_time": "30 minutes",
  "servings": "4 servings",
  "tags": {
    "cuisine": ["Chinese", "Cantonese"],
    "main_ingredient": ["beef", "noodles"],
    "cooking_method": ["stovetop", "wok", "stir-fry"],
    "meal_type": ["dinner"]
  },
  "source_url": "https://madewithlau.com/recipes/beef-chow-fun"
}
```

## Cost Estimate

Each recipe extraction costs approximately $0.003-0.015 depending on the length of the recipe.

- 10 recipes = ~$0.03-0.15
- 100 recipes = ~$0.30-1.50

You can monitor your usage at https://console.anthropic.com/

## Using the Extractor in Your Code

```python
from recipe_extractor import RecipeExtractor

# Initialize
extractor = RecipeExtractor()

# Extract a recipe
recipe = extractor.extract_recipe("https://example.com/recipe")

# Access the data
print(recipe['title'])
print(recipe['ingredients'])
print(recipe['directions'])
print(recipe['tags'])
```

## Troubleshooting

### "Anthropic API key is required"
- Make sure you created a `.env` file (not just `.env.example`)
- Check that your API key is correctly pasted in the `.env` file
- API key should start with `sk-ant-`

### Recipe extraction fails
- Some websites have anti-scraping measures
- Try different recipe websites
- Check your internet connection
- Some sites may be blocked or require authentication

### "Failed to parse AI response as JSON"
- This is rare but can happen with unusual recipe formats
- Try a different recipe URL
- The AI might need better instructions for that specific site

## Next Steps

Once you've tested this and confirmed it works well:

1. Test with 5-10 different recipe websites
2. Check if the ingredient extraction is accurate
3. Verify the auto-tagging makes sense
4. Push this code to GitHub
5. Use Claude Code to build the full web app around this extractor

## Files in This Project

- `recipe_extractor.py` - Main extraction logic
- `test_extractor.py` - Simple test script
- `requirements.txt` - Python dependencies
- `.env.example` - Example environment variables
- `README.md` - This file

## Questions?

If something isn't working, check:
1. Did you install the dependencies?
2. Did you set up your API key in `.env`?
3. Do you have internet connection?
4. Is the recipe URL valid and accessible?
