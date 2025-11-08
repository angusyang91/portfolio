"""
Simple test script for RecipeSnap extractor.
Edit the recipe_url variable below to test different recipes.
"""

from recipe_extractor import RecipeExtractor
import json

# 🔥 EDIT THIS URL TO TEST DIFFERENT RECIPES 🔥
recipe_url = "https://www.seriouseats.com/the-best-chili-recipe"

# Alternative test URLs you can try:
# recipe_url = "https://www.seriouseats.com/the-best-chili-recipe"
# recipe_url = "https://www.allrecipes.com/recipe/23600/worlds-best-lasagna/"
# recipe_url = "https://thewoksoflife.com/chinese-broccoli-beef/"
# recipe_url = "https://www.budgetbytes.com/easy-fried-rice/"

def main():
    print("RecipeSnap - Testing Recipe Extraction")
    print("="*80)
    
    try:
        # Initialize the extractor
        extractor = RecipeExtractor()
        
        # Extract the recipe
        print(f"\n📥 Extracting recipe from:\n{recipe_url}\n")
        recipe = extractor.extract_recipe(recipe_url)
        
        # Display the results
        print("\n✅ EXTRACTION SUCCESSFUL!\n")
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
            print(f"  {i}. {direction}")
        
        print("\n🏷️  TAGS:")
        tags = recipe.get('tags', {})
        print(f"  Cuisine: {', '.join(tags.get('cuisine', []))}")
        print(f"  Main Ingredient: {', '.join(tags.get('main_ingredient', []))}")
        print(f"  Cooking Method: {', '.join(tags.get('cooking_method', []))}")
        print(f"  Meal Type: {', '.join(tags.get('meal_type', []))}")
        
        print(f"\n🔗 Source: {recipe['source_url']}")
        
        # Save to file for inspection
        output_file = "extracted_recipe.json"
        with open(output_file, 'w') as f:
            json.dump(recipe, f, indent=2)
        print(f"\n💾 Full recipe saved to: {output_file}")
        
        print("\n" + "="*80)
        print("✨ Test complete!")
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\n📝 Setup Instructions:")
        print("1. Copy .env.example to .env")
        print("2. Add your Anthropic API key to the .env file")
        print("3. Get your API key from: https://console.anthropic.com/")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("- Check that the URL is valid and accessible")
        print("- Make sure you have internet connection")
        print("- Verify your API key is correct in .env file")

if __name__ == "__main__":
    main()
