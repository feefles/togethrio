from togethr import app, mongo
from flask import render_template, redirect, url_for, request, session, jsonify
from datetime import timedelta
from bson.json_util import dumps
import bcrypt, time



#function to log them in, assumes using a form
##if they cannot log in, will redirect them 
@app.route("/login/", methods = ['POST'])
def auth():
	entered_user = request.form['user']
	entered_password = request.form['password']

	# Check for some errors
	if len(entered_user) == 0:
		return jsonify(errors = 'username_none')
	if len(entered_password) == 0:
		return jsonify(errors = 'pass_none')

	# Find the user
	u = mongo.users.find_one({'name_lower': entered_user.lower()})
	if not(u == None):
		# The user was found, so continue
		if u['password'] == bcrypt.hashpw(entered_password, u['password']):
			# Assign session data for user
			session['username'] = u['name']
			session['username_lower'] = u['name_lower']

			return jsonify(user = u['name'])
		else:
			return jsonify(errors = 'signin_mismatch')
	else:
		# The user was not found
		return jsonify(errors = 'signin_mismatch')

#enters a user into the database
@app.route("/create/", methods = ['POST'])
def create():
	username = request.form['user'].strip()
	pw1 = request.form['password']
	pw2 = request.form['password2']

	# Catch some errors
	if len(request.form['user']) == 0:
		return jsonify(errors = 'username_none')

	# Make sure this isn't a duplicate username -- THIS DOES NOT YET WORK *cough* PyMongo *cough*
	name_exists = mongo.users.find_one({'name_lower': username.lower()})
	if not(name_exists == None):
		# The desired username is taken
		return jsonify(errors = 'username_taken')

	if len(pw1) == 0:
		return jsonify(errors = 'pass_none')


	#Let's put the post in the MongoDB database
	if pw1 == pw2:
		# Hash a password for the first time, with a randomly-generated salt
		hashed_password = bcrypt.hashpw(pw1, bcrypt.gensalt(12))
		user_id = mongo.users.insert({'name' : username,
								'name_lower': username.lower(),
								'password': hashed_password,
								'friends': [],
								'timestamp': time.time()
								})
		app.permanent_session_lifetime = timedelta(days=365)
		# Assign session data for user
		session.permanent = True
		session['id'] = dumps(user_id)
		session['username'] = username

		return jsonify(user = username)
	else:
		# Passwords did not match
		return jsonify(errors = 'pass_nomatch')

@app.route("/logout/", methods = ['POST'])
def logout():
	session.pop('username', None)
	return "success"