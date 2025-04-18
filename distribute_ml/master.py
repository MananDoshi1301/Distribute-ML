from .app.utilities.upload_data import CreateDataPartitions
from .conf.base import BaseConfig
import requests, json, sys
from typing import Dict


def hello():
    print("Hello From module!")

def print_process(text: str):
    print(f"<{'-' * 8}\t{text}\t{'-' * 8}>")    

class Master:
    def __init__(self):
        self.task_params: dict = {}
        self.env_configs = BaseConfig()

    def set_config(self, config_cls: type):
        """Configures parameters for the framework"""
        required_params = ["MODEL_ENTRYPOINT", "MODEL_DATA",
                           "TASK_OUTPUT", "OPTIMIZER", "OPTIMIZER_PARAMS", "INITIAL_PARAMS"]
        final_params = {
            "MODEL_ENTRYPOINT": "", "MODEL_DATA": "", "TASK_OUTPUT": "",
            "MODEL_REQUIREMENTS": "requirements.txt", "TASK_PARTITION": 10,
            "OPTIMIZER": None, "OPTIMIZER_PARAMS": None, "INITIAL_PARAMS": None
        }

        all_configs = {k: v for k, v in vars(config_cls).items()}
        config_attrs = {k: v for k, v in all_configs.items()
                        if not k.startswith("__")}

        # Checking for required params
        for param in required_params:
            if param not in config_attrs:
                print(f"Missing required param: {param}")
                print("Exiting the program")
                sys.exit()

        # Setting overrided params
        for k, _ in final_params.items():
            if k in config_attrs:
                final_params[k] = config_attrs[k]

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

    def __push_model_params(self, file_id: str):
        try:
            fileserver_url = self.env_configs.get_fileserver_url().rstrip('/')
            learning_rate = self.task_params["OPTIMIZER_PARAMS"]["lr"]
            momentum = self.task_params["OPTIMIZER_PARAMS"]["momentum"]
            init_params = self.task_params["INITIAL_PARAMS"]
            json_data = {
                "learning_rate": learning_rate,
                "momentum": momentum,
                "initial_params": init_params
            }
            url = f"{fileserver_url}/uploads/params/{file_id}"
            data: requests = requests.post(url, json=json_data)
            
            data: list = json.loads(data.text)
            response: dict = data[0]
            if 'error' in response:
                print("Error while storing model. Quitting the program")
                sys.exit()

            return response
        except Exception as e:
            print("Error in library", e)
            sys.exit()
        ...

    def __push_env_requirements(self, model_id):
        # -- Push requirements.txt file
        file_id = model_id
        requirements_path = self.task_params["MODEL_REQUIREMENTS"]
        response: dict = self.__store_model_requirements(
            requirements_path, f'requirements/{file_id}')
        requirements_name: str = response['filename']
        # <--> Final requirements info --- X
        # requirements_dict: dict = {"id": file_id, "filename": requirements_name}

    def __push_model_to_cloud(self) -> str:
        # -- Push model to database == POST request to file_transfer_app
        model_path = self.task_params["MODEL_ENTRYPOINT"]
        response: dict = self.__store_model_requirements(model_path, 'model')
        model_id: str = response['file_id']
        # model_name: str = response['filename']
        # <--> Final model info --- X
        # model_dict: dict = {"id": model_id, "filename": model_name}
        return model_id

    def __push_data_to_cloud(self) -> dict:
        # -- Push data to cloud
        data_filename, partitions = self.task_params["MODEL_DATA"], self.task_params["TASK_PARTITION"]
        data_upload = CreateDataPartitions(data_filename, partitions)
        data_upload.initiate()
        new_names_list: list[tuple] = data_upload.get_new_filename_list()

        # <--> Final data info
        data_dict: dict = {
            "original_filename": self.task_params["MODEL_DATA"],
            "filenames": new_names_list,
            "partitions": partitions,
        }
        return data_dict

    def train(self):
        """Pushes data to cloud, model to server database and initiates training on worker"""

        final_dict = {
            'data': {
                'original_filename': './data.csv', 
                'filenames': [
                    ('data_chunk_1.csv', '49248c10-249e-4dfc-9911-8e7038d290d4-data_chunk_1.csv'), 
                    ('data_chunk_2.csv', 'd593839a-d207-48b1-a603-df0ca50bb67e-data_chunk_2.csv')
                ], 
                'partitions': 2
            }, 
            'record_id': '26ca4c5b-f605-429f-b5a6-159cfffb6062'
        }
        
        execute_all = True

        if execute_all:
            # -- Validate incoming code and data
            print_process("Pushing data to cloud begins...")
            data_dict: Dict[str] = self.__push_data_to_cloud()
            print_process("Pushing data to cloud completes!")

            # -- Push model to database == POST request to file_transfer_app
            print_process("Pushing model to cloud begins...")
            model_id: str = self.__push_model_to_cloud()
            print_process("Pushing model to cloud ends!")

            # -- Push requirements.txt file
            file_id = model_id
            print_process("Pushing requirements to cloud begins...")
            self.__push_env_requirements(model_id=model_id)
            print_process("Pushing requirements to cloud ends!")

            # -- Push params, learning_rate, momentum
            print_process("Pushing params to cloud begins...")
            self.__push_model_params(file_id=file_id)
            print_process("Pushing params to cloud ends!")

            print("Data:", data_dict)

            final_dict = {
                "data": data_dict,
                "record_id": file_id
            }
            print("\nfinal_dict =", final_dict)
            print()        

        # POST request to API server with params
        try:
            url = f"{self.env_configs.get_task_manager_url().rstrip('/')}/tasks"            
            print_process("Running jobs on workers begin...")
            response = requests.post(url, json=final_dict)
            print("Response from master:", response.text)            
        except Exception as e:
            print("Error submitting tasks to manager:", e)

        # -----------------------------------------------


if __name__ == "__main__":
    ...