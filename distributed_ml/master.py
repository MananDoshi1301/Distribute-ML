import sys
from .app.utilities.upload_data import CreateDataPartitions
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
        # data_filename, partitions = self.task_params["MODEL_DATA"], self.task_params["TASK_PARTITION"]        
        # data_upload = CreateDataPartitions(data_filename, partitions)
        # data_upload.initiate()
        # new_names_list: list[tuple] = data_upload.new_filename_list        

        # #<--> Final data info
        # data_dict: dict = {            
        #     "filenames": new_names_list,
        #     "partitions": partitions,
        # }
        
        # #-- Push model to database == POST request to file_transfer_app 
        # model_path = self.task_params["MODEL_ENTRYPOINT"]            
        # response: dict = self.__store_model_requirements(model_path, 'model')
        # model_id: str = response['file_id']
        # model_name: str = response['filename']
        # #<--> Final model info
        # model_dict: dict = {"id": model_id, "filename": model_name}        

        # #-- Push requirements.txt file
        # file_id = model_id
        # requirements_path = self.task_params["MODEL_REQUIREMENTS"]
        # response: dict = self.__store_model_requirements(requirements_path, f'requirements/{file_id}')
        # requirements_name: str = response['filename']                
        # #<--> Final requirements info
        # requirements_dict: dict = {"id": file_id, "filename": requirements_name}

        # print("Data:", data_dict)
        # print("Model:", model_dict)
        # print("Requirements:", requirements_dict)

        # final_dict = {
        #     "data": data_dict,
        #     "model": model_dict,
        #     "requirements": requirements_dict
        # }
        # print("final_data:", final_dict)

        # final_data= {'data': {'filenames': [('data/data_chunk_1.csv', '143e2b7b-8129-4336-8141-8a0fc1881259-data_chunk_1.csv'), ('data/data_chunk_2.csv', '2c1310ed-18d2-4a01-980f-405e8765e592-data_chunk_2.csv')], 'partitions': 2}, 'model': {'id': 'e4ca6707-4e80-4fbc-acdf-b607d58666e0', 'filename': 'model.py'}, 'requirements': {'id': 'e4ca6707-4e80-4fbc-acdf-b607d58666e0', 'filename': 'requirements.txt'}}

        # POST request to API server with params

        # -----------------------------------------------        
        ...