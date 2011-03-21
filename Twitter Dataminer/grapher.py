#!/usr/bin/env python3
# encoding: utf-8
"""
grapher.py

Queries the Database for a list of all tags and the occurences of that tag. 
These can then be put into Grapher to graph.

Created by Dustin Bachrach on 2011-02-21.
Copyright (c) 2011 Rice University. All rights reserved.
"""

import sys
import os
import sqlite3
import hashlib
import base64

selectquery = '''SELECT COUNT(*) AS num, tag
FROM tags
GROUP BY tag
ORDER BY num DESC'''
	
def graph(dbcon):
	dbcursor = dbcon.cursor()

	dbcursor.execute(selectquery)
	rows = dbcursor.fetchall()
	print(len(rows))
	i = 1
	for row in rows:
		count = row[0]
		tag = row[1]
		print(i, count)
		i+=1
	
def main():
	sqlitedbpath = sys.argv[1]
	hootcon = None
	
	try:
		hootcon = sqlite3.connect(sqlitedbpath)
	except sqlite3.Error as e:
		print("Could not find sqlite database on path", sqiltedbpath)
		sys.exit(1)
	
	graph(hootcon)
		

if __name__ == '__main__':
	main()

