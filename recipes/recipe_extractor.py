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
        
        # Initialize Anthropic client with API key
        self.client = Anthropic(api_key=self.api_key)
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
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # First, try to extract JSON-LD structured data (many recipe sites use this)
            json_ld_data = []
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    import json
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        json_ld_data.append(data)
                    elif isinstance(data, list):
                        json_ld_data.extend(data)
                except:
                    pass
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            # Try multiple strategies to find recipe content
            text_parts = []
            
            # Strategy 1: Look for recipe-specific HTML structures
            recipe_selectors = [
                {'tag': 'div', 'class': lambda x: x and 'recipe' in ' '.join(x).lower()},
                {'tag': 'article', 'class': lambda x: x and 'recipe' in ' '.join(x).lower()},
                {'tag': 'section', 'class': lambda x: x and 'recipe' in ' '.join(x).lower()},
                {'tag': 'main'},
                {'tag': 'article'},
            ]
            
            for selector in recipe_selectors:
                elements = soup.find_all(selector['tag'], class_=selector.get('class'))
                for elem in elements:
                    text = elem.get_text(separator='\n', strip=True)
                    if len(text) > 500:  # Only use if substantial content
                        text_parts.append(text)
            
            # Strategy 2: Look for ingredient and instruction lists
            ingredient_lists = soup.find_all(['ul', 'ol'], class_=lambda x: x and ('ingredient' in ' '.join(x).lower() or 'recipe' in ' '.join(x).lower()))
            for ul in ingredient_lists:
                text_parts.append(ul.get_text(separator='\n', strip=True))
            
            # Strategy 3: Get all text but prioritize longer sections
            if not text_parts or sum(len(t) for t in text_parts) < 500:
                # Fallback: get all text from body
                body = soup.find('body')
                if body:
                    text = body.get_text(separator='\n', strip=True)
                    text_parts.append(text)
            
            # Combine all text parts
            combined_text = '\n\n'.join(text_parts)
            
            # Add JSON-LD data if found
            if json_ld_data:
                combined_text += "\n\n[Structured Data Found]:\n" + json.dumps(json_ld_data, indent=2)
            
            # Clean up excessive whitespace
            lines = [line.strip() for line in combined_text.splitlines() if line.strip()]
            text = '\n'.join(lines)
            
            # If still too short, try getting raw HTML content for AI to parse
            if len(text) < 500:
                print(f"Warning: Scraped content is short ({len(text)} chars). Including HTML structure...")
                # Get HTML content of likely recipe containers
                html_content = ""
                for selector in recipe_selectors:
                    elements = soup.find_all(selector['tag'], class_=selector.get('class'))
                    for elem in elements[:3]:  # Limit to first 3 matches
                        html_content += str(elem) + "\n"
                
                if html_content:
                    # Parse HTML content as text
                    html_soup = BeautifulSoup(html_content, 'html.parser')
                    for script in html_soup(["script", "style"]):
                        script.decompose()
                    html_text = html_soup.get_text(separator='\n', strip=True)
                    text = text + "\n\n" + html_text
            
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
{webpage_text[:12000]}  # Limit to first 12000 chars to stay within context

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
- If the webpage text doesn't contain a complete recipe, do your best to extract what you can find
- Look for structured data (JSON-LD) if present in the text
- Return ONLY valid JSON, no other text
- Even if the recipe is incomplete, return a valid JSON structure with whatever information you can extract"""

        try:
            # Try different model names in order of preference
            models_to_try = [
                "claude-3-5-sonnet-20240620",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ]
            
            message = None
            last_error = None
            
            for model_name in models_to_try:
                try:
                    message = self.client.messages.create(
                        model=model_name,
                        max_tokens=4000,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    print(f"Using model: {model_name}")
                    break  # Success, exit loop
                except Exception as e:
                    last_error = e
                    if "404" in str(e) or "not_found" in str(e).lower():
                        continue  # Try next model
                    else:
                        raise  # Other error, re-raise
            
            if message is None:
                raise Exception(f"None of the models worked. Last error: {last_error}")
            
            response_text = message.content[0].text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                # Find the first ``` and last ```
                parts = response_text.split("```")
                if len(parts) >= 3:
                    response_text = parts[1]  # Get content between first two ```
                    if response_text.startswith("json"):
                        response_text = response_text[4:]
                else:
                    response_text = response_text.replace("```json", "").replace("```", "")
                response_text = response_text.strip()
            
            # Debug: print response if it's suspicious
            if not response_text or len(response_text) < 10:
                print(f"Warning: AI response seems empty or too short: {response_text[:200]}")
            
            # Try to parse JSON
            try:
                recipe_data = json.loads(response_text)
            except json.JSONDecodeError:
                # If parsing fails, try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        recipe_data = json.loads(json_match.group())
                    except:
                        # Last resort: return empty structure
                        print(f"Warning: Could not parse JSON from response. Returning empty structure.")
                        recipe_data = {
                            "title": None,
                            "ingredients": [],
                            "directions": [],
                            "cooking_time": None,
                            "servings": None,
                            "tags": {
                                "cuisine": [],
                                "main_ingredient": [],
                                "cooking_method": [],
                                "meal_type": []
                            }
                        }
                else:
                    # No JSON found, return empty structure
                    print(f"Warning: No JSON found in AI response. Response: {response_text[:200]}")
                    recipe_data = {
                        "title": None,
                        "ingredients": [],
                        "directions": [],
                        "cooking_time": None,
                        "servings": None,
                        "tags": {
                            "cuisine": [],
                            "main_ingredient": [],
                            "cooking_method": [],
                            "meal_type": []
                        }
                    }
            
            # Validate that we got actual data
            if not recipe_data.get('title') and not recipe_data.get('ingredients'):
                print(f"Warning: AI returned empty recipe data. Full response: {response_text[:500]}")
            
            # Ensure all required fields exist
            if 'title' not in recipe_data:
                recipe_data['title'] = None
            if 'ingredients' not in recipe_data:
                recipe_data['ingredients'] = []
            if 'directions' not in recipe_data:
                recipe_data['directions'] = []
            if 'tags' not in recipe_data:
                recipe_data['tags'] = {
                    "cuisine": [],
                    "main_ingredient": [],
                    "cooking_method": [],
                    "meal_type": []
                }
            
            recipe_data['source_url'] = source_url
            
            return recipe_data
            
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error. Response was: {response_text[:500]}")
            # Return empty structure instead of raising
            return {
                "title": None,
                "ingredients": [],
                "directions": [],
                "cooking_time": None,
                "servings": None,
                "tags": {
                    "cuisine": [],
                    "main_ingredient": [],
                    "cooking_method": [],
                    "meal_type": []
                },
                "source_url": source_url
            }
        except Exception as e:
            print(f"AI extraction error: {str(e)}")
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
