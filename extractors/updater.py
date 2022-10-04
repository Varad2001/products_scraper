import pymongo
import dotenv
import os
from extractors.newegg import get_all_details
from queue import Queue


def update_items():
    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')

    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.x6statp.mongodb.net/?retryWrites=true&w=majority")

    # tasks_db.productCategory
    db = client['Products']
    table = db['Products_details']

    q = Queue()
    cursor = table.find({})

    for item in cursor:
        print("updating")
        url = item['sellers']['productLink']
        category = item['productCategory']
        try :
            results = get_all_details(url, q, category)
            table.insert_one(results)
            print("update successful.")
        except Exception as e:
            print(e)
            continue


update_items()