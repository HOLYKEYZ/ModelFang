"""
FULL extraction of ALL prompts from Unjail.ai JS files.
Parses the JavaScript object structure to get every single fragment prompt.
"""
import re
import json

def extract_all_from_js(js_file_path):
    """Extract ALL entries from the JS data files."""
    with open(js_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The content starts with "const e=" and ends with ";export{e as ...}"
    # Extract just the JSON array part
    match = re.search(r'const e=(\[.*?\]);\s*export', content, re.DOTALL)
    if not match:
        print(f"Could not find data array in {js_file_path}")
        return []
    
    json_str = match.group(1)
    
    # The JS uses unquoted keys and single quotes - convert to valid JSON
    # Replace {key: to {"key":
    json_str = re.sub(r'(\{|,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
    
    # Replace single quotes with double quotes (careful with escaped ones)
    # This is tricky because some strings contain apostrophes
    # Let's use a different approach - just extract using regex
    
    all_prompts = []
    
    # Extract all id, name, description, prompt pairs using regex
    # Pattern for main categories
    category_pattern = r'"id":"([^"]+)","name":"([^"]+)","icon":"([^"]+)","description":"([^"]+)"'
    categories = re.findall(category_pattern, content)
    
    # Pattern for fragments within categories
    # Look for: {id:"...", title:"...", ... prompt:"..."}
    fragment_pattern = r'"id":"([^"]+)","title":"([^"]+)"(?:,"subtitle":"([^"]*)")?(?:,"realPurpose":"([^"]*)")?,"prompt":"((?:[^"\\]|\\.)*)"'
    
    # Also try without quotes on keys
    fragment_pattern2 = r'id:"([^"]+)",title:"([^"]+)"(?:,subtitle:"([^"]*)")?(?:,realPurpose:"([^"]*)")?(?:,prompt:\'([^\']*(?:\\.[^\']*)*)\'|,prompt:"([^"]*(?:\\.[^"]*)*)")'
    
    fragments = re.findall(fragment_pattern2, content)
    
    print(f"Found {len(categories)} categories")
    print(f"Found {len(fragments)} fragments with pattern2")
    
    # Let's try a simpler approach - count actual prompt occurrences
    prompt_count = content.count('prompt:')
    print(f"Total 'prompt:' occurrences: {prompt_count}")
    
    # Extract each prompt field by finding the pattern and reading until the end
    # Pattern: prompt:"..." or prompt:'...'
    prompts = []
    idx = 0
    while True:
        # Find next prompt field
        match = re.search(r'prompt:["\']', content[idx:])
        if not match:
            break
        
        start = idx + match.end()
        quote_char = content[idx + match.end() - 1]
        
        # Find the closing quote (handling escapes)
        end = start
        while end < len(content):
            if content[end] == quote_char and content[end-1] != '\\':
                break
            end += 1
        
        if end < len(content):
            prompt_text = content[start:end]
            # Unescape the string
            prompt_text = prompt_text.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace("\\'", "'")
            prompts.append(prompt_text[:200])  # First 200 chars for preview
        
        idx = end + 1
    
    print(f"Extracted {len(prompts)} prompts")
    
    return categories, prompts

def full_extraction():
    """Do complete extraction with proper JSON parsing."""
    
    all_jailbreaks = []
    
    # Read component-fragmentation-data
    with open("component-fragmentation-data-BeoevF7J.js", 'r', encoding='utf-8') as f:
        cf_content = f.read()
    
    # Read manipulation-matrix-data  
    with open("manipulation-matrix-data-ggLgmtlx.js", 'r', encoding='utf-8') as f:
        mm_content = f.read()
    
    # Extract using a state machine approach to properly parse the nested structure
    def parse_js_array(content, source_name):
        entries = []
        
        # Find all main category blocks
        # Pattern: {id:"...",name:"...",icon:"...",description:"...",fragments:[...]}
        cat_starts = [m.start() for m in re.finditer(r'\{id:"[^"]+",name:"[^"]+"', content)]
        
        for i, cat_start in enumerate(cat_starts):
            # Find this category's data
            cat_end = cat_starts[i+1] if i+1 < len(cat_starts) else len(content)
            cat_block = content[cat_start:cat_end]
            
            # Extract category info
            cat_match = re.match(r'\{id:"([^"]+)",name:"([^"]+)",icon:"([^"]+)",description:"([^"]+)"', cat_block)
            if not cat_match:
                continue
            
            cat_id, cat_name, cat_icon, cat_desc = cat_match.groups()
            
            # Find all fragments in this category
            # Pattern: {id:"...",title:"...",prompt:"..."}
            frag_pattern = r'\{id:"([^"]+)",title:"([^"]+)"'
            frag_matches = list(re.finditer(frag_pattern, cat_block))
            
            for j, frag_match in enumerate(frag_matches):
                frag_start = frag_match.start()
                frag_end = frag_matches[j+1].start() if j+1 < len(frag_matches) else len(cat_block)
                frag_block = cat_block[frag_start:frag_end]
                
                frag_id = frag_match.group(1)
                frag_title = frag_match.group(2)
                
                # Extract subtitle if present
                subtitle_match = re.search(r'subtitle:"([^"]*)"', frag_block)
                subtitle = subtitle_match.group(1) if subtitle_match else ""
                
                # Extract realPurpose if present (manipulation matrix has this)
                purpose_match = re.search(r'realPurpose:"([^"]*)"', frag_block)
                real_purpose = purpose_match.group(1) if purpose_match else ""
                
                # Extract the prompt
                prompt_match = re.search(r'prompt:["\'](.+?)["\'](?:,|\})', frag_block, re.DOTALL)
                if not prompt_match:
                    # Try to find prompt that spans multiple lines
                    prompt_start = frag_block.find('prompt:"')
                    if prompt_start == -1:
                        prompt_start = frag_block.find("prompt:'")
                    if prompt_start != -1:
                        prompt_start += 8
                        quote_char = frag_block[prompt_start - 1]
                        # Find closing quote
                        prompt_end = prompt_start
                        while prompt_end < len(frag_block):
                            if frag_block[prompt_end] == quote_char:
                                # Check if escaped
                                if prompt_end > 0 and frag_block[prompt_end-1] != '\\':
                                    break
                            prompt_end += 1
                        prompt_text = frag_block[prompt_start:prompt_end]
                    else:
                        prompt_text = ""
                else:
                    prompt_text = prompt_match.group(1)
                
                # Clean up the prompt
                prompt_text = prompt_text.replace('\\n', '\n').replace('\\t', '\t')
                prompt_text = prompt_text.replace('\\"', '"').replace("\\'", "'")
                
                entry = {
                    "id": f"{source_name}_{cat_id}_{frag_id}",
                    "category_id": cat_id,
                    "category_name": cat_name,
                    "category_desc": cat_desc,
                    "fragment_id": frag_id,
                    "title": frag_title,
                    "subtitle": subtitle,
                    "real_purpose": real_purpose,
                    "source": source_name,
                    "prompt": prompt_text[:3000]  # Truncate very long prompts
                }
                entries.append(entry)
        
        return entries
    
    print("=== Parsing Component Fragmentation Data ===")
    cf_entries = parse_js_array(cf_content, "unjail_cf")
    print(f"Extracted {len(cf_entries)} entries")
    
    print("\n=== Parsing Manipulation Matrix Data ===")
    mm_entries = parse_js_array(mm_content, "unjail_mm")
    print(f"Extracted {len(mm_entries)} entries")
    
    all_jailbreaks = cf_entries + mm_entries
    
    print(f"\n=== TOTAL: {len(all_jailbreaks)} jailbreak prompts ===")
    
    # Show breakdown by category
    categories = {}
    for entry in all_jailbreaks:
        cat = entry["category_name"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nBreakdown by category:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")
    
    # Save to JSON
    output_path = "modelfang/datasets/jailbreaks.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_jailbreaks, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {output_path}")
    
    return all_jailbreaks

if __name__ == "__main__":
    # First, show what we're working with
    print("=== Analyzing JS files ===")
    cats1, prompts1 = extract_all_from_js("component-fragmentation-data-BeoevF7J.js")
    print()
    cats2, prompts2 = extract_all_from_js("manipulation-matrix-data-ggLgmtlx.js")
    
    print("\n" + "="*50)
    print("=== FULL EXTRACTION ===")
    print("="*50 + "\n")
    
    all_data = full_extraction()
