import pymongo
import os
import dotenv
from bson import ObjectId


def get_all_data(db_name, table_name):

    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')
    arg = os.getenv('CLUSTER_ARG')

    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.{arg}.mongodb.net/?retryWrites=true&w=majority")

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

    db_name = 'ratings'
    table_name = 'userRating'
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

    db_name = 'demo'
    table_name = 'products'
    db = client[db_name]
    table = db[table_name]

    id = ObjectId(id)

    table.delete_one(
        {'_id' : id}
    )


def update_similarity_scores(rating_info, total_updated_items):
    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')
    arg = os.getenv('CLUSTER_ARG')

    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.{arg}.mongodb.net/?retryWrites=true&w=majority")

    db_name = 'ratings'
    table_name = 'settings'
    db = client[db_name]
    table = db[table_name]

    cursor = list(table.find({}))
    scores = cursor[0]
    id = scores['_id']
    del scores['_id']

    correct_titles = rating_info['titleScore']
    correct_descriptions = rating_info['descriptionScore']
    correct_images = rating_info['imageScore']

    correct_titles_avg = correct_titles / total_updated_items * 100
    correct_descriptions_avg = correct_descriptions / total_updated_items * 100
    correct_images_avg = correct_images / total_updated_items * 100

    # if average is less than 50, it means the incorrect items are more than 50%, hence increase the score
    if correct_titles_avg <= 50 :
        scores['titleScore'] += 1
    if correct_descriptions_avg <= 50:
        scores['descriptionScore'] += 1
    if correct_images_avg <= 50:
        scores['imageScore'] += 1

    table.update_one(
        {'_id' : id},
        {'$set' : scores}
    )

    client.close()





