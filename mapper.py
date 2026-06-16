#!/usr/bin/env python3
import sys
import json
import re

stopwords = set()
try:
	with open('stopwords.txt', 'r', encoding='utf-8') as f:
		for line in f:
			stopwords.add(line.strip().lower())
except:
	pass
for line in sys.stdin:
	line = line.strip()
	if not line:
		continue

	try:
		data = json.loads(line)
		content = data.get('content', '')
		if not content or not isinstance(content, str):
			continue
		url = data.get('url', '')

		source_type = "VN" if (".vn" in url or "dantri" in url or "vnexpress" in url) else "Global"

			
		content = re.sub('[^\\w\\s]', ' ', content).lower()
		words = content.split()
			
		filtered_words = [w for w in words if w not in stopwords and len(w) > 1]
	
		for i in range(len(filtered_words) - 1):
			print(f"{source_type}\t{filtered_words[i]},{filtered_words[i+1]}\t1")
	except:
		continue
