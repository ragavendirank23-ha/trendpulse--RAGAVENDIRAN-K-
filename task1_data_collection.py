import requests
import json
import time
import os
from datetime import datetime

# 1. Setup Categories and Keywords
CATEGORIES = {
    "technology": ["AI", "software", "tech", "code", "computer", "data", "cloud", "API", "GPU", "LLM"],
    "worldnews": ["war", "government", "country", "president", "election", "climate", "attack", "global"],
    "sports": ["NFL", "NBA", "FIFA", "sport", "game", "team", "player", "league", "championship"],
    "science": ["research", "study", "space", "physics", "biology", "discovery", "NASA", "genome"],
    "entertainment": ["movie", "film", "music", "Netflix", "game", "book", "show", "award", "streaming"]
}

headers = {"User-Agent": "TrendPulse/1.0"}
collected_stories = []
counts = {cat: 0 for cat in CATEGORIES}

# Create data folder if it doesn't exist
os.makedirs('data', exist_ok=True)

# 2. Fetch Top 1000 IDs (to ensure we find enough matches)
print("Fetching IDs from HackerNews...")
response = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", headers=headers)
top_ids = response.json()[:1000] 

# 3. Fetch Details & Categorize
for story_id in top_ids:
    # Stop if we hit 25 in every category (125 stories total)
    if all(c >= 25 for c in counts.values()): 
        break
    
    try:
        # Fetch individual story details
        item_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        item = requests.get(item_url, headers=headers).json()
        
        if not item or 'title' not in item: 
            continue
        
        title = item['title']
        title_lower = title.lower()

        # Check title against keywords for each category
        for cat, keywords in CATEGORIES.items():
            if counts[cat] < 25 and any(word.lower() in title_lower for word in keywords):
                # Save the 7 required fields
                collected_stories.append({
                    "post_id": item['id'],
                    "title": title,
                    "category": cat,
                    "score": item.get('score', 0),
                    "num_comments": item.get('descendants', 0),
                    "author": item.get('by'),
                    "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                counts[cat] += 1
                print(f"[{cat}] Found: {title[:50]}...")
                
                # Rule: Wait 2 seconds after finding a category match
                time.sleep(2) 
                break
    except Exception as e:
        print(f"Skipping story {story_id} due to error.")
        continue

# 4. Save to JSON File
date_str = datetime.now().strftime('%Y%m%d')
filename = f"data/trends_{date_str}.json"

with open(filename, 'w') as f:
    json.dump(collected_stories, f, indent=4)

print("-" * 30)
print(f"✅ Success! Collected {len(collected_stories)} stories.")
print(f"📂 Saved to {filename}")