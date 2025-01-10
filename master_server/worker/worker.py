from mysql.connector import MySQLConnection
from worker.utilities.fetch_sql_data import fetch_mysql_data
from worker.database import MySQL_Socket
from worker.utilities.create_files import create_files
from worker.utilities.delete_files import delete_files

class Worker:
    def __init__(self, data_package: dict):
        mysql_socket = MySQL_Socket()        
        self.mysql_client_fetcher: MySQLConnection | None = mysql_socket.client_fetcher()        
        self.data_package: dict = data_package

        self.task_data_path = "./task_data"
        self.record_id = data_package['record_id']

    def __del__(self):
        # delete_files(self.record_id, self.task_data_path)
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
        ...

    def install_env_requirements(self):
        """Install environment requirements"""
        ...

    def execute_model_training(self):
        ...
    

def execute_model(params: dict):
    """This install and runs model on worker node"""
    
    # Extract data params
    # params = {
    #     'data': ('data_chunk_1.csv', '143e2b7b-8129-4336-8141-8a0fc1881259-data_chunk_1.csv'), 
    #     'record_id': 'e4ca6707-4e80-4fbc-acdf-b607d58666e0'
    # }    

    # Initialize a worker
    worker = Worker(params)    

    # fetch model, requirements, data
    worker.fetch_task_data()
    
    # fetch data
    worker.fetch_model_training_data()
    
    # install requirements
    worker.install_env_requirements()

    # run model.py
    worker.execute_model_training()

    # return output    