#!/usr/bin/env python3
# encoding: utf-8
"""
dateconverter.py

Created by Christopher Nunu on 2011-02-20.
Copyright (c) 2011 Rice University. All rights reserved.
"""

import sys
import os
from datetime import datetime
from datetime import timedelta
import sqlite3

starttweetID = 907723330
step = 1000
endtweetID = starttweetID + step

searchquery = '''select tweetID, date_created from twitterdata where tweetID >= ? and tweetID < ?'''
updatequery = '''update twitterdata set date_created = ? where tweetID = ?'''

def parseDate(datestring):
	
	timestamp = None
	try:
		timestamp = datetime.strptime(datestring, "%a %b %d %H:%M:%S +0000 %Y")
	except ValueError as e:
		try:
			timestamp = datetime.strptime(datestring, "%a, %d %b %Y %H:%M:%S +0000")
		except ValueError as e:
			pass
	
	return timestamp
	
def updateTimes(dbcon):
	global starttweetID
	global endtweetID
	
	dbcursor = dbcon.cursor()
	dbcursor.execute(searchquery, (starttweetID, endtweetID))
	
	rows = dbcursor.fetchall()
	
	for line in rows: 
		timestamp = parseDate(line[1])
		
		if timestamp == None:
			print("Error: could not convert time for tweetID", line[0])
		else:
			dbcursor.execute(updatequery, (timestamp, line[0]))
			
	dbcon.commit()
	
	print("processed up to", endtweetID - 1)
		
	starttweetID = endtweetID
	endtweetID += step
	
	if starttweetID > 1207540844:
		return True
	else:
		return False;
	
def main():
	sqlitedbpath = sys.argv[1]
	
	hootcon = None
	
	try:
		hootcon = sqlite3.connect(sqlitedbpath)
	except sqlite3.Error as e:
		print("Could not find sqlite database on path", sqiltedbpath)
		sys.exit(1)
		
	done = updateTimes(hootcon)
		
	while not done:
		done = updateTimes(hootcon)


if __name__ == '__main__':
	main()

