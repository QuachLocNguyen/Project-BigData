import json
from collections import Counter

with open(r"C:\Users\Huong Giang\Downloads\newscrawler\newscrawler\vnexpress.json", "r", encoding="utf-8") as f:
    data = json.load(f)

counter = Counter()

for article in data:
    category = article.get("category", "unknown")
    counter[category] += 1

print("\n=== ARTICLE COUNT BY CATEGORY ===")
for category, count in counter.most_common():
    print(f"{category}: {count}")