"""
Quick inline test of the recipe extractor
"""

import requests
from bs4 import BeautifulSoup
from anthropic import Anthropic
import json

# Test with a simple recipe
test_url = "https://www.allrecipes.com/recipe/23600/worlds-best-lasagna/"

print("RecipeSnap - Quick Test")
print("="*80)
print(f"\n📥 Extracting recipe from:\n{test_url}\n")

# Scrape webpage
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(test_url, headers=headers, timeout=10)
soup = BeautifulSoup(response.content, 'lxml')

# Remove script and style elements
for script in soup(["script", "style", "nav", "footer", "header"]):
    script.decompose()

# Get text content
text = soup.get_text(separator='\n', strip=True)
lines = [line.strip() for line in text.splitlines() if line.strip()]
webpage_text = '\n'.join(lines)

print("✓ Webpage scraped successfully")
print(f"  Content length: {len(webpage_text)} characters\n")

# Extract with AI
client = Anthropic()

prompt = f"""You are a recipe extraction expert. Extract the recipe information from the following webpage text and format it into a clean, standardized JSON structure.

Webpage text:
{webpage_text[:8000]}

Please extract and format the following information:
1. Recipe title
2. List of ingredients with quantities (standardize measurements)
3. Step-by-step cooking directions (numbered steps)
4. Estimated cooking time (if available)
5. Number of servings (if available)
6. Automatically categorize this recipe with tags for:
   - Cuisine type (e.g., Chinese, Italian, Mexican, Thai, American, etc.)
   - Main ingredient (e.g., beef, chicken, pork, seafood, vegetables, pasta, etc.)
   - Cooking method (e.g., instant pot, oven, stovetop, sous vide, slow cooker, no-cook, grilling)
   - Meal type (e.g., breakfast, lunch, dinner, dessert, snack, appetizer)

Return ONLY a valid JSON object with this exact structure:
{{
  "title": "Recipe Name",
  "ingredients": [
    "1 cup flour",
    "2 eggs"
  ],
  "directions": [
    "Step 1: ...",
    "Step 2: ..."
  ],
  "cooking_time": "30 minutes" or null,
  "servings": "4 servings" or null,
  "tags": {{
    "cuisine": ["Italian"],
    "main_ingredient": ["beef"],
    "cooking_method": ["oven"],
    "meal_type": ["dinner"]
  }}
}}

Important:
- Clean up and standardize ingredient measurements
- Make directions clear and actionable
- Number the directions steps
- Be generous with tags
- If information is not available, use null
- Return ONLY valid JSON, no other text"""

print("🤖 Extracting recipe with AI...")

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4000,
    messages=[{"role": "user", "content": prompt}]
)

response_text = message.content[0].text.strip()

# Remove markdown code blocks if present
if response_text.startswith("```"):
    response_text = response_text.split("```")[1]
    if response_text.startswith("json"):
        response_text = response_text[4:]
    response_text = response_text.strip()

recipe = json.loads(response_text)
recipe['source_url'] = test_url

print("✓ AI extraction complete\n")

# Display results
print("="*80)
print(f"📋 RECIPE: {recipe['title']}")
print("="*80)

print(f"\n⏱️  Time: {recipe.get('cooking_time', 'Not specified')}")
print(f"🍽️  Servings: {recipe.get('servings', 'Not specified')}")

print("\n📝 INGREDIENTS:")
for i, ingredient in enumerate(recipe['ingredients'][:10], 1):  # Show first 10
    print(f"  {i}. {ingredient}")
if len(recipe['ingredients']) > 10:
    print(f"  ... and {len(recipe['ingredients']) - 10} more")

print("\n👨‍🍳 DIRECTIONS:")
for i, direction in enumerate(recipe['directions'][:5], 1):  # Show first 5
    print(f"  {i}. {direction}")
if len(recipe['directions']) > 5:
    print(f"  ... and {len(recipe['directions']) - 5} more steps")

print("\n🏷️  TAGS:")
tags = recipe.get('tags', {})
print(f"  Cuisine: {', '.join(tags.get('cuisine', []))}")
print(f"  Main Ingredient: {', '.join(tags.get('main_ingredient', []))}")
print(f"  Cooking Method: {', '.join(tags.get('cooking_method', []))}")
print(f"  Meal Type: {', '.join(tags.get('meal_type', []))}")

print(f"\n🔗 Source: {recipe['source_url']}")

# Save to file
with open('test_recipe_output.json', 'w') as f:
    json.dump(recipe, f, indent=2)

print("\n💾 Full recipe saved to: test_recipe_output.json")
print("\n" + "="*80)
print("✅ TEST SUCCESSFUL!")
print("="*80)
