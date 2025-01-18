import sys
from .app.utilities.upload_data import CreateDataPartitions
from .conf.base import BaseConfig
import requests, json, uuid

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
            fileserver_url = self.env_configs.get_fileserver_url().rstrip('/')
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
        # data_filename, partitions = self.task_params["MODEL_DATA"], self.task_params["TASK_PARTITION"]        
        # data_upload = CreateDataPartitions(data_filename, partitions)
        # data_upload.initiate()
        # new_names_list: list[tuple] = data_upload.get_new_filename_list()        

        # #<--> Final data info
        # data_dict: dict = {       
        #     "original_filename": self.task_params["MODEL_DATA"],     
        #     "filenames": new_names_list,
        #     "partitions": partitions,
        # }
        
        # #-- Push model to database == POST request to file_transfer_app 
        # model_path = self.task_params["MODEL_ENTRYPOINT"]            
        # response: dict = self.__store_model_requirements(model_path, 'model')
        # model_id: str = response['file_id']
        # # model_name: str = response['filename']
        # #<--> Final model info --- X
        # # model_dict: dict = {"id": model_id, "filename": model_name}        

        # #-- Push requirements.txt file
        # file_id = model_id
        # requirements_path = self.task_params["MODEL_REQUIREMENTS"]
        # response: dict = self.__store_model_requirements(requirements_path, f'requirements/{file_id}')
        # requirements_name: str = response['filename']                        
        # #<--> Final requirements info --- X
        # # requirements_dict: dict = {"id": file_id, "filename": requirements_name}

        # print("Data:", data_dict)
        # # print("Model:", model_dict)
        # # print("Requirements:", requirements_dict)
        
        # final_dict = {
        #     "data": data_dict,
        #     "record_id": file_id                       
        # }
        # print("final_dict:", final_dict)

        
        final_dict = {
            'data': {
                'original_filename': './data.csv', 
                'filenames': [
                    ('data_chunk_1.csv', '08efd064-b878-4a4d-abee-6bf21ed79621-data_chunk_1.csv'), 
                    ('data_chunk_2.csv', '77de93cc-689f-45c9-9081-c521efb9e426-data_chunk_2.csv')
                ], 
                'partitions': 2
            }, 
            'record_id': '2898d66f-2820-4920-be93-bbe8e0409f6b'
        }

        # POST request to API server with params
        try:
            url = f"{self.env_configs.get_task_manager_url().rstrip('/')}/tasks"            
            response = requests.post(url, json=final_dict)   
            print("Response from master:", response.text)         
        except Exception as e:
            print("Error submitting tasks to manager:", e)

        # -----------------------------------------------                