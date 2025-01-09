from rq import Queue
from redis import Redis
from app.database import redis_queue_client

class RedisQueue:
    def __init__(self):
        self.redis_client: Redis = redis_queue_client        
        self.__training_queue: Queue = Queue(connection=self.redis_client)

    def get_training_queue(self):
        return self.__training_queue
    ...