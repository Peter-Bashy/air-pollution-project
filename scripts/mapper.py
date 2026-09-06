# ================================================
# Mapper: Air Pollution MapReduce
# Job: Count number of records per city
# Input: cleaned data from HDFS
# ================================================

import sys

for line in sys.stdin:
    # Remove whitespace
    line = line.strip()
    
    # Split by comma
    fields = line.split(',')
    
    # Check if line has enough fields
    if len(fields) < 18:
        continue
    
    # Extract City (first column)
    city = fields[0]
    
    # Skip if city is empty
    if not city:
        continue
    
    # Emit key-value pair: (City, 1)
    print(f"{city}\t1")