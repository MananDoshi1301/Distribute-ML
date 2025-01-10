from flask import Flask
def create_app() -> Flask:
    server = Flask(__name__)

    return server    