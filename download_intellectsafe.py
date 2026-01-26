"""
Download ALL files from IntellectSafe GitHub and Unjail.ai data pages
"""
import requests
import json
import os
import time

def download_intellect_safe():
    """Download all files from IntellectSafe rag_fallback directory."""
    
    # 14 JSON files from data/rag_fallback
    rag_files = [
        "084069156303169f77da6ea978d06247.json",
        "1591ed702eacb5b7254b6846fb5137aa.json",
        "1a5d2cbbaf2e6c7418d02679076d29b6.json",
        "27e56101ed6166a123e8e6342ea845ae.json",
        "3ce93a91404586e4861e8b25bd16215f.json",
        "3fa143fe0722e6eaef933d8873fdfe50.json",
        "4da5646d0f3529ce23d320f1b43c15ec.json",
        "57291e64b05a4dc5b944dd8992660bf7.json",
        "74c6a2580d90cab995c775c0ed8a714a.json",
        "bacecf8fa74dc141600346f4b69146e7.json",
        "d9912e867fe0c3101e60128039968a2c.json",
        "ed6576cc2042195b0d8dff13076bbd8c.json",
        "f8cd5f0b37fd8f06dcf961cf6cc87694.json",
        "ff1a5e39d229f21770e6a51f5adf6435.json",
    ]
    
    # 7 MD files from docs
    doc_files = [
        "API.md",
        "ARCHITECTURE.md",
        "INTEGRATION.md",
        "LLM_COUNCIL.md",
        "RESEARCH.md",
        "RESEARCH_ENHANCEMENTS.md",
        "research-findings.md",
    ]
    
    base_raw_url = "https://raw.githubusercontent.com/HOLYKEYZ/IntellectSafe/master"
    
    # Create download directory
    os.makedirs("intellect_safe_data", exist_ok=True)
    os.makedirs("intellect_safe_data/rag_fallback", exist_ok=True)
    os.makedirs("intellect_safe_data/docs", exist_ok=True)
    
    all_data = []
    
    # Download rag_fallback files
    print("=== Downloading RAG Fallback files ===")
    for filename in rag_files:
        url = f"{base_raw_url}/data/rag_fallback/{filename}"
        print(f"  Downloading {filename}...", end=" ")
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                # Save raw file
                with open(f"intellect_safe_data/rag_fallback/{filename}", 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                # Parse JSON and collect data
                try:
                    data = json.loads(response.text)
                    all_data.append({
                        "source": "intellectsafe_rag",
                        "filename": filename,
                        "data": data
                    })
                    print(f"OK ({len(response.text)} bytes)")
                except json.JSONDecodeError:
                    print(f"OK (not valid JSON)")
            else:
                print(f"FAILED ({response.status_code})")
        except Exception as e:
            print(f"ERROR: {e}")
        time.sleep(0.3)  # Be nice to GitHub
    
    # Download docs files
    print("\n=== Downloading Docs files ===")
    for filename in doc_files:
        url = f"{base_raw_url}/docs/{filename}"
        print(f"  Downloading {filename}...", end=" ")
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                with open(f"intellect_safe_data/docs/{filename}", 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"OK ({len(response.text)} bytes)")
            else:
                print(f"FAILED ({response.status_code})")
        except Exception as e:
            print(f"ERROR: {e}")
        time.sleep(0.3)
    
    print(f"\n=== Downloaded {len(all_data)} RAG fallback files ===")
    
    return all_data

def extract_jailbreaks_from_intellect_safe(all_data):
    """Extract jailbreak-style prompts from IntellectSafe data."""
    jailbreaks = []
    
    for item in all_data:
        data = item["data"]
        filename = item["filename"]
        
        # Each file might have different structure - inspect and extract
        if isinstance(data, dict):
            # Common fields: prompt, input, query, text
            for key in ["prompt", "input", "query", "text", "content"]:
                if key in data and isinstance(data[key], str):
                    jailbreaks.append({
                        "id": f"is_{filename.replace('.json', '')}",
                        "source": "intellectsafe",
                        "category": "rag_fallback",
                        "filename": filename,
                        "prompt": data[key][:2000],
                        "metadata": {k: v for k, v in data.items() if k != key and isinstance(v, (str, int, float, bool))}
                    })
                    break
            
            # Also check for nested structures
            for key, val in data.items():
                if isinstance(val, list):
                    for i, item_val in enumerate(val):
                        if isinstance(item_val, str) and len(item_val) > 50:
                            jailbreaks.append({
                                "id": f"is_{filename.replace('.json', '')}_{i}",
                                "source": "intellectsafe",
                                "category": "rag_fallback",
                                "prompt": item_val[:2000]
                            })
        
        elif isinstance(data, list):
            for i, item_val in enumerate(data):
                if isinstance(item_val, dict):
                    for key in ["prompt", "input", "query", "text", "content"]:
                        if key in item_val:
                            jailbreaks.append({
                                "id": f"is_{filename.replace('.json', '')}_{i}",
                                "source": "intellectsafe",
                                "category": "rag_fallback",
                                "prompt": str(item_val[key])[:2000]
                            })
                            break
                elif isinstance(item_val, str) and len(item_val) > 50:
                    jailbreaks.append({
                        "id": f"is_{filename.replace('.json', '')}_{i}",
                        "source": "intellectsafe",
                        "category": "rag_fallback", 
                        "prompt": item_val[:2000]
                    })
    
    return jailbreaks

def main():
    print("="*60)
    print("IntellectSafe Data Downloader")
    print("="*60 + "\n")
    
    # Download all files
    all_data = download_intellect_safe()
    
    # Extract jailbreaks
    print("\n=== Extracting jailbreak prompts ===")
    jailbreaks = extract_jailbreaks_from_intellect_safe(all_data)
    print(f"Extracted {len(jailbreaks)} entries")
    
    # Show sample
    if jailbreaks:
        print("\nSample entry:")
        sample = jailbreaks[0]
        print(f"  ID: {sample['id']}")
        print(f"  Prompt: {sample['prompt'][:100]}...")
    
    # Save extracted data
    with open("intellectsafe_jailbreaks.json", 'w', encoding='utf-8') as f:
        json.dump(jailbreaks, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to intellectsafe_jailbreaks.json")
    
    return jailbreaks

if __name__ == "__main__":
    main()
