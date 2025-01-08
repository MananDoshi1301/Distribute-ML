import sys
from .app.utilities.split_data import split_data
from .database.init_redis import redis_queue_connection
import requests

def hello():
    print("Hello From module!")


class Master:
    def __init__(self):
        self.task_params: dict = {}

    def task_config(self, config_cls: type):
        required_params = ["MODEL_ENTRYPOINT", "MODEL_DATA", "TASK_OUTPUT"]
        final_params = {
            "MODEL_ENTRYPOINT": "", "MODEL_DATA": "", "TASK_OUTPUT": "",
            "MODEL_REQUIREMENTS": "requirements.txt", "TASK_PARTITION": 10
        }
        
        all_configs = {k:v for k, v in vars(config_cls).items()}
        config_attrs = {k:v for k, v in all_configs.items() if not k.startswith("__")}
        
        # Checking for required params
        for param in required_params:
            if param not in config_attrs: 
                print(f"Missing required param: {param}")
                print("Exiting the program")
                sys.exit()

        # Setting overrided params
        for k, _ in final_params.items():
            if k in config_attrs: final_params[k] = config_attrs[k]

        print("Task config set successfully!")
        self.task_params = final_params

    def train(self):
        #-- Validate incoming code and data     
         
        #-- Push data to cloud
        
        #-- Push model to database == POST request to file_transfer_app 
        filepath = self.task_params["MODEL_ENTRYPOINT"]    
        try:
            url = f"http://0.0.0.0:8000/upload"
            with open(filepath, 'rb') as file:
                file_dict = {'file': file}
                data = requests.post(url, files=file_dict)
                print(data)
        except Exception as e:
            print(e)

        # POST request to API server with params

        # -----------------------------------------------        
        ...