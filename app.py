from flask import Flask, jsonify, render_template, request, session, redirect
from flask_session import Session
import threading
from rating import get_data_by_id, store_user_ratings, delete_item, update_similarity_scores, get_data_by_brand_name
from crawler import begin_crawling
import redis_ops
from updater import update_items
from extractors import helpers
import logging

app = Flask(__name__)
app.config['SESSION_TYPE']  = 'filesystem'
Session(app)


@app.route('/begin_crawl', methods=["POST", "GET"])
def start_crawler():

    categoryId = "6338422f02cdaa0d51efb354"

    urls = {'bestbuy' : 'https://www.bestbuy.com/site/speakers/floor-speakers/abcat0205003.c?id=abcat0205003',
            'newegg' : 'https://www.newegg.com/p/pl?N=100008225%20600030002'}

    try :
        address, category = helpers.get_address_by_id(categoryId)

    except Exception as e:
        logging.exception(e)
        print("Could not retrieve category address.")
        return

    if not address:
        print("No category address found for the given id.")
        return jsonify(message="NO category address url found.")

    new_thread = threading.Thread(target=begin_crawling, args=(address, categoryId, urls))
    new_thread.start()

    return jsonify(message="Crawling process started.")


@app.route('/update', methods=["POST", "GET"])
def update():
    print("updating items...")
    new_thread = threading.Thread(target=update_items)
    new_thread.start()

    return jsonify(message="update began...")


@app.route('/index', methods=['POST', 'GET'])
def home():
    return render_template('index.html')


@app.route('/get_data_by_id', methods=['POST'])
def get_data_by_id_value():
    if request.method == "POST":
        id = request.form['id']
        data = get_data_by_id(id)
        session['data'] = data
        session['total_items'] = len(data)
        session['viewed_items'] = 0
        session['updated_items'] = 0
        session['rating_info'] = {
            'titleScore' : 0,
            'descriptionScore' : 0,
            'imageScore' : 0
        }
        return redirect('/get_item')


@app.route('/get_data_by_brand', methods=['POST'])
def get_data_by_brand():
    if request.method == "POST":
        brand = request.form['brand']
        data = get_data_by_brand_name(brand)
        session['data'] = data
        session['total_items'] = len(data)
        session['viewed_items'] = 0
        session['updated_items'] = 0
        session['rating_info'] = {
            'titleScore' : 0,
            'descriptionScore' : 0,
            'imageScore' : 0
        }
        return redirect('/get_item')


@app.route('/get_item', methods=['GET', 'POST'])
def get_item():
    try:
        item = session['data'].pop()
        print(item)
    except IndexError :
        return render_template('final.html')

    data = []
    data.append(item)
    session['viewed_items'] += 1
    return render_template('ratings.html', data = data, id= item['id'])


@app.route('/update_ratings', methods=['POST'])
def update_ratings():
    if request.method == 'POST':
        data = {}
        data['objId'] = request.form['id']
        data['titleRating'] = request.form['titleRating']
        data['descriptionRating'] = request.form['descriptionRating']
        data['imageRating'] = request.form['imageRating']
        try :
            store_user_ratings(data)
        except Exception as e:
            logging.exception(e)
            return redirect('/get_item')

        session['updated_items'] += 1

        r = redis_ops.connect_redis()
        if r:
            redis_ops.increase_value(r, 'count')
            updated_items_till_now = redis_ops.get_value(r, 'count')
            if updated_items_till_now:
                if updated_items_till_now >= 100:
                    new_thread = threading.Thread(target=update_similarity_scores)
                    new_thread.start()
                    print("Updating similarity scores...")

        return redirect('/get_item')


@app.route('/delete_item', methods=["POST"])
def delete():
    if request.method == 'POST':
        id = request.form['id']
        try:
            delete_item(id)
        except Exception as e:
            logging.exception(e)

        return redirect('/get_item')


@app.route('/update_similarity', methods=["POST"])
def update_similarity():
    update_similarity_scores()
    session['updates_items'] = 0
    session['rating_info'] = {}


if __name__ == '__main__' :
    app.run(debug=True)
