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
        # print("Cursor recieved!")

        query = """
        INSERT into master_training_records (record_id, task_id, num_partitions, expected_workers, completed_workers, status, total_iterations, iterations_complete) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s); 
        """        
        
        connection.start_transaction()        
        query_params = (data_package["record_id"], data_package["task_id"], data_package["num_partitions"], data_package["expected_workers"], data_package["completed_workers"], data_package["status"], data_package["total_iterations"], data_package["iterations_complete"])
        cursor.execute(query, query_params)
        connection.commit()
        connection.close()
        return jsonify({"message": "Job created successfully!", "data": data_package}), 200            
    except Exception as e:
        connection.rollback()       
        connection.close()         
        print("Some error", e)
        raise             

# Worker call
def worker_task_complete(record_id: str):
    mysql_socket = MySQL_Socket()
    conn = mysql_socket.connection(db_name="model_training")
    try:
        if not hasattr(conn, "cursor"):
            raise ValueError(f"Invalid connection: {type(conn)}")
        cursor = conn.cursor()

        update_sql = """
        UPDATE model_training.master_training_records
        SET 
          completed_workers = completed_workers + 1,
          status = CASE
            WHEN completed_workers + 1 = expected_workers THEN 'ready_to_optimize'
            ELSE status
          END
        WHERE record_id = %s
        """
        cursor.execute(update_sql, (record_id,))
        conn.commit()

        # cursor.rowcount is how many rows were updated—should be 1.
        if cursor.rowcount != 1:
            raise RuntimeError(f"No such record: {record_id}")

        # Now fetch the new counts & status in one go
        cursor.execute(
          "SELECT completed_workers, expected_workers, status "
          "FROM model_training.master_training_records "
          "WHERE record_id = %s",
          (record_id,)
        )
        comp, exp, status = cursor.fetchone()
        conn.close()

        return {
            "task_completion": (comp == exp),
            "completed_workers": comp,
            "expected_workers": exp,
            "status": status
        }

    except Exception:
        conn.rollback()
        conn.close()
        raise

# Optimizer calls
def get_optimizer_data(record_id):    
    

    mysql_socket = MySQL_Socket()
    connection: PooledMySQLConnection = mysql_socket.connection(db_name="model_training")
    try:
        if not isinstance(connection, PooledMySQLConnection):
            raise ValueError(f"Invalid connection object: {type(connection)}")
                
        cursor = connection.cursor()
        if not cursor: print("Cursor not found for posting mysql results")
        # print("Cursor recieved!")

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

def update_training_state(record_id):
    mysql_socket = MySQL_Socket()
    connection: PooledMySQLConnection = mysql_socket.connection(db_name="model_training")
    try:
        if not isinstance(connection, PooledMySQLConnection):
            raise ValueError(f"Invalid connection object: {type(connection)}")
                
        cursor = connection.cursor()
        if not cursor: print("Cursor not found for posting mysql results")
        # print("Cursor recieved!")
        update_query = """
        UPDATE master_training_records
        SET status = %s
        WHERE record_id = %s
        """
        connection.start_transaction()
        query_params = ("optimizing", record_id)
        cursor.execute(update_query, query_params)   
        connection.commit()
        connection.close()

    except Exception as e:
        connection.rollback()                
        connection.close()
        print("Some error on updating state:", e)
        raise     

def save_new_params(record_id: str, params: dict):
    """Update model_files with this new weights"""
    mysql_socket = MySQL_Socket()
    connection: PooledMySQLConnection = mysql_socket.connection(db_name="model_files")
    try:
        if not isinstance(connection, PooledMySQLConnection):
            raise ValueError(f"Invalid connection object: {type(connection)}")
                
        cursor = connection.cursor()
        if not cursor: print("Cursor not found for posting mysql results")
        # print("Cursor recieved!")
        update_query = """
        UPDATE models
        SET initial_params = %s
        WHERE id = %s
        """
        connection.start_transaction()
        query_params = (json.dumps(params), record_id)
        cursor.execute(update_query, query_params)   
        connection.commit()
        connection.close()

    except Exception as e:
        connection.rollback()                
        connection.close()
        print("Some error on updating state:", e)
        raise    

def delete_old_transaction_records(record_id: str):
    """Delete all transactions from training_records for a certain record_id;"""
    mysql_socket = MySQL_Socket()
    del_connection: PooledMySQLConnection = mysql_socket.connection(db_name="model_training")
    try:
        if not isinstance(del_connection, PooledMySQLConnection):
            raise ValueError(f"Invalid connection object: {type(del_connection)}")
                
        cursor = del_connection.cursor()
        if not cursor: print("Cursor not found for posting mysql results")
        # print("Cursor recieved!")
        update_query = """
        DELETE FROM model_training.training_records
        WHERE record_id = %s
        """
        del_connection.start_transaction()
        query_params = (record_id,)
        cursor.execute(update_query, query_params)   
        del_connection.commit()
        del_connection.close()        

    except Exception as e:
        del_connection.rollback()                
        del_connection.close()
        print("Some error on updating state:", e)
        raise        

