"""
RecipeSnap - Recipe Extractor
This script extracts recipes from URLs, cleans them up, and formats them consistently.
"""

import os
import json
import requests
from bs4 import BeautifulSoup
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class RecipeExtractor:
    """Extracts and formats recipes from URLs using web scraping and AI."""
    
    def __init__(self, api_key=None):
        """
        Initialize the recipe extractor.
        
        Args:
            api_key (str): Anthropic API key. If not provided, reads from ANTHROPIC_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable.")
        
        # Use default API key from the session if available
        self.client = Anthropic()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def scrape_webpage(self, url):
        """
        Scrape the HTML content from a recipe URL.
        
        Args:
            url (str): The recipe URL to scrape
            
        Returns:
            str: Cleaned text content from the webpage
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up excessive whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = '\n'.join(lines)
            
            return text
            
        except requests.RequestException as e:
            raise Exception(f"Failed to scrape URL: {str(e)}")
    
    def extract_recipe_with_ai(self, webpage_text, source_url):
        """
        Use Claude AI to extract and format recipe information from webpage text.
        
        Args:
            webpage_text (str): The scraped text content from the recipe webpage
            source_url (str): The original URL of the recipe
            
        Returns:
            dict: Structured recipe data
        """
        prompt = f"""You are a recipe extraction expert. Extract the recipe information from the following webpage text and format it into a clean, standardized JSON structure.

Webpage text:
{webpage_text[:8000]}  # Limit to first 8000 chars to stay within context

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
    "2 eggs",
    ...
  ],
  "directions": [
    "Step 1: ...",
    "Step 2: ...",
    ...
  ],
  "cooking_time": "30 minutes" or null,
  "servings": "4 servings" or null,
  "tags": {{
    "cuisine": ["Chinese"],
    "main_ingredient": ["beef"],
    "cooking_method": ["stovetop", "wok"],
    "meal_type": ["dinner"]
  }}
}}

Important:
- Clean up and standardize ingredient measurements (e.g., "1/2 c" becomes "1/2 cup")
- Make directions clear and actionable
- Number the directions steps
- Be generous with tags - include multiple if applicable
- If information is not available, use null
- Return ONLY valid JSON, no other text"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            recipe_data = json.loads(response_text)
            recipe_data['source_url'] = source_url
            
            return recipe_data
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI response as JSON: {str(e)}\nResponse: {response_text}")
        except Exception as e:
            raise Exception(f"AI extraction failed: {str(e)}")
    
    def extract_recipe(self, url):
        """
        Complete recipe extraction pipeline: scrape webpage and extract recipe with AI.
        
        Args:
            url (str): The recipe URL to extract
            
        Returns:
            dict: Structured recipe data
        """
        print(f"Scraping recipe from: {url}")
        webpage_text = self.scrape_webpage(url)
        
        print("Extracting recipe with AI...")
        recipe_data = self.extract_recipe_with_ai(webpage_text, url)
        
        print(f"✓ Successfully extracted: {recipe_data['title']}")
        return recipe_data


def main():
    """
    Main function for testing the recipe extractor.
    Run this script directly to test recipe extraction.
    """
    # Example usage
    test_urls = [
        "https://www.seriouseats.com/the-best-chili-recipe",
        # Add more test URLs here
    ]
    
    try:
        extractor = RecipeExtractor()
        
        for url in test_urls:
            print("\n" + "="*80)
            recipe = extractor.extract_recipe(url)
            
            # Pretty print the recipe
            print("\nExtracted Recipe:")
            print(json.dumps(recipe, indent=2))
            print("="*80)
            
    except ValueError as e:
        print(f"Error: {e}")
        print("\nPlease set your ANTHROPIC_API_KEY in a .env file")
        print("Copy .env.example to .env and add your API key")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
