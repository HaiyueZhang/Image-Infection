import json
from flask import Flask, jsonify, render_template, request, send_file
import requests
import dotenv
import os

app = Flask(__name__)

status = 'accept'
xdim = 21
ydim = 26
tilesize = 5
xloc = 0
yloc = 0
voteToken = '45046605-4ef3-4dfc-84ed-cfafade8a2db'

approved = True
currentAuthToken = '34932bd4-fef2-4a30-aa8c-ef15e97ff004'
currentClientID = 'haiyuez2'
currentURL = 'http://127.0.0.1:34000'
currentAuthor = 'Haiyue Zhang'

UPLOAD_FOLDER = "uploads"

image_requests = []
client_image_mapping = {} 

def init():
    dotenv.load_dotenv()

@app.route('/')
def index():
    global file
    return render_template('index.html')

@app.route('/getClientData', methods=['GET'])
def GET_client_data():
    client_data = []
    for clientID, images in client_image_mapping.items():
        client_data.append({
            'clientID': clientID,
            'imageURLs': [f'/getImage/{clientID}/{image}' for image in images]
        })
    return jsonify(client_data), 200

@app.route('/getState', methods=['GET'])
def GET_state():
    state = jsonify({
        'status': status,
        'xdim': xdim,
        'ydim': ydim,
        'tilesize': tilesize,
        'xloc': xloc,
        'yloc': yloc,
        'voteToken': voteToken,
        'approved': approved,
        'currentAuthToken': currentAuthToken,
        'currentAuthor': currentAuthor,
        'currentClientID': currentClientID,
        'currentURL': currentURL
    })
    return state, 200

@app.route('/accept', methods=['POST'])
def POST_accept():
    global status
    status = 'accept'
    return "OK", 200

@app.route('/reject', methods=['POST'])
def POST_reject():
    global status
    status = 'reject'
    return "OK", 200

@app.route('/registerImage/<clientID>', methods=["POST"])
def POST_registerImage(clientID):
    if 'file' not in request.files:
        return "", 400
    file = request.files['file']

    if not file or not file.filename or file.filename == '':
        return "", 500

    os.makedirs(UPLOAD_FOLDER + "/" + clientID, exist_ok=True)
    file.save(UPLOAD_FOLDER + "/" + clientID + "/" + file.filename)
    print("file saved")

    if clientID in client_image_mapping:
        client_image_mapping[clientID].append(file.filename)
    else:
        client_image_mapping[clientID] = [file.filename]

    # Call to /registeredTest after saving the file
    try:
        response = requests.get(f'{request.url_root}registeredTest')
        return response.text, response.status_code
    except requests.exceptions.RequestException as e:
        return str(e), 500

    return "", 200


@ app.route('/registerClient/<clientID>', methods=["PUT"])
def PUT_registerClient(clientID):
    # this puts a json with the following
    # token : auth token for the server
    # url : "http://server:port/"
    # author : "Your Name"
    data = request.get_json()
    print("registerClient/", clientID, json.dumps(data))

    global currentClientID, currentURL, currentAuthToken, currentAuthor
    currentClientID = clientID
    currentURL = data["url"]
    currentAuthToken = data["token"]
    currentAuthor = data["author"]

    # otherwise return 200 "success" and json with
    # xdim : int // in tiles
    # ydim : int // in tiles
    # tilesize : int
    canvasInfo = jsonify({
        'xdim': xdim,
        'ydim': ydim,
        'tilesize': tilesize
    })

    return canvasInfo, 200


@ app.route("/registeredTest", methods=["GET"])
def GET_registeredTest():

    response = requests.put(f'{currentURL}/registered', json={
        'xloc': xloc,
        'yloc': yloc,
        'voteToken': voteToken,
        'approved': approved,
        'authToken': currentAuthToken,
    })

    return response.text, response.status_code

@app.route('/getImage/<clientID>/<imageFileName>', methods=["GET"])
def GET_image(clientID, imageFileName):
    return send_file(f"uploads/{clientID}/{imageFileName}", mimetype='image/png') 
