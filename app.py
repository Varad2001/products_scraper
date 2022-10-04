from flask import Flask, jsonify
from crawler import begin_crawling
from extractors.helpers import get_address_by_id
from extractors.updater import update_items
import threading

app = Flask(__name__)

@app.route('/begin_crawl', methods=["POST", "GET"])
def start_crawler():

    id = "6338422f02cdaa0d51efb354"

    address, category = get_address_by_id(id)
    if not address:
        print("No category address found for the given id.")
        return jsonify(message="NO category address url found.")

    new_thread = threading.Thread(target=begin_crawling, args=(address, category))
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