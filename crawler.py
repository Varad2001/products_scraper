import multiprocessing
import threading
from queue import Queue


from extractors import send_request
from similarity_checker import check_similarity

from extractors import newegg, bestbuy
from extractors import amazon
from extractors.helpers import store_data

import logging
logging.basicConfig(filename='scraper.log', level=logging.DEBUG, format="%(name)s:%(levelname)s:%(asctime)s:%(message)s")


def crawl_new_items_from_newegg(queue, url):

    #url = "https://www.newegg.com/p/pl?N=100008225%20600030002"
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
    #url = "https://www.bestbuy.com/site/speakers/floor-speakers/abcat0205003.c?id=abcat0205003"

    new_products = queue

    print("\n-------Getting new items from BestBuy.com ...----")
    while True:
        url = url + "&intl=nosplash"
        page = send_request.send_request(url)
        if not page:
            return
        #print(f"URL : {url}")

        products = bestbuy.get_urls_and_titles(page)
        for product in products:
            new_products.append(product)

        next_page = next_page_bestbuy(page)
        if next_page:
            url = next_page
        else :
            print("This is the last page.")
            break

    print(f"Complete.   {len(new_products)} new items extracted from BestBuy.com.")


def next_page_amazon(page):

    info_tag = page.find('div', attrs={"cel_widget_id" : "UPPER-RESULT_INFO_BAR-0"})
    if info_tag:
        info = info_tag.find('span').string.split(' ')
        try :
            current = info[0].split('-')[1]
            current = current.replace(',',  '')
        except Exception as e:
            print("This is the only page...")
            return 0

        try :
            final = info[2]
            if final == 'over':
                final = info[3].replace(',', '')
        except Exception as e:
            logging.exception(e)
            return 0
        print(current, final)
        try :
            if int(current) == int(final):
                print("This is the last page..")
                return 0
            else :
                return 1
        except Exception as e:
            logging.exception(e)
            return 0


def next_page_bestbuy(page):

    div = page.find('div', attrs = {'class' : 'footer-pagination'})
    if not div:
        return False

    try :
        next_page_link =div.find('a', attrs = {'class' : 'sku-list-page-next'})
        if next_page_link.get('href'):
            return "https://www.bestbuy.com" + next_page_link.get('href')
        else :
            print("This is the last page.")
            return False
    except Exception as e:
        logging.exception(e)
        return False


def crawl_sample_items(sample_url, queue):

    url = sample_url

    item_queue = queue
    page_num = 1
    finished = False
    print("\n-----Crawling sample items from amazon ----")

    while not finished:

        current_url = url + f"&page={page_num}" + f"&ref=sr_pg_{page_num}"
        print(f"Going to url : {current_url}")

        #page = send_request.send_request(current_url)
        page = send_request.send_request(current_url)

        if not page:
            return

        results = amazon.get_titles_urls_on_page(page)

        for item in results:
            item_queue.put(item)

        print("Items extracted : ", item_queue.qsize())

        page_num += 1

        if next_page_amazon(page) == 0:
            finished = True

    print(f"----Finished crawling sample items. Extracted : {item_queue.qsize()}----\n")


def begin_crawling(address, categoryId, urls):

    sample_url = address
    bestbuy_url = urls['bestbuy']
    newegg_url = urls['newegg']

    sample_products = Queue()           # store sample products from amazon
    new_products_newegg = list()        # store new items extracted from Newegg.com
    new_products_bestbuy = list()       # store new items extracted from Bestbuy.com
    items_to_be_inserted = Queue()      # store items that are to be inserted in the database

    sample_crawler = threading.Thread(target=crawl_sample_items, args=(sample_url, sample_products))
    #crawl_sample_items(sample_url, sample_products)
    sample_crawler.start()
    sample_crawler.join()

    #crawl_new_items_from_newegg(new_products_newegg, newegg_url)
    newegg_crawler = threading.Thread(target=crawl_new_items_from_newegg, args=(new_products_newegg, newegg_url))
    newegg_crawler.start()
    newegg_crawler.join()

    #crawl_new_items_from_bestbuy(new_products_bestbuy, bestbuy_url)
    bestbuy_crawler = threading.Thread(target=crawl_new_items_from_bestbuy, args=(new_products_bestbuy, bestbuy_url))
    bestbuy_crawler.start()
    bestbuy_crawler.join()


    print("\n------Starting comparisons....------")
    while not sample_products.empty():
        sample_product = sample_products.get()
        sample_title = sample_product['title']
        sample_data = None
        similar_items = []

        print("\nSample item : ", sample_title)


        for item in new_products_newegg:
            if check_similarity([sample_title, item['title']]) > 0.5:
                if not sample_data:
                    sample_data = amazon.get_all_details(sample_product['url'])

                item_data = newegg.get_all_details(item['url'])
                if not (sample_data['productDescription'] == 'NA' or item_data['productDescription'] == 'NA'):
                    if check_similarity([sample_data['productDescription'], item_data['productDescription']]) > 0.3:
                        print("Similar item found on Newegg.")
                        similar_items.append(item_data)
                else:
                    print("Similar item found on Newegg.")
                    similar_items.append(item_data)


        for item in new_products_bestbuy:
            if check_similarity([sample_title, item['title']]) > 0.5:
                if not sample_data:
                    sample_data = amazon.get_all_details(sample_product['url'])

                item_data = bestbuy.get_all_details(item['url'],categoryId)

                if not (sample_data['productDescription'] == 'NA' or item_data['productDescription'] == 'NA'):
                    if check_similarity([sample_data['productDescription'], item_data['productDescription']]) > 0.3:
                        print("Similar item found on Bestbuy.")
                        similar_items.append(item_data)
                else:
                    print("Similar item found on Bestbuy.")
                    similar_items.append(item_data)

        if len(similar_items) > 0:
            print("Saving similar items...")
            similar_items.append(sample_data)
            items_to_be_inserted.put(similar_items)
            #store_data(items_to_be_inserted, categoryId)
            storing_process = threading.Thread(target=store_data, args=(items_to_be_inserted, categoryId))
            storing_process.start()
            storing_process.join()


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


