import json
import sqlite3
from sqlite3 import Error
from datetime import datetime
import glob
import pandas as pd
import itertools
import csv

conn = sqlite3.connect('data.db')
c = conn.cursor()

c.execute('SELECT location_id, location_slug, num_pics, likes, comment_count, timestring FROM posts;')

result = c.fetchall()

# slug to id
location_ids = {}
curr_id = 0

# stores row in csv
rows = []
for x in result:
	row = []

	if (x[1] == '' or x[1] == None):
		continue

	# get location id
	if (x[1] in location_ids):
		row.append(location_ids[x[1]])
	else:
		row.append(curr_id)
		curr_id += 1

	# get location id (as text)
	row.append(x[0])

	# get location name
	row.append(x[1])

	# num_pics
	row.append(x[2])

	# num likes (as real)
	row.append(x[3])

	# num comments (as real)
	row.append(x[4])

	# timestring (as timestamp)
	row.append(x[5])

	rows.append(row)

# write rows to csv file
with open('regression.csv', 'w') as writeFile:
    writer = csv.writer(writeFile)
    writer.writerow(['location_index', 'location_id', 'location_name', 'num_pics', 'likes', 'comment_count', 'timestring'])
    writer.writerows(rows)
    writeFile.close()
