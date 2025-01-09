from mysql.connector import MySQLConnection
from ..conf.base import BaseConfig

class MySQL_Socket:
    def __init__(self):
        self.mysql_client_fetcher: MySQLConnection = BaseConfig.get_mysql_client_fetcher()
    
    @classmethod
    def client_fetcher(self) -> MySQLConnection:
        return self.mysql_client_fetcher
