import os, subprocess, sys
from .database import MySQL_Socket
from mysql.connector import MySQLConnection
from .utilities.fetch_sql_data import fetch_mysql_data

class Worker:
    def __init__(self, data_package: dict):
        self.mysql_client_fetcher: MySQLConnection = MySQL_Socket.client_fetcher()        
        self.data_package: dict = data_package

    def fetch_task_data(self):
        """Fetch model, requirements from mysql db"""
        record_id: str = self.data_package['record_id']
        model_and_requirements = fetch_mysql_data(self.mysql_client_fetcher, record_id)
        if not model_and_requirements: 
            print("Error fetching data from mysql. Quitting program!")
            sys.exit()
        print(model_and_requirements)        

    def fetch_model_training_data(self):
        """Fetch training data chunk from cloud"""
        ...

    def execute_model_training(self):
        ...
    

def execute_model(self, params: dict):
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
    
    # install requirements
    worker.install_env_requirements()

    # fetch data
    worker.fetch_model_training_data()

    # run model.py
    worker.execute_model_training()

    # return output    