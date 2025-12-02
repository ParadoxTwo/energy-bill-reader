from redis import Redis
from rq import Connection, Worker, Queue

# Run from backend directory; use absolute imports for sibling modules.
from config import get_settings

def main() -> None:
  settings = get_settings()
  redis_conn = Redis.from_url(settings.redis_url)
  queue = Queue(settings.rq_queue_name, connection=redis_conn)

  with Connection(redis_conn):
    worker = Worker(queues=[queue])
    worker.work()


if __name__ == "__main__":
  main()


