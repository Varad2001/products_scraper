
import dotenv
import os
import pymongo
from bson import ObjectId
from datetime import datetime
from rake_nltk import Rake
import nltk
import settings
import logging
logging.basicConfig(filename='extractors/scraper.log', level=logging.DEBUG, format="%(name)s:%(levelname)s:%(asctime)s:%(message)s")
import warnings
warnings.filterwarnings('ignore')


def get_important_text(text):
    nltk.download('stopwords')
    nltk.download('punkt')
    r = Rake()
    r.extract_keywords_from_text(text)
    return r.get_ranked_phrases()


def format_url(url, str):

    if not str in url :
        return 0
    url_parts = url.split(str)

    second_part = url_parts[1]

    for i in range(len(second_part)):
        if second_part[i] != '&':
            continue
        else:
            second_part = second_part[i:]
            break

    result = url_parts[0] + second_part

    return result


def get_formatted_url(url):
    new_url = format_url(url, "&page=")
    if new_url:
        url = new_url

    new_url = format_url(url, "&ref=sr_pg_")
    if new_url:
        url = new_url

    return url


def get_address_by_id(id):
    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')
    arg = os.getenv('CLUSTER_ARG')

    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.{arg}.mongodb.net/?retryWrites=true&w=majority")

    # tasks_db.productCategory
    db_name = settings.db_products
    table_name = settings.products_category_table
    db = client[db_name]
    table = db[table_name]

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


def get_app_settings():
    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')
    arg = os.getenv('CLUSTER_ARG')

    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.{arg}.mongodb.net/?retryWrites=true&w=majority")

    # tasks_db.productCategory
    db_name = settings.db_settings
    table_name = "settings"
    db = client[db_name]
    table = db[table_name]

    setting = list(table.find({}).limit(1))[0]

    return setting


def store_data_products(queue, category):
    while not queue.empty():
        try :
            sellers = queue.get()
            results = {'productCategory': category,
                       'lastUpdate': datetime.timestamp(datetime.now())
                       }
            for seller in sellers:
                if seller['sellerName'] == 'Amazon' :
                    amazon_seller = seller
                    results['productDescription'] = amazon_seller['productDescription']
                    results['productBrand'] = amazon_seller['productBrand']
                    break

            results['sellers'] = sellers

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

            table.insert_one(results)

            client.close()
            print("Item saved in products collection.")
            return True
        except Exception as e:
            logging.exception(e)
            print("Could not save the details to database.")
            return False


def store_data_price(queue, category):
    while not queue.empty():
        try :
            item = queue.get()

            dotenv.load_dotenv()
            user = os.getenv('USER')
            passwd = os.getenv('PASSWD')
            arg = os.getenv('CLUSTER_ARG')
            db_name = settings.db_products
            table_name = settings.product_price_history_table

            # connect to the mongodb database
            client = pymongo.MongoClient(
                f"mongodb+srv://{user}:{passwd}@cluster0.{arg}.mongodb.net/?retryWrites=true&w=majority")

            db = client[db_name]
            table = db[table_name]

            table.insert_one(item)

            client.close()
            print("Item saved in productPriceHistory.")
            return True
        except Exception as e:
            logging.exception(e)
            print("Could not save the details to database.")
            return False


def product_already_in_database(url):
    try:
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

        results = table.count_documents(
            { "sellers.productLink" : url}
        )
        if results:
            return True
        else:
            return False
    except Exception as e:
        logging.exception(e)
        return False


def get_similarity_scores():
    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')
    arg = os.getenv('CLUSTER_ARG')

    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.{arg}.mongodb.net/?retryWrites=true&w=majority")

    db_name = settings.db_settings
    table_name = 'settings'

    db= client[db_name]
    table = db[table_name]

    cursor = list(table.find({}))
    return cursor[0]['similarityScores']

