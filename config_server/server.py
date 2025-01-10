import functools
from configure_app import create_app
from flask import Flask, jsonify
from conf.base import BaseConfig

server: Flask = create_app()

# Init db if configs are stored on db

def return_response(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        response, statuscode = func(*args, **kwargs)
        return jsonify(response), statuscode
    return wrapper

@server.route("/", methods=["GET"])
@return_response
def hello():
    return {"message": "Hello from configs :)"}, 200

@server.route("/configs/<service_name>", methods=["GET"])
@return_response
def get_config(service_name: str):

    err_res: dict = {"error": ""}
    success_response = {"message": "Service Found successfully", "config": ""}
    config_details = BaseConfig()
    keywords: dict = {
        "mysql": config_details.get_mysql_dict(),
        "fileserver": config_details.get_fileserver_url(),
        "amazon_s3": config_details.get_s3_url(),
        "task_manager": config_details.get_task_manager_server_url()
    }

    config = keywords.get(service_name, None)    
    if not config:
        err_res["error"] = "Service not found!"
        return err_res, 400

    success_response["config"] = config
    return success_response, 200    


if __name__ == "__main__":
    PORT = 5003
    server.run(debug=True, port=PORT)