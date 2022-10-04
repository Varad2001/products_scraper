import logging

import dotenv
import os
import pymongo
from bson import ObjectId
from extractors.newegg import get_all_details




def get_address_by_id(id):
    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')

    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.x6statp.mongodb.net/?retryWrites=true&w=majority")

    # tasks_db.productCategory
    db = client['tasks_db']
    table = db['productCategory']

    id = ObjectId(id)

    cursor = table.find({"_id" : id})
    for document in cursor:
        try :
            url = document['amazonCategoryAddress']
            category = document['categoryName']
            return url, category
        except Exception as e:
            print(e)
            return None



def get_details_and_store(url, q, category):
    try :
        results = get_all_details(url, q, category)

        dotenv.load_dotenv()
        user = os.getenv('USER')
        passwd = os.getenv('PASSWD')

        # connect to the mongodb database
        client = pymongo.MongoClient(
            f"mongodb+srv://{user}:{passwd}@cluster0.x6statp.mongodb.net/?retryWrites=true&w=majority")

        db_name = 'Products'
        table_name = "Products_details"
        db = client[db_name]
        table = db[table_name]

        table.insert_one(results)

        client.close()
        return True
    except Exception as e:
        logging.exception(e)
        print(e)
        return False
