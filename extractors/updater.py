import logging

import pymongo
import dotenv
import os

import requests
from queue import Queue

from extractors import newegg
from extractors import send_request


def update_items():
    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')
    arg = os.getenv('CLUSTER_ARG')


    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.{arg}.mongodb.net/?retryWrites=true&w=majority")

    # tasks_db.productCategory
    try :
        db = client['tasks_db']
        table = db['products']
    except Exception as e:
        print(f"Invalid credentials.")
        logging.exception(e)
        return

    q = Queue()
    cursor = table.find({})

    for item in cursor:
        print("Updating")

        try :
            obj_id = item['_id']
            url = item['sellers']['productLink']
            category = item['productCategory']
            price = item['productPrice']
            page = send_request.send_request(url)       # raise missing-schema exception if invalid url
            if not page :
                continue

            new_price = newegg.get_price(page)
            discount = newegg.get_discount_info(page)
            if discount:
                table.update_one(
                    {'_id' : obj_id},
                    {'$set' : {'productPrice': new_price, 'productPriceType' : 'Discounted', 'lastPrice' : price}}
                )
            else:
                table.update_one(
                    {'_id': obj_id},
                    {'$set': {'productPrice': new_price}}
                )

            print("Update successful.")
        except requests.exceptions.ConnectionError as e:
            table.delete_one(
                {'_id' : obj_id}
            )
            print("Item deleted.")
        except Exception as e:
            logging.exception(e)
            continue

    print("Update finished.")

#update_items()
