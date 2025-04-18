from mysql.connector.pooling import PooledMySQLConnection, MySQLConnectionPool
from worker.models.models import Models
import json

def fetch_mysql_data(connection: PooledMySQLConnection, id: str) -> dict:
    
    try:
        if not isinstance(connection, PooledMySQLConnection):
            raise ValueError(f"Invalid connection object: {type(connection)}")
        
        cursor = connection.cursor()
        if not cursor:
            print("Cursor not found for fetching mysql data")
        print("Cursor recieved!")
        query = """
        SELECT id, model_filename, model_content, requirements_filename, requirements_content, initial_params
        FROM models WHERE id = %s;
        """
        cursor.execute(query, (id,))
        data = cursor.fetchone()                
        if not data: 
            print("Error in fetching data!")
            return {}                
        model_obj = Models(
            id=data[0], 
            model_filename=data[1], 
            model_content=data[2], 
            requirements_filename=data[3], 
            requirements_content=data[4], 
            upload_time=None, 
            model_params=json.loads(data[5])
        )           
        return model_obj.get_dict()
    except Exception as e:
        print("Some error in fetch_mysql_data function", e)
        raise
