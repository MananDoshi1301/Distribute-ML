from redis import Redis
from conf.base import BaseConfig
from typing import Optional
from mysql.connector.pooling import PooledMySQLConnection

redis_queue_client = Redis()

class MySQL_Socket:

    def __init__(self):
        self.base = BaseConfig()

    def connection(self, db_name) -> Optional[PooledMySQLConnection]:
        # conn = self.base.get_connection()        
        conn = self.base.get_connection(db_name=db_name)
        # print(f"Successful connection for master @{db_name}:", conn)
        if isinstance(conn, PooledMySQLConnection): return conn
        else: print("No MySQl conn found on socket. Returning None")
        return None    
    
    def release_client(self, conn: PooledMySQLConnection):
        self.base.release_connection(conn)