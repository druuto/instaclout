import json
import sqlite3 
from sqlite3 import Error
from datetime import datetime
import glob
import pandas as pd
import itertools

conn = sqlite3.connect('data.db')
c = conn.cursor()

c.execute('DROP TABLE IF EXISTS "posts";')
c.execute('DROP TABLE IF EXISTS "hashtags";')
c.execute('CREATE TABLE posts(id bigint PRIMARY KEY not null, location_id text, location_slug text, num_pics int, accessibility_caption text, caption text, likes real, comment_count real, hashtags_string text, timestring timestamp)');
c.execute('CREATE TABLE hashtags(tag_id INTEGER PRIMARY KEY AUTOINCREMENT, tag text , post_id bigint, location_slug text)')

json_files = glob.glob('./*.json')
json_xz_files = glob.glob('./*.json.xz')

for filename in itertools.chain(json_files, json_xz_files):
	print(filename)
	if("comments" in filename):
		continue
	df = pd.read_json(filename)
	info = df["node"]
	num_pics = 1
	if("edge_sidecar_to_children" in info):
		num_pics = len(info["edge_sidecar_to_children"]["edges"])
	accessibility_caption = None
	if("accessibility_caption" in info):
		accessibility_caption = info["accessibility_caption"]
	likes = info["edge_media_preview_like"]["count"]
	caption = None
	if(len(info["edge_media_to_caption"]["edges"])>0):
		caption = info["edge_media_to_caption"]["edges"][0]["node"]["text"]
	comment_count = info["edge_media_to_comment"]["count"]
	location_id = None
	location_slug = None
	if(info["location"]):
		location_id = info["location"]["id"]
		location_slug = info["location"]["slug"]
	hashtags_string = None
	hashtags_list = []
	if(caption):
		hashtags_list = set([word[1:] for word in caption.split() if word[0] == '#'])
		hashtags_string =  ",".join(hashtags_list)

	time = int(info["taken_at_timestamp"])
	timestring = datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
	post_id = info["id"]

	c.execute('INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (post_id, location_id, location_slug, num_pics, accessibility_caption, caption, likes, comment_count, hashtags_string, timestring))
	
	print(hashtags_list)
	if (hashtags_string != None):
		for tag in hashtags_list:
			print(tag, post_id, location_slug)
			c.execute('INSERT INTO hashtags VALUES (Null, ?, ?, ?)', ( tag, post_id, location_slug))

conn.commit()
