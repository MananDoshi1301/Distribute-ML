# from mysql.connector import MySQLConnection
# from conf.base import BaseConfig

# class MySQL_Socket:
#     def __init__(self):
#         self.mysql_client = BaseConfig()        
#         # self.mysql_client_fetcher: MySQLConnection = BaseConfig.get_mysql_client_fetcher()
        
#     def client_fetcher(self) -> MySQLConnection:
#         self.mysql_client.fetch_config()
#         obj = self.mysql_client.get_mysql_client_fetcher()
#         # return self.mysql_client_fetcher
#         return obj


from mysql.connector.pooling import PooledMySQLConnection
# from conf.base import BaseConfig
# from master_server import BaseConfig
from worker.conf.base import BaseConfig
# from worker.conf.base2 import BaseConfig
from typing import Optional

class MySQL_Socket:

    def __init__(self):
        self.base = BaseConfig()

    def client_fetcher(self) -> Optional[PooledMySQLConnection]:
        # conn = self.base.get_connection()
        conn = self.base.get_connection()
        print("Connection:", conn)
        if isinstance(conn, PooledMySQLConnection): return conn
        else: print("No MySQl conn found on socket. Returning None")
        return None
    
    def release_client(self, conn: PooledMySQLConnection):
        self.base.release_connection(conn)