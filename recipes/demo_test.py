"""
Demo test of RecipeSnap extraction using sample recipe content
This simulates what would happen when scraping a real recipe website
"""

from anthropic import Anthropic
import json

print("RecipeSnap - Extraction Demo")
print("="*80)
print("\nSimulating recipe extraction from a typical recipe website...\n")

# This simulates what we'd get from scraping a recipe website like Made with Lau
sample_recipe_html_text = """
Made with Lau - Beef Chow Fun Recipe

HOME RECIPES BEEF CHOW FUN

Beef Chow Fun (Beef Ho Fun)
A Cantonese classic! Silky wide rice noodles wok-tossed with tender beef

Prep Time: 20 minutes
Cook Time: 10 minutes
Total Time: 30 minutes
Servings: 4

Ingredients:

For the beef marinade:
1 pound beef sirloin or flank steak, thinly sliced against the grain
2 tablespoons soy sauce
1 tablespoon Shaoxing wine
1 tablespoon cornstarch
2 teaspoons sesame oil

For the noodles:
1.5 pounds fresh wide rice noodles (ho fun)
3 tablespoons vegetable oil
4 cups bean sprouts
3 scallions, cut into 2-inch pieces
2 tablespoons dark soy sauce
1 tablespoon light soy sauce
1/2 teaspoon white pepper
1/4 teaspoon sugar

Directions:

Step 1: Marinate the beef
In a bowl, combine the sliced beef with soy sauce, Shaoxing wine, cornstarch, and sesame oil. 
Mix well and let marinate for 15-20 minutes while you prep other ingredients.

Step 2: Prepare the noodles
Gently separate the rice noodles if they're stuck together. If they're cold from the fridge, 
you can microwave them for 30 seconds to make them more pliable.

Step 3: Cook the beef
Heat your wok over high heat until smoking. Add 1 tablespoon of oil. Add the marinated beef 
in a single layer and let it sear for 1-2 minutes without moving. Flip and cook another minute 
until just cooked through. Remove beef and set aside.

Step 4: Stir fry the noodles
Add remaining 2 tablespoons oil to the wok. Add the noodles and spread them out. 
Let them sear for 30 seconds, then start tossing. Add dark soy sauce and light soy sauce.

Step 5: Combine everything
Add back the beef, then add bean sprouts and scallions. Toss everything together for 
1-2 minutes. Season with white pepper and sugar. Toss one more time.

Step 6: Serve immediately
Transfer to a serving plate. Best enjoyed immediately while the noodles are still slightly 
crispy from the wok!

Tips from Dad:
- The key is high heat and quick cooking - wok hei!
- Don't overcrowd the wok or noodles will steam instead of fry
- Fresh rice noodles are essential for authentic texture
"""

print("📄 Sample recipe content loaded")
print(f"   Content length: {len(sample_recipe_html_text)} characters\n")

# Now extract with AI
client = Anthropic()

prompt = f"""You are a recipe extraction expert. Extract the recipe information from the following webpage text and format it into a clean, standardized JSON structure.

Webpage text:
{sample_recipe_html_text}

Please extract and format the following information:
1. Recipe title
2. List of ingredients with quantities (standardize measurements)
3. Step-by-step cooking directions (numbered steps)
4. Estimated cooking time (if available)
5. Number of servings (if available)
6. Automatically categorize this recipe with tags for:
   - Cuisine type (e.g., Chinese, Italian, Mexican, Thai, American, etc.)
   - Main ingredient (e.g., beef, chicken, pork, seafood, vegetables, pasta, etc.)
   - Cooking method (e.g., instant pot, oven, stovetop, sous vide, slow cooker, no-cook, grilling, wok, stir-fry)
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
    "cuisine": ["Chinese"],
    "main_ingredient": ["beef"],
    "cooking_method": ["wok", "stovetop"],
    "meal_type": ["dinner"]
  }}
}}

Important:
- Clean up and standardize ingredient measurements
- Make directions clear and actionable
- Number the directions steps
- Be generous with tags - include multiple if applicable
- If information is not available, use null
- Return ONLY valid JSON, no other text"""

print("🤖 Extracting recipe with Claude AI...")

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
recipe['source_url'] = "https://madewithlau.com/recipes/beef-chow-fun"

print("✓ Extraction complete!\n")

# Display the results
print("="*80)
print(f"📋 RECIPE: {recipe['title']}")
print("="*80)

print(f"\n⏱️  Time: {recipe.get('cooking_time', 'Not specified')}")
print(f"🍽️  Servings: {recipe.get('servings', 'Not specified')}")

print("\n📝 INGREDIENTS:")
for i, ingredient in enumerate(recipe['ingredients'], 1):
    print(f"  {i}. {ingredient}")

print("\n👨‍🍳 DIRECTIONS:")
for i, direction in enumerate(recipe['directions'], 1):
    # Truncate long directions for display
    display_direction = direction if len(direction) < 100 else direction[:100] + "..."
    print(f"  {i}. {display_direction}")

print("\n🏷️  AUTO-GENERATED TAGS:")
tags = recipe.get('tags', {})
print(f"  Cuisine: {', '.join(tags.get('cuisine', []))}")
print(f"  Main Ingredient: {', '.join(tags.get('main_ingredient', []))}")
print(f"  Cooking Method: {', '.join(tags.get('cooking_method', []))}")
print(f"  Meal Type: {', '.join(tags.get('meal_type', []))}")

print(f"\n🔗 Source: {recipe['source_url']}")

# Save to file
with open('demo_recipe_output.json', 'w') as f:
    json.dump(recipe, f, indent=2)

print("\n💾 Full recipe data saved to: demo_recipe_output.json")

print("\n" + "="*80)
print("✅ DEMO SUCCESSFUL!")
print("="*80)

print("\n💡 What just happened:")
print("   1. ✓ Scraped recipe content (simulated)")
print("   2. ✓ Used Claude AI to extract structured data")
print("   3. ✓ Auto-tagged by cuisine, ingredient, method, meal type")
print("   4. ✓ Standardized measurements and format")
print("   5. ✓ Generated clean JSON output")

print("\n📊 Cost for this extraction: ~$0.003-0.008")
print("\n🎯 Next steps:")
print("   - Test on your local machine with real recipe URLs")
print("   - Try different recipe websites")
print("   - Push to GitHub and continue with Claude Code for full app")
