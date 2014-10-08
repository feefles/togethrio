from togethr import app, mongo
from flask import render_template, redirect, url_for, request, session, jsonify
import time, re
from bson.json_util import dumps
from bson import ObjectId


@app.route("/getContacts/", methods = ['POST'])
def getContacts():
	user = session['username']
	self = mongo.users.find({'name': user})
	friends = self[0]['friends']

	friendInfo = {}
	if friends:
		friendCursor = mongo.users.find({'_id': { '$in' : friends } }).sort("timestamp", -1)
	 	for friend in friendCursor:
			if friend['name'].lower() == user.lower():
				continue
	 		friendInfo[friend['name']] = userIsOnline(friend['timestamp'])
	return jsonify(result = friendInfo)

@app.route("/findContacts/", methods = ['POST'])
def findContacts():
	user = session['username']
	friend = request.form['input'].lower()

	f = mongo.users.find({'name_lower': {"$regex": re.compile(friend, re.IGNORECASE)}})
	flist = ""
	for contact in f:
		if contact['name'].lower() == user.lower():
			continue
		flist = flist + contact['name'] + ","
	flist = flist[:-1]

	return flist


@app.route("/addContact/", methods = ['POST'])
def addContact():
	user = session['username']
	self = mongo.users.find_one({'name':user})
	newContact = request.form['contact'].lower()
	f = mongo.users.find_one({'name_lower': newContact})
	if not(f == None):
		current_friends = mongo.users.find_one({'name': user})
		if current_friends != None:
			current_friends = current_friends['friends']
		else:
			current_friends = []
		if f['_id'] not in current_friends and f['_id'] != self['_id']:
			# Add the contact to the current user's list of contacts
			mongo.users.update({'name': user}, { '$push': {'friends': f['_id']} })
			# Add the current user to the new contact's list of contacts
			mongo.users.update({'_id': f['_id']}, { '$push': {'friends': self['_id']} })
			# Return info
			friendInfo = {}
			friendInfo[f['name']] = userIsOnline(f['timestamp'])
			return jsonify(success = friendInfo)
		else:
			return "duplicate"
	else:
		return "notfound"


#remove_friend()

@app.route("/updateTimestamp/", methods = ['POST'])
def updateTimestamp():
	mongo.users.update({'name_lower': session['username'].lower()}, { '$set': { 'timestamp': time.time() } })
	return "done"

# A method for detecting if a user's status should be considered "online"
def userIsOnline(timestamp):
	interval = 5  # In seconds
	if time.time() > timestamp + interval:
		return False
	else:
		return True
