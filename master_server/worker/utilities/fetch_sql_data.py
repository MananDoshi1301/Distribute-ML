from mysql.connector.pooling import PooledMySQLConnection, MySQLConnectionPool
from worker.models.models import Models
# from models.models import Models

def fetch_mysql_data(connection: PooledMySQLConnection, id: str) -> dict:
    
    try:
        if not isinstance(connection, PooledMySQLConnection):
            raise ValueError(f"Invalid connection object: {type(connection)}")
        
        cursor = connection.cursor()
        if not cursor:
            print("Cursor not found for fetching mysql data")
        print("Cursor recieved!")
        query = """
        SELECT id, model_filename, model_content, requirements_filename, requirements_content
        FROM models WHERE id = %s;
        """
        cursor.execute(query, (id,))
        data = cursor.fetchone()                
        if not data: 
            print("Error in fetching data!")
            return {}                
        model_obj = Models(data[0], data[1], data[2], data[3], data[4])                
        return model_obj.get_dict()
    except Exception as e:
        print("Some error in fetch_mysql_data function", e)
        raise
