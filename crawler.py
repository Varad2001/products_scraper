from queue import Queue

from extractors import send_request
from similarity_checker import check_similarity, images_are_similar

from extractors import newegg, bestbuy
from extractors import amazon
from helpers import store_data_products,store_data_price, product_already_in_database, get_similarity_scores, get_important_text
from datetime import datetime
from bson import ObjectId
import logging
logging.basicConfig(filename='scraper.log', level=logging.DEBUG, format="%(name)s:%(levelname)s:%(asctime)s:%(message)s")


def crawl_new_items_from_newegg(queue, url):

    page = send_request.send_request(url)

    if not page:
        return

    page_num = 1

    new_products = queue

    try :
        next_page = page.find('div', attrs={'class' : 'list-tools-bar'})
        total_pages = next_page.strong.text.split('/')[1]
        total_pages = int(total_pages)
    except Exception as e:
        print("Could not extract the count of results")
        return

    print("\n-------Getting items from NewEgg.com ....------")
    while page_num <= total_pages:
        current_url = f"{url}&page={page_num}"
        #print("Url : ", current_url)

        page = send_request.send_request(current_url)
        if not page:
            continue

        products = newegg.find_urls_and_titles_on_page(page)

        for product in products:
            new_products.append(product)

        page_num += 1

    print(f"Complete.   {len(new_products)} new items extracted from Newegg.com.")


def crawl_new_items_from_bestbuy(queue, url):

    new_products = queue

    print("\n-------Getting new items from BestBuy.com ...----")
    while True:
        url = url + "&intl=nosplash"
        page = send_request.send_request(url)
        if not page:
            return
        # print(f"URL : {url}")

        products = bestbuy.get_urls_and_titles(page)
        for product in products:
            new_products.append(product)

        next_page = bestbuy.next_page_bestbuy(page)
        if next_page:
            url = next_page
        else :
            print("This is the last page.")
            break

    print(f"Complete.   {len(new_products)} new items extracted from BestBuy.com.")


def crawl_sample_items(sample_url, queue):

    url = sample_url

    item_queue = queue
    page_num = 1
    finished = False

    print("\n-----Crawling sample items from amazon ----")

    while not finished:

        current_url = url + f"&page={page_num}" + f"&ref=sr_pg_{page_num}"
        print(f"Going to url : {current_url}")

        page = send_request.send_request(current_url)

        if not page:
            return

        results = amazon.get_titles_urls_on_page(page)

        for item in results:
            item_queue.put(item)

        print("Items extracted : ", item_queue.qsize())

        page_num += 1

        if amazon.next_page_amazon(page) == 0:
            finished = True

    print(f"----Finished crawling sample items. Extracted : {item_queue.qsize()}----\n")


