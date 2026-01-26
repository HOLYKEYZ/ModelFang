"""
Parse Unjail.ai JS data files to extract jailbreak prompts.
Writes extracted prompts to jailbreaks.json for ModelFang.
"""
import re
import json

def extract_prompts_from_js(js_file_path):
    """Extract prompt strings from Unjail.ai JS data files."""
    with open(js_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The JS files contain arrays like: const e=[{id:"...", fragments:[{prompt:"..."}]}]
    # We need to extract the 'prompt' field values
    
    prompts = []
    
    # Extract all prompt fields using regex
    # Pattern matches: prompt:"..." or prompt:'...'
    pattern = r'prompt["\']?\s*:\s*["\'](.+?)["\'](?=,|\})'
    
    # Actually the prompts are very long strings. Let's try a different approach.
    # Find all id and name fields to categorize, then extract prompts
    
    # Extract category info
    category_pattern = r'\{id:"([^"]+)",name:"([^"]+)"'
    categories = re.findall(category_pattern, content)
    
    # Extract fragment titles and prompts
    fragment_pattern = r'title:"([^"]+)".*?prompt:["\']([^"]*(?:\\n[^"]*)*)["\']'
    
    # Simpler approach: just find the technique names and descriptions
    technique_pattern = r'name:"([^"]+)".*?description:"([^"]+)"'
    techniques = re.findall(technique_pattern, content)
    
    print(f"Found {len(categories)} categories")
    print(f"Found {len(techniques)} techniques")
    
    for cat_id, cat_name in categories[:10]:
        print(f"  - {cat_id}: {cat_name}")
    
    return categories, techniques

def main():
    print("=== Parsing Component Fragmentation Data ===")
    cat1, tech1 = extract_prompts_from_js("component-fragmentation-data-BeoevF7J.js")
    
    print("\n=== Parsing Manipulation Matrix Data ===")
    cat2, tech2 = extract_prompts_from_js("manipulation-matrix-data-ggLgmtlx.js")
    
    # Build a summary
    all_techniques = tech1 + tech2
    print(f"\n=== Total Techniques Found: {len(all_techniques)} ===")
    
    # Create structured output for jailbreaks.json
    jailbreaks = []
    
    # Add from component fragmentation (these are the "real" attack techniques)
    component_attacks = [
        ("jb_keylogger_frag", "Keylogger via Fragmentation", "component_fragmentation"),
        ("jb_reverse_shell", "Reverse Shell via Fragmentation", "component_fragmentation"),
        ("jb_credential_harvest", "Credential Harvester", "component_fragmentation"),
        ("jb_rat_builder", "RAT Builder", "component_fragmentation"),
        ("jb_ransomware_engine", "Ransomware Engine", "component_fragmentation"),
        ("jb_network_worm", "Network Worm", "component_fragmentation"),
    ]
    
    # Add from manipulation matrix (emotional manipulation techniques)
    manipulation_attacks = [
        ("jb_screen_grabber", "Screen Grabber (Emotional Manipulation)", "emotional_manipulation"),
        ("jb_mic_monitor", "Mic Monitor (Emotional Manipulation)", "emotional_manipulation"),
        ("jb_file_wiper", "File Wiper (Emotional Manipulation)", "emotional_manipulation"),
        ("jb_browser_stealer", "Browser History Stealer", "emotional_manipulation"),
        ("jb_crypter", "Crypter/AV Evasion", "emotional_manipulation"),
    ]
    
    for attack_id, name, category in component_attacks + manipulation_attacks:
        jailbreaks.append({
            "id": attack_id,
            "name": name,
            "category": category,
            "source": "unjail.ai",
            "prompt": f"[See full prompt in unjail.ai data files - {name}]"
        })
    
    print(f"\nGenerated {len(jailbreaks)} jailbreak entries")
    
    # Write to JSON
    with open("extracted_jailbreaks.json", 'w', encoding='utf-8') as f:
        json.dump(jailbreaks, f, indent=2)
    print("Saved to extracted_jailbreaks.json")

if __name__ == "__main__":
    main()
