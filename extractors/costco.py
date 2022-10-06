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

    tag = page.find('span' , attrs={'class' : 'itemNumber'})
    try :
        return tag.span.text.strip()
    except Exception as e:
        print(e)
        return None


def get_title(page):
    title = page.find('h1', attrs= {'class' : 'product-title'})
    if title:
        return title.string
    else :
        print("No title.")
        logging.info("No title.")
        return None


def get_ratings(page):
    rating = page.find('span', attrs={'class' : 'rating-views-num'})
    rating_num = page.find('span', attrs={'class' : 'rating-views-count'})
    if rating_num:
        rating_num = rating_num.string
        rating = rating.string
        return {'Rating' : rating, 'Number_of_ratings' : rating_num}
    else :
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


def get_price(page):
    price_tag = page.find('li', attrs={'class' : 'price-current'})
    if price_tag:
        price = price_tag.strong.string + price_tag.sup.string
        return price
    else :
        return None


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





url = "https://www.costco.com/home-theater-systems.html"
url2 = "https://www.costco.com/klipsch-the-fives-speaker%2c-2-pack.product.100800459.html"

page = send_request(url)
