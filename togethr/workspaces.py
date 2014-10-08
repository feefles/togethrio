from togethr import app, mongo
from flask import render_template, redirect, url_for, request, session, jsonify
import time, re, datetime
from bson.json_util import dumps
from bson import ObjectId
import OpenTokSDK

@app.route("/createWorkspace/", methods= ['POST'])
def createWorkspace():
	workspaceName=request.form['workspaceName']

	#OpenTok 
	api_key = "40606782"
	api_secret = "f8650fd90d4ad2500f15c0bd6d725d06c643b63b"
	OTSDK = OpenTokSDK.OpenTokSDK(api_key,api_secret)
	
	session_id = OTSDK.create_session().session_id
	users = request.form['users'].split(",");
	users.append(session['username'])
	timestamp = time.time()
	results = mongo.db.workspaces.insert({'name':workspaceName, 'users': users, 
								'session_id': session_id,
								'timestamp': timestamp})
	workspaces_results = {}
	workspaces_results[workspaceName] = dumps(results)
	return jsonify(result=workspaces_results, last_time = timestamp)

@app.route("/getWorkspaces/", methods= ['POST'])
def getWorkspaces():
	self = session['username']
	workspaces = mongo.db.workspaces.find({'users': { '$in' : [self]}, 'timestamp': {'$gt': int(round(float(request.form['last_time']))) + 1}})
	workspaces_results = {}
	last_time = int(round(float(request.form['last_time']))) + 1
	for workspace in workspaces:
		last_time = int(round(float(workspace['timestamp']))) + 1
		workspaces_results[workspace['name']] = dumps(workspace['_id'])
	return jsonify(result=workspaces_results, last_time = last_time)

@app.route("/addUserToWorkspace/", methods= ['POST'])
def addUserToWorkspace():
	u = request.form['contact']
	user = mongo.db.users.find_one({'name':u})
	workspace_id = "hi"
	mongo.db.workspaces.update({'workspace_id':workspace_id}, { '$push': {'users' : user['name']}})
	return 'success'

@app.route("/loadWorkspaces/", methods = ['POST'])
def loadWorkspaces():
	workspaceId = ObjectId(request.form['workspace_id'])
	f = mongo.db.items.find({'workspace_id': workspaceId, 'timestamp': {'$gt': int(round(float(request.form['last_time']))) + 1}}).sort("timestamp", 1)
	content = ""
	last_time = int(round(float(request.form['last_time']))) + 1
	for item in f:
		if not(item['creator'] == session['username'] and not(request.form['first_load'])):
			last_time = int(round(float(item['timestamp']))) + 1
			item['content'] = "<br />".join(item['content'].split("\n"))
			content = content + "<div class='content-box'><div class='content-box-inner'>" + str(item['content']) + "</div><div class='content-box-lower'><i class='icon-time'></i> by <strong>" + str(item['creator']) + "</strong> &raquo; <span class='post_times'>" + datetime.datetime.fromtimestamp(item['timestamp']).strftime('%A, %B %d, %Y @ %I:%M%p') + "</span></div></div>"
	if content == "":
		# No content found
		return jsonify(output = content, last_time = last_time)

	return jsonify(output = content, last_time = last_time)

@app.route("/addContent/", methods=['POST'])
def addContent():
	self = session['username']
	workspace_id = ObjectId(request.form['workspace_id'])
	content = request.form['content']
	timestamp = time.time()
	mongo.db.items.insert({'workspace_id': workspace_id, 'content': content, 
							'creator': self, 'timestamp': timestamp})
	item = {}
	item['content'] = content
	item['content'] = "<br />".join(item['content'].split("\n"))
	item['creator'] = self
	item['timestamp'] = timestamp
	content = "<div class='content-box'><div class='content-box-inner'>" + str(item['content']) + "</div><div class='content-box-lower'><i class='icon-time'></i> by <strong>" + str(item['creator']) + "</strong> &raquo; <span class='post_times'>" + datetime.datetime.fromtimestamp(item['timestamp']).strftime('%A, %B %d, %Y @ %I:%M%p') + "</span></div></div>"

	return jsonify(output = content, last_time = timestamp)