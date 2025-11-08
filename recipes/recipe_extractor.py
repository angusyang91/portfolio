"""
RecipeSnap - Recipe Extractor
This script extracts recipes from URLs using AI, matching the output format from the Recipes repo.
Uses Anthropic Claude API instead of Gemini.
"""

import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class RecipeExtractor:
    """Extracts and formats recipes from URLs using AI."""
    
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
    
    def extract_recipe(self, url):
        """
        Extract recipe from URL using AI.
        Matches the output format from the Recipes repo.
        
        Args:
            url (str): The recipe URL to extract
            
        Returns:
            dict: Structured recipe data with format:
            {
                "recipeName": str,
                "ingredients": [str, ...],
                "instructions": [str, ...],
                "applianceInstructions": [
                    {
                        "applianceName": str,
                        "instructions": [str, ...]
                    }
                ]
            }
        """
        print(f"Extracting recipe from: {url}")
        
        # Prompt matching the Recipes repo approach
        appliance_prompt_section = """
After extracting the main instructions, please analyze them.
1. If the recipe involves using a pressure cooker, add a set of specific, alternative instructions under the appliance name "Instant Pot" in the "applianceInstructions" field.
2. If the recipe involves baking or air frying, add a set of specific, alternative instructions under the appliance name "Breville Smart Oven Toaster Pro" in the "applianceInstructions" field.

If neither of these conditions are met, the "applianceInstructions" field MUST be an empty array [].
"""

        prompt = f"""From the URL: {url}, extract the recipe name, the ingredients, and the primary cooking instructions.
{appliance_prompt_section}
Ignore all non-recipe content like stories, ads, and comments.

Return ONLY a valid JSON object with this exact structure:
{{
  "recipeName": "Recipe Name",
  "ingredients": [
    "1 cup flour",
    "2 eggs",
    ...
  ],
  "instructions": [
    "Step 1: ...",
    "Step 2: ...",
    ...
  ],
  "applianceInstructions": [
    {{
      "applianceName": "Instant Pot",
      "instructions": ["Step 1: ...", "Step 2: ..."]
    }}
  ]
}}

Important:
- Clean up and standardize ingredient measurements
- Make instructions clear and actionable
- Number the instructions if they aren't already numbered
- Only include applianceInstructions if the recipe can be adapted for Instant Pot or Breville Smart Oven
- Return ONLY valid JSON, no other text"""

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
                            "recipeName": None,
                            "ingredients": [],
                            "instructions": [],
                            "applianceInstructions": []
                        }
                else:
                    # No JSON found, return empty structure
                    print(f"Warning: No JSON found in AI response. Response: {response_text[:200]}")
                    recipe_data = {
                        "recipeName": None,
                        "ingredients": [],
                        "instructions": [],
                        "applianceInstructions": []
                    }
            
            # Ensure all required fields exist
            if 'recipeName' not in recipe_data:
                recipe_data['recipeName'] = recipe_data.get('title') or None
            if 'ingredients' not in recipe_data:
                recipe_data['ingredients'] = []
            if 'instructions' not in recipe_data:
                recipe_data['instructions'] = recipe_data.get('directions') or []
            if 'applianceInstructions' not in recipe_data:
                recipe_data['applianceInstructions'] = []
            
            # Ensure applianceInstructions is a list
            if not isinstance(recipe_data.get('applianceInstructions'), list):
                recipe_data['applianceInstructions'] = []
            
            print(f"✓ Successfully extracted: {recipe_data.get('recipeName', 'Unknown')}")
            return recipe_data
            
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error. Response was: {response_text[:500]}")
            # Return empty structure instead of raising
            return {
                "recipeName": None,
                "ingredients": [],
                "instructions": [],
                "applianceInstructions": []
            }
        except Exception as e:
            print(f"AI extraction error: {str(e)}")
            raise Exception(f"AI extraction failed: {str(e)}")


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