def begin_crawling(address, categoryId):

    sample_url = address

    sample_products = Queue()           # store sample products from amazon
    new_products_newegg = list()        # store new items extracted from Newegg.com
    new_products_bestbuy = list()       # store new items extracted from Bestbuy.com
    items_to_be_inserted = Queue()      # store items that are to be inserted in the table prodcuts
    items_to_be_inserted_prices = Queue()   # store documents to be inserted in table 'productHistory'

    # get similarity scores
    try:
        similarity_scores = get_similarity_scores()
    except Exception as e:
        print("Could not fetch similarity scores.")
        print(e)
        return

    # extract sample items from amazon
    crawl_sample_items(sample_url, sample_products)

    print("-----Processing each sample item...------")
    while not sample_products.empty():
        sample_product = sample_products.get()

        if product_already_in_database(sample_product['url']):
            print("Product already in database...")
            continue

        sample_title = sample_product['title']
        sample_data = None
        similar_items = []

        print("\nSample item : ", sample_title)

        # extract important part of the title
        try :
            keywords = get_important_text(sample_title)
            keywords = keywords[0] + ' ' + keywords[1]
        except Exception as e:
            print("Could not extract important parts from title. Using sample title as keywords...")
            keywords = sample_title

        # generate urls for searching this keyword in the search boxes of other sites
        try:
            bestbuy_url = bestbuy.get_bestbuy_url(keywords)
            newegg_url = newegg.get_newegg_url(keywords)
        except Exception as  e:
            print("Could not generate urls for searching due to the following error.")
            print(e)
            return

        # extract items from search results
        crawl_new_items_from_newegg(new_products_newegg, newegg_url)
        crawl_new_items_from_bestbuy(new_products_bestbuy, bestbuy_url)

        # now the items have been extracted,
        current_item_newegg = { 'productPrice' : 'NA' , 'productLink' : None}
        for item in new_products_newegg:

            if check_similarity([sample_title, item['title']]) > int(similarity_scores['titleScore']) / 100:
                #print("Similar titles...")
                if not sample_data:
                    sample_data = amazon.get_all_details(sample_product['url'])

                item_data = newegg.get_all_details(item['url'])

                if not current_item_newegg['productPrice'] == 'NA':
                    if item_data['productPrice'] == 'NA' :
                        continue
                    else:
                        if float(item_data['productPrice']) >= float(current_item_newegg['productPrice']) :
                            continue

                if not (sample_data['productDescription'] == 'NA' or item_data['productDescription'] == 'NA'):
                    if check_similarity([sample_data['productDescription'], item_data['productDescription']]) > \
                            int(similarity_scores['descriptionScore']) / 100:
                        #print("similar descriptions...")

                        image_score = int(similarity_scores['imageScore']) * 2 - 100
                        if images_are_similar(sample_data['imageLink'], item_data['imageLink'], image_score):
                            print("Similar item found on Newegg.")
                            current_item_newegg = item_data
                else:
                    print("Similar item found on Newegg.")
                    current_item_newegg = item_data

        if len(new_products_newegg) > 0:
            if current_item_newegg['productLink'] :
                similar_items.append(current_item_newegg)



        current_item_bestbuy = {'productPrice': 'NA' , 'productLink' : None}
        for item in new_products_bestbuy:

            if check_similarity([sample_title, item['title']]) > int(similarity_scores['titleScore']) / 100:
                if not sample_data:
                    sample_data = amazon.get_all_details(sample_product['url'])

                item_data = bestbuy.get_all_details(item['url'])

                if not current_item_bestbuy['productPrice'] == 'NA':
                    if item_data['productPrice'] == 'NA' :
                        continue
                    else:
                        if float(item_data['productPrice']) >= float(current_item_bestbuy['productPrice']) :
                            continue

                if not (sample_data['productDescription'] == 'NA' or item_data['productDescription'] == 'NA'):
                    if check_similarity([sample_data['productDescription'], item_data['productDescription']]) > \
                            int(similarity_scores['descriptionScore']) / 100:

                        image_score = similarity_scores['imageScore'] * 2 - 100
                        if images_are_similar(sample_data['imageLink'], item_data['imageLink'], image_score):
                            print("Similar item found on Bestbuy.")
                            current_item_bestbuy = item_data
                else:
                    print("Similar item found on Bestbuy.")
                    current_item_bestbuy = item_data

        if len(new_products_bestbuy) > 0:
            if current_item_bestbuy['productLink']:
                similar_items.append(current_item_bestbuy)


        if len(similar_items) > 0:
            print("Saving similar items...")
            similar_items.append(sample_data)
            obj_id = ObjectId()

            # store in 'priceHistory' collection
            for item in similar_items:
                document = {
                    'productID' : obj_id,
                    'sellerID' : item['sellerID'],
                    'priceUpdateTime' : datetime.timestamp(datetime.now()),
                    'productPrice' : item['productPrice'],
                    'productShippingFee' : item['productShippingFee'],
                    'productPriceType' :  item['productPriceType']
                }
                # store discount if available
                if item['productPriceType'] == 'Discounted':
                    document['lastPrice'] = item['lastPrice']
                    del item['lastPrice']

                items_to_be_inserted_prices.put(document)
            store_data_price(items_to_be_inserted_prices, categoryId)

            # store in 'products' collection
            for item in similar_items:          # remove attributes not to be stored in 'products'
                del item['productPrice']
                del item['productShippingFee']
                if item['sellerName'] != 'Amazon':
                    del item['productDescription']

            items_to_be_inserted.put(similar_items)
            store_data_products(items_to_be_inserted, categoryId, obj_id)



    print("\n-------Crawling finished.--------")


"""
id = "6338422f02cdaa0d51efb354"
begin_crawling(id)

url = "https://www.amazon.com/s?i=electronics-intl-ship&bbn=16225009011&rh=n%3A667846011%2Cn%3A172563%2Cn%3A3236453011&dc&ds=v1%3AJv2xBSfZoPwFQeY9m2RlhnlAXk6zLqOsRxX58kxLWxA&qid=1664904357&rnid=172563&ref=sr_nr_n_4&page=2"
url2 = "https://www.amazon.com/s?i=electronics-intl-ship&bbn=16225009011&rh=n%3A667846011%2Cn%3A9977442011%2Cn%3A12097481011&dc&ds=v1%3Acnj5e5wMF7gzPrL54jV8emwqe65y1czvO%2FYKWIgk5bI&qid=1664904642&rnid=9977442011&ref=sr_nr_n_2"
url3 = "https://www.amazon.com/s?i=electronics-intl-ship&bbn=16225009011&rh=n%3A667846011%2Cn%3A9977442011%2Cn%3A12097481011%2Cn%3A3236452011&dc&page=3&qid=1664904691&rnid=12097481011&ref=sr_pg_3"
page = send_request(url3)

print(next_page(page))
url = "https://www.amazon.com/s?k=Home+Theater+Systems&i=electronics&rh=n%3A281056&c=ts&qid=1665155417&ts_id=281056"
crawl_sample_items(url, multiprocessing.Queue())"""


