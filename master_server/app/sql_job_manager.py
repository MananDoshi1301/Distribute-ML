from mysql.connector.pooling import PooledMySQLConnection
from app.database import MySQL_Socket
from flask import jsonify
import time

# data_params: dict = {
#     "record_id": record_id,
#     "task_id": task_id,
#     "num_partitions": 2,
#     "expected_workers": 2,
#     "completed_workers": 0,
#     "status": "in_progress"
# }

def record_job(data_package: dict):
    # Create a connection, and make a record on the db `master_training_records`
    mysql_socket = MySQL_Socket()
    connection: PooledMySQLConnection = mysql_socket.connection(db_name="model_training")
    try:
        if not isinstance(connection, PooledMySQLConnection):
            raise ValueError(f"Invalid connection object: {type(connection)}")
                
        cursor = connection.cursor()
        if not cursor: print("Cursor not found for posting mysql results")
        print("Cursor recieved!")

        query = """
        INSERT into master_training_records (record_id, task_id, num_partitions, expected_workers, completed_workers, status) 
        VALUES (%s, %s, %s, %s, %s, %s); 
        """        
        
        connection.start_transaction()        
        query_params = (data_package["record_id"], data_package["task_id"], data_package["num_partitions"], data_package["expected_workers"], data_package["completed_workers"], data_package["status"])
        cursor.execute(query, query_params)
        connection.commit()
        connection.close()
        return jsonify({"message": "Job created successfully!", "data": data_package}), 200            
    except Exception as e:
        connection.rollback()       
        connection.close()         
        print("Some error", e)
        raise             

def worker_task_complete(record_id: str):
    mysql_socket = MySQL_Socket()
    connection: PooledMySQLConnection = mysql_socket.connection(db_name="model_training")
    try:
        if not isinstance(connection, PooledMySQLConnection):
            raise ValueError(f"Invalid connection object: {type(connection)}")
                
        cursor = connection.cursor()
        if not cursor: print("Cursor not found for posting mysql results")
        print("Cursor recieved!")

        # Get number of workers complete
        query = """
        SELECT expected_workers, completed_workers FROM master_training_records
        WHERE record_id = %s
        """

        cursor.execute(query, (record_id,))
        data = cursor.fetchone()  
        
        if not data: 
            print("Error in fetching data!")
            return None
        
        expected_workers, completed_workers = int(data[0]), int(data[1])              
        completed_workers += 1

        # Insert worker completion
        update_query = """
        UPDATE master_training_records
        SET completed_workers = %s
        WHERE record_id = %s
        """
        # connection.start_transaction()        
        query_params = (completed_workers, record_id)
        cursor.execute(update_query, query_params)

        # Change state of operation
        if expected_workers == completed_workers:
            update_query = """
            UPDATE master_training_records
            SET status = %s
            WHERE record_id = %s
            """
            query_params = ("ready_to_optimize", record_id)
            cursor.execute(update_query, query_params)        

        connection.commit()
        connection.close()

        res = {"task_completion": False}
        if expected_workers == completed_workers:
            res["task_completion"] = True
            return res                    
        
        return res

    except Exception as e:
        connection.rollback()                
        connection.close()
        print("Some error", e)
        raise     


def get_optimizer_data(record_id):    
    

    mysql_socket = MySQL_Socket()
    connection: PooledMySQLConnection = mysql_socket.connection(db_name="model_training")
    try:
        if not isinstance(connection, PooledMySQLConnection):
            raise ValueError(f"Invalid connection object: {type(connection)}")
                
        cursor = connection.cursor()
        if not cursor: print("Cursor not found for posting mysql results")
        print("Cursor recieved!")

        query = """
        SELECT results_content
        FROM training_records
        WHERE record_id = %s
        """
        query_param = (record_id,)
        cursor.execute(query, query_param)
        data = cursor.fetchall()                   
        processed_data = []
        for tup in data:
            processed_data.append(tup[0])    
        
        connection.close()
        return {"message": "Optimizer data fetched successfully!", "data": processed_data}
    except Exception as e:            
        connection.close()         
        print("Some error", e)
        raise                 