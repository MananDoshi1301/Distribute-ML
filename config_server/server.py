import functools, logging
from configure_app import create_app
from flask import Flask, jsonify, request
from conf.base import BaseConfig

# Creating app
server: Flask = create_app()

# Setting Logger
# logging.basicConfig(filename="config_server.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
user_logger = logging.getLogger("user_requests")
user_logger.setLevel(logging.INFO)
filehandler = logging.FileHandler("config_server.log")
filehandler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
user_logger.addHandler(filehandler)

# Init db if configs are stored on db

def return_response(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        response, statuscode = func(*args, **kwargs)
        return jsonify(response), statuscode
    return wrapper

def log_user(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        remote_addr, user_agent = request.remote_addr, request.headers.get("User-Agent", "Unknown")
        service_name = kwargs["service_name"]
        user_logger.info(f"Request recieved for {service_name} from {remote_addr}, User-Agent: {user_agent}")
    
        response, statuscode = func(*args, **kwargs)        
        return response, statuscode
    return wrapper    

@server.route("/configs/", methods=["GET"])
@return_response
def hello():
    return {"message": "Hello from configs :)"}, 200

@server.route("/configs/<service_name>", methods=["GET"])
@return_response
@log_user
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