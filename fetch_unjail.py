import requests
from bs4 import BeautifulSoup

def fetch_assets():
    base_url = "https://www.unjail.ai"
    assets = [
        "/assets/component-fragmentation-data-BeoevF7J.js",
        "/assets/manipulation-matrix-data-ggLgmtlx.js"
    ]
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for asset in assets:
        url = base_url + asset
        filename = asset.split("/")[-1]
        try:
            print(f"Fetching {url}...")
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(response.text)
                print(f"Saved {filename}")
        except Exception as e:
            print(f"Error fetching {asset}: {e}")

if __name__ == "__main__":
    fetch_assets()
