# ================================================
# Reducer: Air Pollution MapReduce
# Job: Sum up counts per city
# Input: sorted key-value pairs from mapper
# ================================================

import sys

current_city = None
current_count = 0

for line in sys.stdin:
    # Remove whitespace
    line = line.strip()
    
    # Split into city and count
    fields = line.split('\t')
    
    if len(fields) != 2:
        continue
    
    city = fields[0]
    
    try:
        count = int(fields[1])
    except ValueError:
        continue
    
    # If same city as before add to count
    if current_city == city:
        current_count += count
    else:
        # New city — print previous city result
        if current_city:
            print(f"{current_city}\t{current_count}")
        # Reset for new city
        current_city = city
        current_count = count

# Print last city
if current_city:
    print(f"{current_city}\t{current_count}")