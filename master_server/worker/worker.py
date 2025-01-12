import boto3, os, docker
from mysql.connector import MySQLConnection
from worker.utilities.fetch_sql_data import fetch_mysql_data
from worker.database import MySQL_Socket
from worker.utilities.manage_files import create_files, delete_files
from worker.utilities.manage_venv import create_venv, remove_venv
from worker.conf.amzn_s3 import S3Config

class Worker:
    def __init__(self, data_package: dict):
        mysql_socket = MySQL_Socket()        
        self.mysql_client_fetcher: MySQLConnection | None = mysql_socket.client_fetcher()        
        self.data_package: dict = data_package

        # Data
        self.data_filename, self.data_fileobj = data_package['data']   
        self.original_datafilename = data_package["data_filename"]             

        # File path
        self.task_data_path = "./task_data"
        self.record_id = data_package['record_id']

        # setup virtual env variables
        self.docker_client = docker.from_env()
        self.s3_object = S3Config()
        self.s3_client: boto3.client = self.s3_object.get_client()
        if not self.s3_client: print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ No S3 client found")
        self.bucket_name = "paritioned-data-bucket"
        self.venv_path = None

    def __del__(self):
        # delete_files(self.record_id, self.task_data_path)        
        remove_venv(self.record_id)
        ...

    def fetch_task_data(self):
        """Fetch model, requirements from mysql db"""
        record_id: str = self.data_package['record_id']
        if self.mysql_client_fetcher:
            task_data: dict = fetch_mysql_data(self.mysql_client_fetcher, record_id)
            if not task_data: 
                print("Error fetching data from mysql. Quitting program!")
            
            # data = {
            #     "id": self.id,
            #     "model_filename": self.model_filename,
            #     "model_content": self.model_content,
            #     "requirements_filename": self.requirements_filename,
            #     "requirements_content": self.requirements_content,
            #     "upload_time": self.upload_time
            # }

            create_files(task_data["requirements_content"], task_data["model_content"], self.record_id, self.task_data_path) 
        else:
            print("No mysqlclient to fetch")          

    def fetch_model_training_data(self):
        """Fetch training data chunk from cloud"""
        path = os.path.join(self.task_data_path, self.data_filename)
        self.s3_client.download_file(self.bucket_name, self.data_fileobj, path)                  

    def setup_env(self):
        self.venv_path = create_venv(self.record_id, self.task_data_path)            

    def execute_model_training(self):        
        if not self.venv_path or not os.path.isdir(self.venv_path):
            raise ValueError(f"Invalid virtual environment path: {self.venv_path}")
        
        # Prepare paths
        requirements_path = os.path.join(self.task_data_path, f"requirements-{self.record_id}.txt")
        model_path = os.path.join(self.task_data_path, f"model-{self.record_id}.py")
        data_path = os.path.join(self.task_data_path, self.data_fileobj)

        # Container paths
        container_app_path = "/app"
        container_requirements_path = f"{container_app_path}/requirements.txt"
        container_model_path = f"{container_app_path}/model.py"
        container_data_path = f"{container_app_path}/{self.original_datafilename}"

        try:                        

            container = self.docker_client.containers.run(
                "ml-base:latest",  # Replace with your Docker image
                command=f"/bin/bash -c 'ls && pip install -r {container_requirements_path} && python {container_model_path}'",
                volumes={
                    os.path.abspath(requirements_path): {"bind": container_requirements_path, "mode": "ro"},  # requirements.txt
                    os.path.abspath(model_path): {"bind": container_model_path, "mode": "ro"},  # model.py
                    os.path.abspath(data_path): {"bind": container_data_path, "mode": "ro"},  # data file
                },
                working_dir=container_app_path,  # Set working directory in the container
                detach=True,                
            )

            result = container.wait()
            logs = container.logs()
            # container.remove()
        except Exception as e:
            print(f"Error while running container: {e}")
            raise
        finally:
            if os.path.exists(self.venv_path):
                os.system(f"rm -rf {self.venv_path}")

        print("*--- Result --*\n", result)
        print("*--- Logs ---*\n", logs)           
    

def execute_model(params: dict):
    """This install and runs model on worker node"""
    
    # Extract data params
    # params = {
    #     'data': ('data_chunk_1.csv', '143e2b7b-8129-4336-8141-8a0fc1881259-data_chunk_1.csv'), 
    #     "data_filename": "data.csv"
    #     'record_id': 'e4ca6707-4e80-4fbc-acdf-b607d58666e0'
    # }    

    # Initialize a worker
    worker = Worker(params)    

    # fetch model, requirements, data
    worker.fetch_task_data()
    
    # fetch data
    worker.fetch_model_training_data()

    # Setting virtual environment
    worker.setup_env()        

    # run model.py
    worker.execute_model_training()

    # return output    