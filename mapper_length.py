#!/usr/bin/env python3
import sys
import json

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
		
		words = content.split()
		word_count = len(words) 

		if word_count < 300:
			length_group = "Short"
		elif 300 <= word_count <= 1000:
			length_group = "Medium"
		else:
			length_group = "Long"

		print(f"{source_type}\t{length_group}\t1")
	except:
		continue
