import boto3, os, docker, requests, json
from mysql.connector.pooling import PooledMySQLConnection
from worker.utilities.fetch_sql_data import fetch_mysql_data
from worker.utilities.post_sql_results import post_mysql_results
from worker.database import MySQL_Socket
from worker.utilities.manage_files import LocalFileManager
import worker.utilities.manage_training as worker_training
# from worker.utilities.manage_venv import create_venv, remove_venv
from worker.conf.amzn_s3 import S3Config
from worker.conf.static_url import BaseConfig

def print_process(header: str):
    print(f"<{"=" * 15}\t{header}\t{"=" * 15}>")

class Worker:
    def __init__(self, data_package: dict):
        self.worker_id = data_package["worker_id"]    
        self.mysql_socket = MySQL_Socket()        
        self.mysql_client_fetcher: PooledMySQLConnection = self.mysql_socket.client_fetcher(db_name="model_files")        
        self.mysql_results_cursor: PooledMySQLConnection = self.mysql_socket.client_fetcher(db_name="model_training")        
        self.data_package: dict = data_package
        self.env_configs = BaseConfig()

        # Data
        self.data_filename, self.data_fileobj = data_package['data']   
        self.original_datafilename = data_package["data_filename"]    
        self.iteration = 0   
        if "results" in self.data_package and "iteration" in self.data_package["results"]:
            self.iteration = self.data_package["results"]["iteration"]

        # File path
        self.task_data_path = "./task_data"
        self.record_id = data_package['record_id']
        self.task_id = data_package['task_id'] 

        # setup virtual env variables
        self.docker_client = docker.from_env()
        self.s3_object = S3Config()
        self.s3_client: boto3.client = self.s3_object.get_client()
        if not self.s3_client: print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ No S3 client found")
        self.bucket_name = "paritioned-data-bucket"

        # Template packets
        self.info_dict = {
            "record_id": "",
            "task_id": "",
            "data_filename": "",
            "original_datafilename": "",
            "worker_id": "",                        
            "results_path": "",
            "filename": ""
        }

    def __del__(self):
        # delete_files(self.record_id, self.task_data_path)        
        # remove_venv(self.record_id)
        if isinstance(self.mysql_client_fetcher, PooledMySQLConnection):
            self.mysql_socket.release_client(self.mysql_client_fetcher)

        if isinstance(self.mysql_client_fetcher, PooledMySQLConnection):
            self.mysql_socket.release_client(self.mysql_results_cursor)            
        ...

    def fetch_task_data(self):
        """Fetch model, requirements from mysql db"""
        print_process("Fetching Task Data")
        record_id: str = self.data_package['record_id']
        if isinstance(self.mysql_client_fetcher, PooledMySQLConnection):
            print("<---- Client Fetcher type:", type(self.mysql_client_fetcher))
            task_data: dict = fetch_mysql_data(self.mysql_client_fetcher, record_id)
            
            if not task_data: 
                print("Error fetching data from mysql. Quitting program!")
            
            # data = {
            #     "id": self.id,
            #     "model_filename": self.model_filename,
            #     "model_content": self.model_content,
            #     "requirements_filename": self.requirements_filename,
            #     "requirements_content": self.requirements_content,
            #     "upload_time": self.upload_time,
            #     "model_params": self.model_params
            # }
            # create_files(task_data["requirements_content"], task_data["model_content"], self.record_id, self.task_data_path)             
            local_file_manager = LocalFileManager(task_data["requirements_content"], task_data["model_content"], task_data["model_params"], self.record_id, self.task_data_path)
            local_file_manager.create_all_files()
        else:
            print("No mysqlclient to fetch")          

    def fetch_model_training_data(self):
        """Fetch training data chunk from cloud"""
        print_process("Fetching Model Training Data")
        path = os.path.join(self.task_data_path, self.data_filename)
        self.s3_client.download_file(self.bucket_name, self.data_fileobj, path)                  

    def setup_env(self):
        print_process("Setting up the environment")
        # self.venv_path = create_venv(self.record_id, self.task_data_path)            
        ...

    def execute_model_training(self):        
        # if not self.venv_path or not os.path.isdir(self.venv_path):
        #     raise ValueError(f"Invalid virtual environment path: {self.venv_path}")
        
        print_process("Beginning model training execution")
        
        params = {
            "task_data_path": self.task_data_path,
            "record_id": self.record_id,
            "task_id": self.task_id,
            "data_filename": self.data_filename,
            "original_datafilename": self.original_datafilename,
            "worker_id": self.worker_id
        }
                
        container_result, logs, results_dir, filename  = worker_training.begin_training(params, self.docker_client, print_process)
        # print_process("Results")
        # print(container_result)
        # print_process("Logs")
        # print(logs)

        self.info_dict = self.data_package
        res = {
            "dir": results_dir,
            "filenames": filename,
            "iteration": self.iteration + 1
        }

        for k, v in self.info_dict.items():
            if not (isinstance(v, dict) or isinstance(v, list)):
                self.info_dict[k] = str(v)

        self.info_dict["results"] = res      

    def post_training_results(self):
        # (record_id, task_id, worker_id, data_chunkname, data_sourcename, results_filename, results_content, training_iteration) 
        print_process("Posting Results")
        # Read result contents
        results_path = os.path.join(self.info_dict["results"]["dir"], self.info_dict["results"]["filenames"])
        model_content = ""
        try:
            with open(results_path, 'r') as f:
                model_content = json.loads(f.read())
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON from results file {results_path}: {e}")
            raise
            
        post_dict = {
            "record_id": self.info_dict["record_id"], 
            "task_id": self.info_dict["task_id"], 
            "worker_id": self.info_dict["worker_id"], 
            "data_chunkname": self.info_dict["data"][0], 
            "data_sourcename": self.info_dict["data"][1], 
            "results_filename": self.info_dict["results"]["filenames"], 
            "results_content": json.dumps(model_content), 
            "training_iteration": self.info_dict["results"]["iteration"]
        }
        
        if isinstance(self.mysql_results_cursor, PooledMySQLConnection):
            print("<---- Client Results Posting Connection type:", type(self.mysql_results_cursor))
            response = post_mysql_results(self.mysql_results_cursor, post_dict)            
            print("Results posting complete!")            

        # info dict:
        # {
        #     'data': ['data_chunk_2.csv', '95293ee7-70c9-4449-8197-471cfbfcd323-data_chunk_2.csv'], 
        #     'data_filename': './data.csv', 
        #     'record_id': '44a3d781-8949-4364-88b8-160e7b1fbae0', 
        #     'task_id': '547fb1b4-421b-4e2b-87aa-70089e2e39b8',
        #     'worker_id': '0eb81264-3adc-4d75-89ac-41617fee789a', 
        #     'results': {
        #         'dir': './task_data/results-44a3d781-8949-4364-88b8-160e7b1fbae0', 
        #         'filenames': 'res-0eb81264-3adc-4d75-89ac-41617fee789a.json', 
        #         'iteration': 1
        #     }
        # }        

    def post_training_request(self):
        url = f"{self.env_configs.get_task_manager_url().rstrip('/')}/optimize"
        # Info on: worker_id, data_trained, result_path, filename
        try:
            response = requests.post(url, json=self.info_dict)
            # delete_files(self.record_id, self.task_data_path)
        except Exception as e:
            print("Post training exception on worker:", e)                    
    

def execute_model(params: dict):
    """This install and runs model on worker node"""
    
    # Extract data params
    # params = {
    #     'data': ('data_chunk_1.csv', '143e2b7b-8129-4336-8141-8a0fc1881259-data_chunk_1.csv'), 
    #     "data_filename": "data.csv"
    #     'record_id': 'e4ca6707-4e80-4fbc-acdf-b607d58666e0'
    #     "task_id": "fb86cac4-0ea4-44e5-9fdd-934605a0bb73"
    # }    

    # Initialize a worker
    worker = Worker(params)    

    # fetch model, requirements, data
    worker.fetch_task_data()
    
    # fetch data
    worker.fetch_model_training_data()

    # # Setting virtual environment
    worker.setup_env()        

    # run model.py
    worker.execute_model_training()

    # Post results to the database
    worker.post_training_results()

    # return output and inform master
    worker.post_training_request()