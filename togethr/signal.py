from togethr import app, mongo
from flask import Flask, request, render_template
import time
#main display

@app.route('/signal')
def signal():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        while True:
            message = ws.receive()
            print message
            ws.send("It worked!")
    return "hi"


@app.route('/getPeers/')
def getPeers():
    workspace_hash = "1234"
    peers = mongo.db.workspaces.find_one({"hash":workspace_hash})['users']
    peerInfo = []
    for peer in peers:
        user_peer = mongo.db.users.find_one({"name":peer})
        timestamp = user_peer['timestamp']

        if time.time() > (timestamp + 10):
            #if the peer has been offline longer than 5 minutes, delete their ICE data
            if time.time() > (timestamp + 300):
                mongo.db.users.update({"name":peer}, {"$set": {"ice_info":""}})
        else:
            peerInfo.append(mongo.db.users.find_one({"name":peer})['ice_info'])
    return jsonify(result = peerInfo)

