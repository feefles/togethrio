from flask import Flask

app = Flask(__name__)
from pymongo import MongoClient
# app.config['MONGO_DBNAME'] = 'togethrdb'
# mongo = PyMongo(app)

@app.route('/')
def hello_world():
    return 'Hello World!'

app.config['db_username'] = "feefles"
app.config['db_password'] = "togethr2013"

server = 'linus.mongohq.com'
port = 10040
db_name = 'togethrio'

conn = MongoClient(server, port)
mongo = conn[db_name]
mongo.authenticate(app.config['db_username'], app.config['db_password'])

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


import togethr.views
import togethr.users
import togethr.actions
import togethr.tokbox
import togethr.workspaces

