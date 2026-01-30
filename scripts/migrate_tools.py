import json
import re
import requests
import os

# URLs and Paths
TOOLS_DATA_URL = "https://www.unjail.ai/assets/tools-data-C81uFwHn.js"
CHAINS_FILE = "modelfang/datasets/crescendo_chains/full_attack_chains.json"
GOALS_FILE = "modelfang/datasets/attack_goals.json"

def fetch_tools_data():
    print(f"Fetching tools data from {TOOLS_DATA_URL}...")
    try:
        response = requests.get(TOOLS_DATA_URL)
        response.raise_for_status()
        content = response.text
        
        # Extract JSON array: inside JSON.parse('...')
        match = re.search(r"JSON\.parse\('(.+?)'\)", content)
        if match:
            json_str = match.group(1)
            # Unescape if necessary (the JS string might have escaped quotes)
            # But likely standard JSON.parse input. Let's try direct load.
            # Actually, the content inside might be escaped like \' -> '
            json_str = json_str.replace("\\'", "'") 
            # Wait, if it's JSON, it uses double quotes. The JS wrapper uses single quotes.
            # Let's inspect a snippet: [{'id':"a1"...
            # If the JS uses ' for the wrapper, specific chars might be escaped.
            # Simple replace might be safer.
            # Let's try collecting the raw string and loading.
            data = json.loads(json_str)
            return data
        else:
            print("Could not find JSON.parse pattern.")
            return []
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def transform_to_chains(tools):
    chains = []
    for tool in tools:
        chain_entry = {
            "id": f"crescendo_{tool['id']}",
            "name": tool['name'],
            "category": tool['category'],
            "turns": []
        }
        
        for turn in tool.get('turns', []):
            chain_turn = {
                "turn": turn['number'],
                "purpose": f"Step {turn['number']}",
                "prompt": turn['content'],
                "expected_response": "Continue attack or yield info"
            }
            chain_entry['turns'].append(chain_turn)
            
        chains.append(chain_entry)
    return {"chains": chains}

def transform_to_goals(tools):
    goals = []
    for tool in tools:
        goal_entry = {
            "id": f"crescendo_{tool['id']}",
            "name": tool['name'],
            "category": tool['category'],
            "description": tool['description']
        }
        goals.append(goal_entry)
    return {"goals": goals} # Wrap in object or list? Usually list for goals. 
    # Checking existing attack_goals.json structure...
    # It seems to be a list based on context. I'll make it a list.

def main():
    tools = fetch_tools_data()
    if not tools:
        print("No tools found. Exiting.")
        return

    print(f"Found {len(tools)} tools.")

    # 1. Update Chains
    chain_data = transform_to_chains(tools)
    with open(CHAINS_FILE, 'w', encoding='utf-8') as f:
        json.dump(chain_data, f, indent=2)
    print(f"Updated {CHAINS_FILE} with {len(chain_data['chains'])} chains.")

    # 2. Update Goals
    goal_data = transform_to_goals(tools)
    # Check if goals file expects a list or object. 
    # I'll default to just writing the list if consistent with typical JSONs, 
    # but based on 'chains' wrapping, I'll do a quick check.
    # Actually, let's just write the list of goals directly.
    with open(GOALS_FILE, 'w', encoding='utf-8') as f:
        json.dump(goal_data['goals'], f, indent=2)
    print(f"Updated {GOALS_FILE} with {len(goal_data['goals'])} goals.")
    
    # 3. Create a summary of categories for the user
    categories = set(t['category'] for t in tools)
    print(f"Categories found: {len(categories)}")
    print(sorted(list(categories)))

if __name__ == "__main__":
    main()
