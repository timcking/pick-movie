import json
import random

def get_random_item(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            
        # Selects a random item from the list
        items = data.get("watchlist", [])
        if not items:
            return "The watchlist is empty."
        
        selection = random.choice(items)
        return f"How about watching: {selection['title']}?"
        
    except FileNotFoundError:
        return "Error: Could not find the file. Make sure the filename is correct."
    except json.JSONDecodeError:
        return "Error: The file is not valid JSON."

# Run the selection
print(get_random_item('watchlist.json'))
