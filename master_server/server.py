from flask import Flask, request, jsonify
from master_server.app_configure import create_app
import json

server: Flask = create_app()
 
# Initialize redis


@server.route("/tasks", methods=["POST"])
def process_task():
    data = request.get_json()          
    return jsonify({"message": "Route sucess"}), 200

if __name__ == "__main__":
    PORT = 5002
    server.run(debug=True, port=PORT)