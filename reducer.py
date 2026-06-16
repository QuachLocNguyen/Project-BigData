#!/usr/bin/env python3
import sys

current_key = None
current_count = 0

for line in sys.stdin:
	line = line.strip()
	if not line:
		continue

	parts = line.split('\t')
	if len(parts) != 3:
		continue

	source, bigram, count = parts[0], parts[1], parts[2]
	key = f"{source}\t{bigram}"

	try:
		count = int(count)
	except ValueError:
		continue
	
	if current_key == key:
		current_count += count
	else:
		if current_key:
			print(f"{current_key}\t{current_count}")
		current_key = key
		current_count = count

if current_key:
	print(f"{current_key}\t{current_count}")
