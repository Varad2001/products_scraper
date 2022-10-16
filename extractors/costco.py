import time

from bs4 import BeautifulSoup
import requests


import extractors.send_request
from extractors.send_request import send_request
from datetime import datetime
import dotenv, os, pymongo
import logging
logging.basicConfig(filename='scraper.log', level=logging.DEBUG, format="%(name)s:%(levelname)s:%(asctime)s:%(message)s")


def get_seller_id(name):
    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')

    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.x6statp.mongodb.net/?retryWrites=true&w=majority")

    # tasks_db.productCategory
    db = client['tasks_db']
    table = db['productSellers']

    cursor = table.find({'sellerName' : 'costco'})
    for document in cursor:
        id = document['_id']
        return id


def find_urls_and_titles_on_page(page):
    title_tags = page.find_all('span' , attrs= {'class' : 'description'})
    results = []
    for tag in title_tags:
        try :
            title = tag.a.text.strip()
            url = tag.a.get('href')
            results.append({'url' : url , 'title' : title})
        except Exception as e:
            print(e)
            continue

    return results


def get_product_id(page):

    tag = page.find('span' , attrs={'automation-id' :"itemNumber"})
    if not tag:
        return None

    try :
        return tag.text.strip()
    except Exception as e:
        logging.exception(e)
        return None


def get_title(page):

    tag = page.find('h1', attrs={"automation-id":"productName"})
    if not tag:
        return None

    try :
        return tag.text.strip()
    except Exception as e:
        logging.exception(e)
        return None


def get_price(page):
    price_tag = page.find('span', attrs={"automation-id":"productPriceOutput"})
    tag = page.find('div', attrs={'id' : 'pull-right-price'})
    print(tag)
    print(price_tag)
    if price_tag:
        price = price_tag.text
        return price
    else :
        return None


def get_ratings(page):
    rating_tag = page.find('div' , attrs={"itemprop" : "ratingValue"})
    tag = page.find('span', attrs={'class' : 'bv-rating'})
    print(tag)
    rating_count = page.find('div', attrs={'class' : 'bv_numReviews_text'})
    print(rating_count, rating_tag)
    if not rating_count or not rating_tag:
        return None

    try:
        return {'Rating' : rating_tag.text.strip(),  'Number_of_ratings' : rating_count.text.
        strip().replace('(','').replace(')','')}
    except Exception as e:
        logging.exception(e)
        return None


def get_brand(page):
    rows = page.find_all('tr')
    for row in rows:
        if row.th and row.td:
            if 'Brand' in row.th:
                return row.td.string
    return None


def get_description(page):
    tag = page.find('div', attrs={'class' : 'product-bullets'})
    if tag:
        l = tag.find_all('li')
        desc = ''
        for i in l:
            try :
                desc += i.string + '\n'
            except :
                continue
        return desc


def get_discount_info(page):
    last_price = page.find('span' , attrs={'class' : 'price-was-data'})
    if last_price:
        return last_price.string
    else :
        return None


def get_shipping_price(page):
    tag = page.find('li', attrs={'class' : 'price-ship'})
    if tag :
        return tag.text.split(' ')[0]


def get_all_details(url, queue, category):
    page = send_request(url)

    seller_details = {}

    results = {}
    #productID, productCategory, favoritedCount, lastUpdate, productBrand, productDescription,
    results['productID'] = get_product_id(page)
    results['productPrice'] =  get_price(page)
    results['productShippingFee'] = get_shipping_price(page)
    results['productCategory'] = category
    results['favoritedCount'] = get_ratings(page)
    results['lastUpdate'] = str(datetime.timestamp(datetime.now()))
    results['productBrand'] = get_brand(page)
    results['productDescription'] = get_description(page)

    seller_details['sellerID'] = get_seller_id('NewEgg')
    seller_details['sellerName'] = 'NewEgg'
    seller_details['productLink'] = url
    seller_details['productTitle'] = get_title(page)

    results['sellers'] = seller_details

    discount = get_discount_info(page)
    if discount :
        results['productPriceType'] = "Discounted"
        results['lastPrice'] = discount


    return results


"""url = "https://www.costco.com/home-theater-systems.html"
url2 = "https://www.costco.com/klipsch-the-fives-speaker%2c-2-pack.product.100800459.html"
url3 = "https://www.costco.com/jbl-bar-5.1-channel-soundbar-multibeam%e2%84%a2-sound-technology.product.100982543.html"
url4 = "https://www.costco.com/klipsch-reference-dolby-atmos-5.0.2-home-theater-system.product.100665767.html"

page = send_request(url4)
time.sleep(1)
#print(find_urls_and_titles_on_page(page))
#print(get_product_id(page))
#print(get_title(page))

print(get_price(page))"""
