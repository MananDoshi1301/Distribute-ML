from mysql.connector.pooling import PooledMySQLConnection, MySQLConnectionPool
from worker.models.models import Models
# from models.models import Models

def post_mysql_results(connection: PooledMySQLConnection, data_package: dict):
    try:
        if not isinstance(connection, PooledMySQLConnection):
            raise ValueError(f"Invalid connection object: {type(connection)}")
        

        # data_package = {
        #     "record_id": self.info_dict["record_id"], 
        #     "task_id": self.info_dict["task_id"], 
        #     "worker_id": self.info_dict["worker_id"], 
        #     "data_chunkname": self.info_dict["data"][0], 
        #     "data_sourcename": self.info_dict["data"][1], 
        #     "results_filename": self.info_dict["results"]["filenames"], 
        #     "results_content": model_content, 
        #     "training_iteration": self.info_dict["results"]["iteration"]
        # }

        cursor = connection.cursor()
        if not cursor: print("Cursor not found for posting mysql results")

        print("Cursor recieved!")
        query = """
        INSERT into training_records (record_id, task_id, worker_id, data_chunkname, data_sourcename, results_filename, results_content, training_iteration) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s); 
        """        
        print("Posting results: Transaction Begins")        
        connection.start_transaction()        
        query_params = (data_package["record_id"], data_package["task_id"], data_package["worker_id"], data_package["data_chunkname"], data_package["data_sourcename"], data_package["results_filename"], data_package["results_content"], data_package["training_iteration"])
        cursor.execute(query, query_params)
        connection.commit()
        print("Posting results: Transaction Complete!")
        return {"message": "Training inserted successfully!", "data": data_package}, 200            
    except Exception as e:
        connection.rollback()        
        print("Posting results: Transaction Aborts, Try Again!")
        print("Some error in post_mysql_results function", e)
        raise         
    


# def fetch_mysql_data(connection: PooledMySQLConnection, id: str) -> dict:
    
#     try:
#         if not isinstance(connection, PooledMySQLConnection):
#             raise ValueError(f"Invalid connection object: {type(connection)}")
        
#         cursor = connection.cursor()
#         if not cursor:
#             print("Cursor not found for fetching mysql data")
#         print("Cursor recieved!")
#         query = """
#         SELECT id, model_filename, model_content, requirements_filename, requirements_content
#         FROM models WHERE id = %s;
#         """
#         cursor.execute(query, (id,))
#         data = cursor.fetchone()                
#         if not data: 
#             print("Error in fetching data!")
#             return {}                
#         model_obj = Models(data[0], data[1], data[2], data[3], data[4])                
#         return model_obj.get_dict()
#     except Exception as e:
#         print("Some error in fetch_mysql_data function", e)
#         raise



# +--------------------+--------------+------+-----+---------+-------+
# | Field              | Type         | Null | Key | Default | Extra |
# +--------------------+--------------+------+-----+---------+-------+
# | id                 | varchar(36)  | NO   | PRI | NULL    |       |
# | record_id          | varchar(255) | YES  |     | NULL    |       |
# | task_id            | varchar(255) | YES  |     | NULL    |       |
# | worker_id          | varchar(255) | YES  |     | NULL    |       |
# | data_chunkname     | varchar(255) | YES  |     | NULL    |       |
# | data_sourcename    | varchar(255) | YES  |     | NULL    |       |
# | results_filename   | varchar(255) | YES  |     | NULL    |       |
# | results_content    | longblob     | YES  |     | NULL    |       |
# | training_iteration | int          | YES  |     | NULL    |       |
# +--------------------+--------------+------+-----+---------+-------+