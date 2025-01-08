import sys
from .app.utilities.split_data import split_data
from .conf.base import BaseConfig
import requests, json

def hello():
    print("Hello From module!")


class Master:
    def __init__(self):
        self.task_params: dict = {}
        self.env_configs = BaseConfig()

    def task_config(self, config_cls: type):
        """Configures parameters for the framework"""
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

    def __store_model_requirements(self, model_path, url_path):        
        try:
            fileserver_url = self.env_configs.get_fileserver_url()
            url = f"{fileserver_url}/uploads/{url_path}"
            with open(model_path, 'rb') as file:
                file_dict = {"file": file}
                data: requests = requests.post(url, files=file_dict)
                data: list = json.loads(data.text)
                response: dict = data[0]
                if 'error' in response:
                    print("Error while storing model. Quitting the program")
                    sys.exit()

                return response
        except Exception as e:
            print("Error in library", e)
            sys.exit()


    def train(self):
        """Pushes data to cloud, model to server database and initiates training on worker"""
        #-- Validate incoming code and data     
         
        #-- Push data to cloud 
        # (Temporary hack) change later
        data_filename, partitions = self.task_params["MODEL_DATA"], self.task_params["TASK_PARTITION"]
        new_names_list: list[str] = split_data(data_filename, partitions)

        #<-->
        data_dict: dict = {
            "filenames": new_names_list,
            "partitions": partitions,
        }
        
        #-- Push model to database == POST request to file_transfer_app 
        model_path = self.task_params["MODEL_ENTRYPOINT"]            
        response: dict = self.__store_model_requirements(model_path, 'model')
        model_id: str = response['file_id']
        model_name: str = response['filename']
        #<--> Final important info
        model_dict: dict = {"id": model_id, "filename": model_name}        

        #-- Push requirements.txt file
        file_id = model_id
        requirements_path = self.task_params["MODEL_REQUIREMENTS"]
        response: dict = self.__store_model_requirements(requirements_path, f'requirements/{file_id}')
        requirements_name: str = response['filename']                
        requirements_dict: dict = {"id": file_id, "filename": requirements_name}

        print("Model:", model_dict)
        print("Requirements:", requirements_dict)

        # POST request to API server with params

        # -----------------------------------------------        
        ...