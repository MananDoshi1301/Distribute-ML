from mysql.connector.pooling import PooledMySQLConnection
# from conf.base import BaseConfig
# from master_server import BaseConfig
from worker.conf.base import BaseConfig
# from worker.conf.base2 import BaseConfig
from typing import Optional

class MySQL_Socket:

    def __init__(self):
        self.base = BaseConfig()

    def client_fetcher(self, db_name) -> Optional[PooledMySQLConnection]:
        # conn = self.base.get_connection()
        conn = self.base.get_connection(db_name=db_name)
        print(f"Successful connection for {db_name}:", conn)
        if isinstance(conn, PooledMySQLConnection): return conn
        else: print("No MySQl conn found on socket. Returning None")
        return None
    
    
    def release_client(self, conn: PooledMySQLConnection):
        self.base.release_connection(conn)