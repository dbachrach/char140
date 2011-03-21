#!/usr/bin/env python3
# encoding: utf-8
"""
tag_hasher.py

Created by Dustin Bachrach on 2011-02-21.
Copyright (c) 2011 Rice University. All rights reserved.
"""

import sys
import os
import sqlite3
import hashlib
import base64

tagquery = '''UPDATE tags SET long_tag=(?) WHERE tweetID=(?) AND tag=(?)'''
#selectquery = '''SELECT * FROM tags WHERE long_tag IS NULL'''
selectquery = '''SELECT * FROM tags'''

def updateTagsDB(dbcon):
	dbcursor = dbcon.cursor()


	dbcursor.execute(selectquery)
	rows = dbcursor.fetchall()
	print(len(rows))
	for row in rows:
		tweetID = row[0]
		tag_with_hash = row[1]
		tag = tag_with_hash[1:]
		long_tag = base64.b64encode(hashlib.sha1(tag.encode('utf-8')).digest()) # TODO: Hash tag
		# print(tweetID, tag, long_tag)
		try:
			dbcursor.execute(tagquery, (long_tag, tweetID, tag_with_hash))
			print("Updated", tweetID, "tag:", tag, "long_tag:", long_tag)
		except sqlite3.Error as e:
			print("Error: Database error occurred:", e.args[0], "\nRolling back.")
			dbcon.rollback()
	
	dbcon.commit()
	
def main():
	sqlitedbpath = sys.argv[1]
	hootcon = None
	
	try:
		hootcon = sqlite3.connect(sqlitedbpath)
	except sqlite3.Error as e:
		print("Could not find sqlite database on path", sqiltedbpath)
		sys.exit(1)
	
	updateTagsDB(hootcon)
		

if __name__ == '__main__':
	main()

