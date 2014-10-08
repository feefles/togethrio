from togethr import app
from flask import render_template, redirect, url_for, request, escape, session

#main display

@app.route("/")
def display():
	if 'username' in session:
		return render_template('main.html', user=session['username'])
	else:
		return render_template('login.html')