import pymongo
import os
import dotenv
from bson import ObjectId
import settings


def get_all_data():

    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')
    arg = os.getenv('CLUSTER_ARG')

    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.{arg}.mongodb.net/?retryWrites=true&w=majority")

    db_name = settings.db_products
    table_name = settings.products_table
    db = client[db_name]
    table = db[table_name]

    cursor = table.find({})
    data = list(cursor)
    results = []
    for item in data:
        results.append(restructure_document(item))

    return results


def restructure_document(item):
    sellers = item['sellers']
    results = {'sample_item' : None, 'similar_items' : [], 'id' : str(item['_id'])}
    for seller in sellers:
        if seller['sellerName'].lower().strip() == 'amazon':
            results['sample_item'] = seller
        else :
            results['similar_items'].append(seller)

    return results


def store_user_ratings(ratings):
    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')
    arg = os.getenv('CLUSTER_ARG')

    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.{arg}.mongodb.net/?retryWrites=true&w=majority")

    db_name = settings.db_rating
    table_name = settings.userRating_table
    db = client[db_name]
    table = db[table_name]

    id = str(ObjectId(ratings['objId']))
    cursor =list( table.find({'objId' : id}))     # check if the item with the given id exists

    if len(cursor) > 0:                         # if item exists, update the values
        table.update_one(
            { 'objId' : id},
            { '$set' : {'titleRating' : ratings['titleRating'],
                        'descriptionRating' : ratings['descriptionRating'] ,
                        'imageRating' : ratings['imageRating']
                        }}
        )
    else:
        table.insert_one( ratings )
    client.close()


def delete_item(id):
    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')
    arg = os.getenv('CLUSTER_ARG')

    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.{arg}.mongodb.net/?retryWrites=true&w=majority")

    db_name = settings.db_products
    table_name = settings.products_table
    db = client[db_name]
    table = db[table_name]

    id = ObjectId(id)

    table.delete_one(
        {'_id' : id}
    )


def update_similarity_scores():
    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')
    arg = os.getenv('CLUSTER_ARG')

    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.{arg}.mongodb.net/?retryWrites=true&w=majority")

    db_name = settings.db_rating

    db = client[db_name]
    table = db[settings.userRating_table]

    cursor = list(table.find({}).limit(100))
    total_ratings= {'titleRating' : 0 , 'descriptionRating' : 0, 'imageRating' : 0}

    for rating in cursor:
        total_ratings['titleRating'] += int(rating['titleRating'])
        total_ratings['descriptionRating'] += int(rating['descriptionRating'])
        total_ratings['imageRating'] += int(rating['imageRating'])

    db = client[settings.db_settings]
    scores_table = db['settings']
    scores = list(scores_table.find({}).limit(1))[0]
    id = scores['_id']
    similarity_scores = scores['similarityScores']
    if total_ratings['titleRating'] <= 50 :
        similarity_scores['titleScore'] = 1 + int(similarity_scores['titleScore'])
    if total_ratings['descriptionRating'] <= 50:
        similarity_scores['descriptionScore'] = 1 + int(similarity_scores['descriptionScore'])
    if total_ratings['imageRating'] <= 50:
        similarity_scores['imageScore'] = 1 + int(similarity_scores['imageScore'])

    scores_table.update_one(
        {'_id' : id},
        {'$set' : {'similarityScores' : similarity_scores}
         }
    )


def get_data_by_id(id):
    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')
    arg = os.getenv('CLUSTER_ARG')

    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.{arg}.mongodb.net/?retryWrites=true&w=majority")

    db_name = settings.db_products
    table_name = settings.products_table

    db = client[db_name]
    table = db[table_name]

    id = ObjectId(id)

    cursor = list(table.find({'_id' : id}))
    results = []
    for item in cursor:
        results.append(restructure_document(item))

    return results


def get_data_by_brand_name(brand):
    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')
    arg = os.getenv('CLUSTER_ARG')

    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.{arg}.mongodb.net/?retryWrites=true&w=majority")

    db_name = settings.db_products
    table_name = settings.products_table
    db = client[db_name]
    table = db[table_name]

    items = list(table.find({'sellers.productBrand' : brand}))
    results = []
    for item in items:
        results.append(restructure_document(item))

    return results


update_similarity_scores()