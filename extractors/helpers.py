import logging
import multiprocessing

import dotenv
import os
import pymongo
from bson import ObjectId

from extractors import newegg, bestbuy


def format_url(url):
    url2 = url.split('//')[1].split('/')
    result = url2[0]
    for s in url2[1:4]:
        result += f"/{s}"

    result = "https://" + result

    return result


def get_address_by_id(id):
    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')
    arg = os.getenv('CLUSTER_ARG')

    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.{arg}.mongodb.net/?retryWrites=true&w=majority")

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
            logging.exception(e)

            return None, None


def get_details_from_newegg_and_store(url, q, category):
    try :
        results = newegg.get_all_details(url, q, category)

        dotenv.load_dotenv()
        user = os.getenv('USER')
        passwd = os.getenv('PASSWD')
        arg = os.getenv('CLUSTER_ARG')
        db_name = os.getenv('db_name')
        table_name = os.getenv('table_name')

        # connect to the mongodb database
        client = pymongo.MongoClient(
            f"mongodb+srv://{user}:{passwd}@cluster0.{arg}.mongodb.net/?retryWrites=true&w=majority")

        #db_name = 'tasks_db'
        #table_name = "products"
        db = client[db_name]
        table = db[table_name]

        table.insert_one(results)

        client.close()
        return True
    except Exception as e:
        logging.exception(e)
        print("Could not save the details to database.")
        print(url)
        print(results)
        return False


def get_details_from_bestbuy_and_store(url, q, category):
    try :
        results = bestbuy.get_all_details(url, q, category)

        dotenv.load_dotenv()
        user = os.getenv('USER')
        passwd = os.getenv('PASSWD')
        arg = os.getenv('CLUSTER_ARG')
        db_name = os.getenv('db_name')
        table_name = os.getenv('table_name')

        # connect to the mongodb database
        client = pymongo.MongoClient(
            f"mongodb+srv://{user}:{passwd}@cluster0.{arg}.mongodb.net/?retryWrites=true&w=majority")

        #db_name = 'tasks_db'
        #table_name = "products"
        db = client[db_name]
        table = db[table_name]

        table.insert_one(results)

        client.close()
        return True
    except Exception as e:
        logging.exception(e)
        print("Could not save the details to database.")
        return False

"""url4 = "https://www.newegg.com/creality-ender-3-v2-black/p/288-00DY-00001"
print(get_details_from_newegg_and_store(url4, multiprocessing.Queue(), '4534535'))"""
