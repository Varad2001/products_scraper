from flask import Flask, jsonify
import logging
import threading

from crawler import begin_crawling
from extractors.helpers import get_address_by_id
from extractors.updater import update_items


app = Flask(__name__)

@app.route('/begin_crawl', methods=["POST", "GET"])
def start_crawler():

    categoryId = "6338422f02cdaa0d51efb354"

    try :
        address, category = get_address_by_id(categoryId)
    except Exception as e:
        logging.exception(e)
        print("Could not retrieve category address.")
        return

    if not address:
        print("No category address found for the given id.")
        return jsonify(message="NO category address url found.")

    new_thread = threading.Thread(target=begin_crawling, args=(address, id))
    new_thread.start()

    return jsonify(message="Crawling process started.")


@app.route('/update', methods=["POST", "GET"])
def update():
    print("updating items...")
    new_thread = threading.Thread(target=update_items)
    new_thread.start()

    return jsonify(message="update began...")


if __name__ == '__main__' :
    app.run()