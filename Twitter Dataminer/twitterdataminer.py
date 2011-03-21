#!/usr/bin/env python3
# encoding: utf-8
"""
twitterdataminer.py

Created by Christopher Nunu on 2011-02-19.
Copyright (c) 2011 Rice University. All rights reserved.
"""

import sys
import os
import sqlite3
import json
import re
import xml.dom.minidom as xmlminidom
import xml

tweetquery = '''insert or ignore into twitterdata(tweetID, text, toID, fromID, date_created) values (?,?,?,?,?)'''
userquery = '''insert or ignore into users(userID, username) values (?,?)'''
tagquery = '''insert or replace into tags(tweetID, tag) values (?,?)'''

jsonWrapper = 'results'
xmlWrapper = 'status'

tagpattern = '''#\w+'''
compiledtagpattern = re.compile(tagpattern)

def updateUserDB(userid, username, dbcon):
	dbcursor = dbcon.cursor()
	dbcursor.execute(userquery, (userid, username))
	
def updateTagsDB(tweetid, text, dbcon):
	dbcursor = dbcon.cursor()
	tags = re.findall(compiledtagpattern, text)
	
	for tag in tags:
		dbcursor.execute(tagquery, (tweetid, tag))
		
	
def updateTweetDB(tweetID, text, toID, fromID, username, created, dbcon):
	dbcursor = dbcon.cursor()
	try:
		dbcursor.execute(tweetquery, (tweetID, text, toID, fromID, created))
		updateUserDB(fromID, username, dbcon)
		updateTagsDB(tweetID, text, dbcon)
	except sqlite3.Error as e:
		print("Error: Database error occurred:", e.args[0], "\nRolling back.")
		dbcon.rollback()
	
	dbcon.commit()
	
	
def parseJSON(jsonfile, dbcon):
	
	try:
		jsonobj = json.load(jsonfile)
	except Exception as e:
		print("Error: Could not open file", jsonfile, "due to", e)
		return
	
	for tweet in jsonobj[jsonWrapper]:
		tweetID = tweet['id']
		text = tweet['text']
		toID = tweet['to_user_id']
		fromID = tweet['from_user_id']
		username = tweet['from_user']
		created = tweet['created_at']
		
		updateTweetDB(tweetID, text, toID, fromID, username, created, dbcon)
		
	
def getText(nodelist):
	rc = []
	
	for node in nodelist:
		if node.nodeType == node.TEXT_NODE:
			rc.append(node.data)
			
	return ' '.join(rc)
	
	
def parseXML(xmlfile, dbcon):
	
	try:
		xmlobj = xmlminidom.parse(xmlfile)
	except Exception as e:
		print("Error: Could not open file", xmlfile, "due to", e)
		return
	
	for tweet in xmlobj.getElementsByTagName(xmlWrapper):
		tweetID = getText(tweet.getElementsByTagName('id')[0].childNodes)
		text = getText(tweet.getElementsByTagName('text')[0].childNodes)
		toID = getText(tweet.getElementsByTagName('in_reply_to_user_id')[0].childNodes)
		created = getText(tweet.getElementsByTagName('created_at')[0].childNodes)
		
		user = tweet.getElementsByTagName('user')[0]
		fromID = getText(user.getElementsByTagName('id')[0].childNodes)
		username = getText(user.getElementsByTagName('screen_name')[0].childNodes)
		
		updateTweetDB(tweetID, text, toID, fromID, username, created, dbcon)


def main():
	tweetfolder = sys.argv[1]
	sqlitedbpath = sys.argv[2]
	
	hootcon = None
	
	try:
		hootcon = sqlite3.connect(sqlitedbpath)
	except sqlite3.Error as e:
		print("Could not find sqlite database on path", sqiltedbpath)
		sys.exit(1)
		
	if not os.path.exists(tweetfolder):
		print("Tweeter data directory not found", tweetfolder)
		sys.exit(1)
		
	twitterdatafiles = [os.path.join(tweetfolder, tweetfile) for tweetfile in os.listdir(tweetfolder)]
	count = 0
	for datafile in twitterdatafiles:
		
		print("[Processing file:", datafile)
		count += 1
		
		fh = open(datafile, "r")
		
		if datafile.endswith(".xml"):
			parseXML(fh, hootcon)
		elif datafile.endswith(".json"):
			parseJSON(fh, hootcon)
			
		fh.close()
		
		print("]\n")
		
	print("Total files processed", count)
		

if __name__ == '__main__':
	main()

