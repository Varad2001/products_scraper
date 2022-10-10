import redis
import dotenv
import os


def connect_redis():
    try :
        dotenv.load_dotenv()
        host = os.getenv('redishost')
        port = os.getenv('redisport')
        passwd = os.getenv('redispasswd')

        r = redis.Redis(
            host=host,
            port = int(port),
            password=passwd
        )

        if r.ping():
            print("Redis connected successfully.")
            return r
    except Exception as e:
        print("Could not connect to redis server due to the following error : ")
        print(e)
        return 0


def increase_value(r, key):
    try :
        r.incr(key)
        return 1
    except Exception as e:
        print("Value increment failed for key :", key)
        print(e)
        return 0


def get_value(r, key):
    try :
        return int(r.get(key))
    except Exception as e:
        print("Could not fetch value for key : ", key)
        print(e)
        return None

