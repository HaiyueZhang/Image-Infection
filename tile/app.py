import requests
import io
import os
from PIL import Image
from io import BytesIO
from flask import Flask, jsonify, request, render_template, Response, send_file
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
servers = {}

# Global variables
approved = 'True'
resized_image_path = None
tilesize = None
xdim = None
ydim = None
CANVAS_WIDTH = None
CANVAS_HEIGHT = None
TILESERVER_URL = os.getenv('TILESERVER_URL')
CANVASSERVER_URL = os.getenv('CANVASSERVER_URL')
CLIENT_ID = 'haiyuez2'  # Replace with your netid
AUTHTOKEN = '34932bd4-fef2-4a30-aa8c-ef15e97ff004'  # Generate a unique token
VOTETOKEN = None
# Assuming global variables to store votes and sequence number
CURRENT_VOTES = 0
CURRENT_SEQ = -1
# Global variables for xloc and yloc
xloc = 0
yloc = 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sendRegister', methods=["PUT"])
def send_register():
    global tilesize, xdim, ydim, CANVAS_WIDTH, CANVAS_HEIGHT

    data = {
        "author": "Haiyue Zhang",
        "url": TILESERVER_URL,
        "token": AUTHTOKEN
    }
    response = requests.put(f'{CANVASSERVER_URL}/registerClient/{CLIENT_ID}', json=data)

    if response.status_code == 200:
        response_data = response.json()
        tilesize = response_data.get("tilesize")
        xdim = response_data.get("xdim")
        ydim = response_data.get("ydim")

        # Calculate canvas dimensions
        CANVAS_WIDTH = tilesize * xdim
        CANVAS_HEIGHT = tilesize * ydim

    return response.json(), response.status_code

@app.route('/sendImage', methods=["PUT"])
def send_image():
    global resized_image_path
    # Check if the file part is present in the request
    if 'file' not in request.files:
        return 'File not provided', 400

    file = request.files['file']
    # If the user does not select a file, the browser submits an empty file without a filename.
    if file.filename == '':
        return 'No selected file', 400
    resized_image_path = 'resized_' + file.filename

    # Resize the image
    img = Image.open(file)
    resized_img = img.resize((CANVAS_WIDTH, CANVAS_HEIGHT))
    resized_img.save(resized_image_path)

    # Send the resized image
    with open(resized_image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f'{CANVASSERVER_URL}/registerImage/{CLIENT_ID}', files=files)
    return response.text, response.status_code

@app.route('/registered', methods=["PUT"])
def PUT_registered():
    global approved, xloc, yloc, VOTETOKEN
    data = request.get_json()
    if data['authToken'] != AUTHTOKEN:  # Replace with your expected token
        return "Authorization token invalid", 455
    # Set global variables
    approved = data.get('approved', 'true')
    xloc = data.get('xloc', 0)
    yloc = data.get('yloc', 0)
    VOTETOKEN = data.get('voteToken', None)
    print(VOTETOKEN)
    print(data)
    return jsonify(data), 200

@app.route('/image', methods=['GET'])
def get_image():
    global approved, resized_image_path
    print(f"Approved: {approved}, Type: {type(approved)}")
    print(f"Resized Image Path: {resized_image_path}")
    file_exists = os.path.exists(resized_image_path)
    print(f"File Exists: {file_exists}")

    if approved == True and resized_image_path and file_exists:  # Assuming approved is a boolean
        return send_file(resized_image_path, mimetype='image/png')
    else:
        return "Image not approved or not found", 404

@app.route('/tile', methods=['GET'])
def get_tile():
    global approved, resized_image_path, xloc, yloc, tilesize

    # Check if the image is approved
    if not approved or not os.path.exists(resized_image_path):
        return "Image not approved or not found", 404

    try:
        with Image.open(resized_image_path) as img:
            # Calculate the pixel coordinates of the tile
            left = xloc * tilesize
            top = yloc * tilesize
            right = left + tilesize
            bottom = top + tilesize

            # Ensure the tile coordinates are within the image bounds
            if right > img.width or bottom > img.height:
                raise ValueError("Tile coordinates are outside the image bounds")

            print(f"Tile coordinates: ({left}, {top}, {right}, {bottom})")
            print(f"Image dimensions: {img.width}x{img.height}")
            
            # Crop the tile from the image
            tile = img.crop((left, top, right, bottom))
            tile_io = BytesIO()
            tile.save(tile_io, 'PNG')
            tile_io.seek(0)

            return Response(tile_io.getvalue(), mimetype='image/png')
    except Exception as e:
        return f"Error processing image: {e}", 500