def get_iterations_info(record_id: str) -> dict:
    mysql_socket = MySQL_Socket()
    connection: PooledMySQLConnection = mysql_socket.connection(db_name="model_training")
    try:
        if not isinstance(connection, PooledMySQLConnection):
            raise ValueError(f"Invalid connection object: {type(connection)}")
                
        cursor = connection.cursor()
        if not cursor: print("Cursor not found for posting mysql results")
        # print("Cursor recieved!")

        # Get number of workers complete
        data_package = {
            "success": False, 
            "more_iterations": False,
            "data": {
                "total_iterations": None,
                "iterations_complete": None
            }
        }
        query = """
        SELECT total_iterations, iterations_complete FROM model_training.master_training_records
        WHERE record_id = %s
        """

        cursor.execute(query, (record_id,))
        data = cursor.fetchone()  
        
        if not data: 
            print("Error in fetching data!")
            return data_package
        
        total_iterations, iterations_complete = int(data[0]), int(data[1])
        data_package["success"] = True
        
        if total_iterations > iterations_complete:
            next_iteration = iterations_complete + 1
            data_package["more_iterations"] = True
            update_query = """
            UPDATE model_training.master_training_records
            SET iterations_complete = %s
            WHERE record_id = %s
            """
            query_params = (next_iteration, record_id)
            cursor.execute(update_query, query_params)
            
            connection.commit()
        connection.close()

        data_package["data"]["total_iterations"] = total_iterations
        data_package["data"]["iterations_complete"] = iterations_complete

        return data_package
    except Exception as e:
        print("Some errors on fetching iterations_info:", e)
        raise e

def get_reiteration_info(record_id: str) -> dict:
    mysql_socket = MySQL_Socket()
    connection: PooledMySQLConnection = mysql_socket.connection(db_name="model_training")
    try:
        if not isinstance(connection, PooledMySQLConnection):
            raise ValueError(f"Invalid connection object: {type(connection)}")
                
        cursor = connection.cursor()
        if not cursor: print("Cursor not found for posting mysql results")
        # print("Cursor recieved!")

        # I need record_id, orginal_filename, filenames, partitions, 
        # data_dict = {
        #     'original_filename': './data.csv', 
        #     'filenames': [
        #         ['data_chunk_1.csv', '5d3a7010-9f87-45c8-b82a-bade79ad0e37-data_chunk_1.csv'], 
        #         ['data_chunk_2.csv', '085014c1-55d7-40eb-a4a4-8c5516008d2d-data_chunk_2.csv']
        #     ], 
        #     'partitions': 2, 
        #     'record_id': '80c69045-06a0-4d48-b506-118cc8be904d'
        # }
        data_dict = {
            "record_id": record_id,
            "original_filename": "",
            "filenames": [],
            "partitions": 0            
        }

        # getoriginal_filename
        query = """
        SELECT data_originalname FROM model_training.training_records 
        WHERE record_id=%s
        """
        cursor.execute(query, (record_id,))
        data = cursor.fetchall()          
        if not data: 
            print("Error in fetching data_originalname!")
            raise ValueError("No data found")            
                
        original_filename = data[0][0]
        data_dict["original_filename"] = original_filename

        # Get all data_chunkname, data_sourcename
        query = """
        SELECT data_chunkname, data_sourcename FROM model_training.training_records 
        WHERE record_id = %s
        """
        cursor.execute(query, (record_id,))
        data = cursor.fetchall()          
        if not data: 
            print("Error in fetching data_chunkname or data_sourcename!")
            raise ValueError("No data found")    

        # print("-9-9-9-9-9-9-9-: datanames:", data, type(data))     

        training_data_list = []
        for data_tuple in data:            
            training_data_list.append([data_tuple[0], data_tuple[1]])
        
        # original_filename = data[0]
        # data_dict["original_filename"] = original_filename        
        data_dict["filenames"] = training_data_list
        data_dict["partitions"] = len(training_data_list)
        connection.close()
        
        return {"success": True, "data": data_dict}
    except Exception as e:
        print("Some errors on fetching iterations_info:", e)
        raise e
    ...

def update_worker_on_new_iteration(record_id):
    mysql_socket = MySQL_Socket()
    connection: PooledMySQLConnection = mysql_socket.connection(db_name="model_training")
    try:
        if not isinstance(connection, PooledMySQLConnection):
            raise ValueError(f"Invalid connection object: {type(connection)}")
                
        cursor = connection.cursor()
        if not cursor: print("Cursor not found for posting mysql results")
        # print("Cursor recieved!")
        update_query = """
        UPDATE model_training.master_training_records
        SET completed_workers = %s
        WHERE record_id = %s
        """
        connection.start_transaction()
        query_params = (0, record_id)
        cursor.execute(update_query, query_params)   
        connection.commit()
        connection.close()

    except Exception as e:
        connection.rollback()                
        connection.close()
        print("Some error on updating state:", e)
        raise   

# Testing calls