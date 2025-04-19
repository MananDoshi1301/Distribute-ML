from mysql.connector.pooling import PooledMySQLConnection
from app.database import MySQL_Socket
from flask import jsonify
import time, json

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
        # print("RESPONSE:\n", data)                
        processed_data = []
        for tup in data:
            # print()
            # print(tup[0], type(tup[0]))
            decoded_str = tup[0].decode('utf-8')            
            parsed_data = json.loads(decoded_str)
            processed_data.append(parsed_data)    
        # print("RESPONSE:\n\n", processed_data)

        connection.close()
        return {"message": "Optimizer data fetched successfully!", "data": processed_data}
    except Exception as e:            
        connection.close()         
        print("Some error", e)
        raise               

    [
        (b'[{"layer": "linear", "type": "weight", "values": [[-0.04837987944483757, 0.015684878453612328, 0.014911244623363018, 0.09553203731775284, 0.03261147812008858, 0.04086461290717125, 0.03488050773739815, -0.08591537177562714]]}, {"layer": "linear", "type": "bias", "values": [-0.08242813497781754]}]',),

        (b'[{"layer": "linear", "type": "weight", "values": [[-0.03884708508849144, 0.013743504881858826, -0.11262378841638565, 0.022557340562343597, 0.04209470376372337, -0.010569879785180092, -0.06886139512062073, -0.08061739057302475]]}, {"layer": "linear", "type": "bias", "values": [0.101676344871521]}]',)
    ]
