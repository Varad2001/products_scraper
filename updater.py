import logging

import pymongo
import dotenv
import os
from datetime import datetime
from multiprocessing import Pool
from extractors import newegg, amazon, bestbuy
from helpers import get_app_settings
import settings


def update_items():
    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')
    arg = os.getenv('CLUSTER_ARG')

    db_name = settings.db_products
    table_name = settings.products_table

    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.{arg}.mongodb.net/?retryWrites=true&w=majority")

    # tasks_db.productCategory
    try :
        db = client[db_name]
        table = db[table_name]
    except Exception as e:
        print(f"Invalid credentials.")
        logging.exception(e)
        return

    cursor = list(table.find({}))
    max_threads = get_app_settings()['max_threads']
    pool = Pool(max_threads)
    procs = []

    for item in cursor:
        result = pool.apply_async(update_one_item, args=(item,))
        procs.append(result)

    print("Starting update...")

    results = [result.get() for result in procs]

    print("Update finished.")


def update_one_item(item):
    obj_id = item['_id']
    results = []
    sellers = item['sellers']
    for seller in sellers:
        if seller['sellerName'].lower().strip() == 'amazon':
            result = amazon.get_all_details(seller['productLink'])
            if result:
                results.append(result)
        if seller['sellerName'].lower().strip() == 'bestbuy':
            result = bestbuy.get_all_details(seller['productLink'])
            if result:
                results.append(result)
        if seller['sellerName'].lower().strip() == 'newegg':
            result = newegg.get_all_details(seller['productLink'])
            if result:
                results.append(result)

    # connect with mongodb and update this result
    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')
    arg = os.getenv('CLUSTER_ARG')

    db_name = settings.db_products
    table_name = settings.products_table

    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.{arg}.mongodb.net/?retryWrites=true&w=majority")
    db = client[db_name]
    table = db[table_name]

    table.update_one(
        {'_id': obj_id},
        {'$set': {
            'lastUpdate': datetime.timestamp(datetime.now()),
            'sellers': results
        }}
    )
    client.close()
    print(f"Updated item. Id : {obj_id}")


if __name__ == '__main__' :
    update_items()