@app.route('/votes', methods=['GET'])
def get_votes():
    # Assuming votes are stored in a variable 'votes_count'
    return jsonify({"votes": CURRENT_VOTES})

@app.route('/status', methods=['GET'])
def get_status():
    global approved, xloc, yloc

    # Prepare the status information
    status_info = {
        "image_approved": approved,  # Assuming 'approved' is a boolean indicating approval status
        "tile_location": {
            "x": xloc,  # X-coordinate of the tile
            "y": yloc   # Y-coordinate of the tile
        }
        # Add any other status information you want to include
    }

    return jsonify(status_info), 200

@app.route('/votes', methods=["PUT"])
def update_votes():
    global CURRENT_VOTES, CURRENT_SEQ

    data = request.get_json()
    received_token = data.get('authToken')
    received_votes = data.get('votes')
    received_seq = data.get('seq')
    print(data)
    # Check if the token matches
    if received_token != AUTHTOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    # Check if the sequence number is valid
    if received_seq <= CURRENT_SEQ:
        return jsonify({"error": "Conflict"}), 409

    # Update votes and sequence number
    CURRENT_VOTES = received_votes
    CURRENT_SEQ = received_seq

    return jsonify({"success": "Votes updated"}), 200


@app.route('/castVote/<int:xloc>/<int:yloc>', methods=['POST'])
def cast_vote(xloc, yloc):
    # Data to be sent to the canvas server
    vote_data = {
        "voteToken": VOTETOKEN,
        "xloc": xloc,
        "yloc": yloc
    }

    # Sending the vote to the canvas server
    vote_url = f'{CANVASSERVER_URL}/vote/{CLIENT_ID}'
    response = requests.put(vote_url, json=vote_data)

    if response.status_code == 200:
        return jsonify({"success": "Vote cast successfully"}), 200
    else:
        return jsonify({"error": "Failed to cast vote"}), response.status_code

@app.route('/update', methods=["PUT"])
def update():
    data = request.get_json()
    authToken = data.get('authToken')
    neighbors = data.get('neighbors')

    # Verify if the auth token is correct
    if authToken != AUTHTOKEN:  # Replace AUTHTOKEN with your server's auth token
        return jsonify({"error": "Unauthorized"}), 401

    # Initialize variables to track the highest votes and the corresponding neighbor
    highest_votes = CURRENT_VOTES  # Assuming CURRENT_VOTES is the current vote count of your server
    update_required = False
    selected_neighbor_url = None

    # Connect to each neighbor to get their votes
    for neighbor_url in neighbors:
        try:
            response = requests.get(f'{neighbor_url}/votes')  # Assuming /votes endpoint gives the votes
            if response.status_code == 200:
                neighbor_votes = response.json().get('votes', 0)
                # Check if this neighbor has more votes than the highest recorded
                if neighbor_votes > highest_votes:
                    highest_votes = neighbor_votes
                    selected_neighbor_url = neighbor_url
                    update_required = True
        except Exception as e:
            print(f"Error connecting to neighbor {neighbor_url}: {e}")

    # Update image and tiles if necessary
    if update_required and selected_neighbor_url:
        try:
            # Get the full image from the neighbor with the most votes
            image_response = requests.get(f'{selected_neighbor_url}/image')  # Adjust endpoint as necessary
            if image_response.status_code == 200:
                with open(resized_image_path, 'wb') as f:  # Assuming resized_image_path is where you store the image
                    f.write(image_response.content)
                # Update any other necessary information, like tiles
                # ...
                return jsonify({"success": "Image updated from neighbor"}), 200
            else:
                return jsonify({"error": "Failed to update image from neighbor"}), image_response.status_code
        except Exception as e:
            return jsonify({"error": f"Error updating image: {e}"}), 500
    else:
        return jsonify({"message": "No update required"}), 200