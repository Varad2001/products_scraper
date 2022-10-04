
from queue import Queue
import bson.errors
from cachetools import FIFOCache
from extractors.newegg import find_urls_and_titles_on_page
from extractors import amazon
from extractors.send_request import send_request
from similarity_checker import check_similarity
from queue import Queue
from extractors.helpers import get_address_by_id, get_details_and_store
import dotenv, os
import pymongo
import threading
from bson import ObjectId
import logging
logging.basicConfig(filename='scraper.log', level=logging.DEBUG, format="%(name)s:%(levelname)s:%(asctime)s:%(message)s")



def crawl_new_items(queue):

    sample_title = "Klipsch RP-280F Reference Premiere Floorstanding Speaker With Dual 8' Cerametallic Cone Woofers - Each (Cherry)"
    url = "https://www.newegg.com/p/pl?N=100008225%20600030002"
    url2 = "https://www.newegg.com/todays-deals?cm_sp=Head_Navigation-_-Under_Search_Bar-_-Today%27s+Best+Deals&icid=720202"
    page = send_request(url)

    page_num = 1

    new_products = queue

    next_page = page.find('div', attrs={'class' : 'list-tools-bar'})
    total_pages = next_page.strong.text.split('/')[1]
    total_pages = int(total_pages)
    print("Getting items from NewEgg.com ....")
    while page_num <= total_pages:
        current_url = f"{url}&page={page_num}"
        print("Url : ", current_url)

        page = send_request(current_url)

        products = find_urls_and_titles_on_page(page)

        for product in products:
            new_products.append(product)

        page_num += 1

    print(f"Complete.   {len(new_products)} new items extracted from Newegg.com.")


def crawl_sample_items(sample_url, queue):
    #url = "https://www.amazon.com/s?i=electronics-intl-ship&bbn=16225009011&rh=n%3A667846011%2Cn%3A172563%2Cn%3A3236453011&dc&ds=v1%3AEFY5sTMk3Z4ZRYMmgxKXMZnGREWYV07tNThsyh91Lec&qid=1664860424&rnid=172563&ref=sr_nr_n_4"
    url = sample_url

    q = queue
    page_num = 1
    finished = False
    print("Crawling sample items from amazon ----")

    while not finished:

        current_url = url + f"&page={page_num}"
        print(f"Going to url : {current_url}")

        page = send_request(current_url)
        results = amazon.get_titles_urls_on_page(page)
        for item in results:
            q.put(item)

        print("Items extracted : ", q.qsize())
        page_num += 1

        if next_page(page) == 0:
            finished = True

    print("finished crawling sample items.")


def next_page(page):

    info_tag = page.find('div', attrs={"cel_widget_id" : "UPPER-RESULT_INFO_BAR-0"})
    if info_tag:
        info = info_tag.find('span').string.split(' ')
        try :
            current = info[0].split('-')[1]
        except Exception as e:
            print("This is the only page...")
            return 0
        final = info[2]
        if int(current) == int(final):
            print("This is the last page..")
            return 0
        else :
            return 1


def begin_crawling(address, category):

    #sample_url, category = get_address_by_id(category_id)
    sample_url = address
    category = category

    sample_products = Queue()
    new_products = list()
    items_to_be_inserted = Queue()

    crawl_sample_items(sample_url, sample_products)
    crawl_new_items(new_products)

    while not sample_products.empty():
        sample_product = sample_products.get()
        sample_title = sample_product['title']
        print("Sample item : ", sample_title)

        for item in new_products:
            if check_similarity([sample_title, item['title']]) > 0.5:
                print("Similar product found : ", item['title'])
                if get_details_and_store(item['url'], items_to_be_inserted, category):
                    print("Item stored successfully.")
                else:
                    print("Could not save item.")

    print("Crawling finished.")


"""
id = "6338422f02cdaa0d51efb354"
begin_crawling(id)

url = "https://www.amazon.com/s?i=electronics-intl-ship&bbn=16225009011&rh=n%3A667846011%2Cn%3A172563%2Cn%3A3236453011&dc&ds=v1%3AJv2xBSfZoPwFQeY9m2RlhnlAXk6zLqOsRxX58kxLWxA&qid=1664904357&rnid=172563&ref=sr_nr_n_4&page=2"
url2 = "https://www.amazon.com/s?i=electronics-intl-ship&bbn=16225009011&rh=n%3A667846011%2Cn%3A9977442011%2Cn%3A12097481011&dc&ds=v1%3Acnj5e5wMF7gzPrL54jV8emwqe65y1czvO%2FYKWIgk5bI&qid=1664904642&rnid=9977442011&ref=sr_nr_n_2"
url3 = "https://www.amazon.com/s?i=electronics-intl-ship&bbn=16225009011&rh=n%3A667846011%2Cn%3A9977442011%2Cn%3A12097481011%2Cn%3A3236452011&dc&page=3&qid=1664904691&rnid=12097481011&ref=sr_pg_3"
page = send_request(url3)

print(next_page(page))"""