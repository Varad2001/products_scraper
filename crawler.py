from queue import Queue

from extractors.send_request import send_request
from similarity_checker import check_similarity

from extractors import newegg, bestbuy
from extractors import amazon
from extractors.helpers import get_details_from_newegg_and_store, get_details_from_bestbuy_and_store

import logging
logging.basicConfig(filename='scraper.log', level=logging.DEBUG, format="%(name)s:%(levelname)s:%(asctime)s:%(message)s")


def crawl_new_items_from_newegg(queue):

    url = "https://www.newegg.com/p/pl?N=100008225%20600030002"
    page = send_request(url)

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
        print("Url : ", current_url)

        page = send_request(current_url)
        if not page:
            continue

        products = newegg.find_urls_and_titles_on_page(page)

        for product in products:
            new_products.append(product)

        page_num += 1

    print(f"Complete.   {len(new_products)} new items extracted from Newegg.com.")


def crawl_new_items_from_bestbuy(queue):
    url = "https://www.bestbuy.com/site/speakers/floor-speakers/abcat0205003.c?id=abcat0205003"

    new_products = queue

    print("\n-------Getting new items from BestBuy.com ...----")
    while True:
        page = send_request(url)
        if not page:
            return
        print(f"URL : {url}")

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


def next_page_newegg(page):

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


def next_page_bestbuy(page):

    div = page.find('div', attrs = {'class' : 'footer-pagination'})
    if not div:
        return False

    try :
        next_page_link =div.find('a', attrs = {'class' : 'sku-list-page-next'})
        if  next_page_link:
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

        current_url = url + f"&page={page_num}"
        #print(f"Going to url : {current_url}")

        page = send_request(current_url)

        if not page:
            return

        results = amazon.get_titles_urls_on_page(page)

        for item in results:
            item_queue.put(item)

        print("Items extracted : ", item_queue.qsize())

        page_num += 1

        if next_page_newegg(page) == 0:
            finished = True

    print("----Finished crawling sample items.----\n")


def begin_crawling(address, categoryId):

    sample_url = address

    sample_products = Queue()           # store sample products from amazon
    new_products_newegg = list()        # store new items extracted from Newegg.com
    new_products_bestbuy = list()       # store new items extracted from Bestbuy.com
    items_to_be_inserted = Queue()      # store items that are to be inserted in the database

    crawl_sample_items(sample_url, sample_products)

    crawl_new_items_from_newegg(new_products_newegg)
    crawl_new_items_from_bestbuy(new_products_bestbuy)

    print("\n------Starting comparisons....------")
    while not sample_products.empty():
        sample_product = sample_products.get()
        sample_title = sample_product['title']

        print("\nSample item : ", sample_title)

        print("Comparing item Newegg.com...")
        for item in new_products_newegg:
            if check_similarity([sample_title, item['title']]) > 0.5:
                print("Similar product found on Newegg : ", item['title'])
                if get_details_from_newegg_and_store(item['url'], items_to_be_inserted, categoryId):
                    print("Item stored successfully.")
                else:
                    print("Could not save item.")
        print("Comparison with Newegg complete.")

        print("Comparing item with BestBuy...")
        for item in new_products_bestbuy:
            if check_similarity([sample_title, item['title']]) > 0.5:
                print("Similar product found on Bestbuy : ", item['title'])
                if get_details_from_bestbuy_and_store(item['url'], items_to_be_inserted, categoryId):
                    print("Item stored successfully.")
                else:
                    print("Could not save item.")
        print("Comparison with Bestbuy complete.")

    print("\n-------Crawling finished.--------")


"""
id = "6338422f02cdaa0d51efb354"
begin_crawling(id)

url = "https://www.amazon.com/s?i=electronics-intl-ship&bbn=16225009011&rh=n%3A667846011%2Cn%3A172563%2Cn%3A3236453011&dc&ds=v1%3AJv2xBSfZoPwFQeY9m2RlhnlAXk6zLqOsRxX58kxLWxA&qid=1664904357&rnid=172563&ref=sr_nr_n_4&page=2"
url2 = "https://www.amazon.com/s?i=electronics-intl-ship&bbn=16225009011&rh=n%3A667846011%2Cn%3A9977442011%2Cn%3A12097481011&dc&ds=v1%3Acnj5e5wMF7gzPrL54jV8emwqe65y1czvO%2FYKWIgk5bI&qid=1664904642&rnid=9977442011&ref=sr_nr_n_2"
url3 = "https://www.amazon.com/s?i=electronics-intl-ship&bbn=16225009011&rh=n%3A667846011%2Cn%3A9977442011%2Cn%3A12097481011%2Cn%3A3236452011&dc&page=3&qid=1664904691&rnid=12097481011&ref=sr_pg_3"
page = send_request(url3)

print(next_page(page))"""