import multiprocessing
import time
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from flask_session import Session
import logging
import threading
from rating import get_all_data, store_user_ratings, delete_item, update_similarity_scores
from crawler import begin_crawling
from extractors.helpers import get_address_by_id
from extractors.updater import update_items


app = Flask(__name__)
app.config['SESSION_TYPE']  = 'filesystem'
Session(app)

@app.route('/begin_crawl', methods=["POST", "GET"])
def start_crawler():

    categoryId = "6338422f02cdaa0d51efb354"

    urls = {'bestbuy' : 'https://www.bestbuy.com/site/speakers/floor-speakers/abcat0205003.c?id=abcat0205003',
            'newegg' : 'https://www.newegg.com/p/pl?N=100008225%20600030002'}

    try :
        #address, category = get_address_by_id(categoryId)
        address = "https://www.amazon.com/s?k=Floorstanding+Speakers&i=electronics&rh=n%3A3236453011&c=ts&qid=1665238284&ts_id=3236453011"
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


@app.route('/get_data', methods=['POST'])
def get_data():
    data = get_all_data('demo', 'products')
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
        session['rating_info']['titleScore'] += data['titleRating']
        session['rating_info']['descriptionScore'] += data['descriptionRating']
        session['rating_info']['imageScore'] += data['imageRating']

        if session['updated_items'] == 100:
            update_similarity_scores(session['rating_info'], 100)
            session['updates_items'] = 0
            session['rating_info'] = {}

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
    update_similarity_scores(session['rating_info'], session['updated_items'])
    session['updates_items'] = 0
    session['rating_info'] = {}



if __name__ == '__main__' :
    app.run(debug=True)
