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
    max_threads = int(get_app_settings()['updateThreads'])
    pool = Pool(max_threads)
    procs = []

    for item in cursor[1:]:
        result = pool.apply_async(update_one_item, args=(item,))
        procs.append(result)

    print("Starting update...")

    results = [result.get() for result in procs]

    # print("Update finished.")


def update_one_item(sellers):

    # connect with mongodb and update this result
    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')
    arg = os.getenv('CLUSTER_ARG')

    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.{arg}.mongodb.net/?retryWrites=true&w=majority")

    # first update the price history table , then at last update stockCount in 'products' table
    db = client[settings.db_products]
    table = db[settings.product_price_history_table]

    print(sellers)
    for item in sellers['sellers']:
        print(item)
        if item['sellerName'] == 'Amazon':
            data = amazon.get_all_details(item['productLink'])
        elif item['sellerName'] == 'NewEgg' :
            data = newegg.get_all_details(item['productLink'])
        elif item['sellerName'] == 'BestBuy' :
            data = bestbuy.get_all_details(item['productLink'])
        else :
            print("Following seller name not found : ", item['sellerName'])
            return

        # find the document corresponding to this product and seller
        cursor = table.find(
            {
                'productID' : sellers['_id'],
                'sellerID' : item['sellerID']
            }
        )
        #
        print(list(cursor))
        for i in cursor:
            item = i
            break
        #print(item)
        """item_id = item['_id']           # get _id of this item

        # update the document with this _id
        table.update_one(
            {
                '_id' : item_id
            },
            {
                '$set' :
                {
                'priceUpdateTime': datetime.timestamp(datetime.now()),
                'productPrice': data['productPrice'],
                'productPriceType': data['productPriceType'],
                'productShippingFee': data['productShippingFee'],
                'lastPrice' : data['lastPrice']
            }
            }
        )

        # update the stock count for this seller
        item['stockCount'] = data['stockCount']

    # update the 'products' table
    table = db[settings.db_products]
    table.update_one(
        {
            '_id' : sellers['_id']
        },
        {
            'lastUpdate' : datetime.timestamp(datetime.now()),
            'sellers' : sellers
        }
    )"""
    client.close()

    print(f"Updated item. Id : {sellers['_id']}")


if __name__ == '__main__' :
    update_items()
