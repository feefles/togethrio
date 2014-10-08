from togethr import app, mongo
from flask import Flask, request, render_template
import time
from opentok import OpenTok
from bson import ObjectId

@app.route("/tokbox/", methods= ['POST'])
def tokbox():

	#OpenTok 
	api_key = "40606782"
	api_secret = "f8650fd90d4ad2500f15c0bd6d725d06c643b63b"
	# OTSDK = OpenTok(api_key,api_secret)
	#Find session ID of workspace
	workspace = mongo.db.workspaces.find_one({'_id': ObjectId(request.form['workspace_id'])})
	session_id = workspace['session_id']
	print "****************"
	print session_id
	print "*****************"
	#Generate session token for this user
	token = OTSDK.generate_token(session_id)
	print token
	#Return both token and session ID
	return session_id + "," + token