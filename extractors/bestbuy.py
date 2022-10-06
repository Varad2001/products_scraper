import multiprocessing
import os
import dotenv
import pymongo
from datetime import datetime
from extractors.send_request import send_request

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

    cursor = table.find({'sellerName' : 'BestBuy'})
    for document in cursor:
        id = document['_id']
        return id


def get_urls_and_titles(page):
    tags = page.find_all('div', attrs={'class' : 'information'})
    results = []

    for tag in tags:
        try :
            results.append({'url' : "https://www.bestbuy.com" + tag.a.get('href') ,
                            'title' : tag.a.text.strip()})
        except Exception as e:
            logging.exception(e)
            continue

    return results


def get_product_id(page):
    sku = page.find('div', attrs = {'class' : 'sku product-data'})
    if not sku:
        return None

    tags = sku.find_all('span')
    try :
        return tags[1].text
    except Exception as e:
        logging.exception(e)
        return None


def get_title(page):
    tag = page.find('div', attrs = {'class' : 'sku-title'})
    if not tag :
        return None

    try :
        return tag.h1.text
    except Exception as e:
        logging.exception(e)
        return None


def get_price(page):
    tag = page.find('div' , attrs={'class' : 'priceView-hero-price priceView-customer-price'})
    if not tag:
        return None

    try :
        return tag.span.text
    except Exception as e:
        logging.exception(e)
        return None


def get_description(page):
    tag = page.find('div', attrs= {'class' : 'shop-product-description'})
    if not tag:
        return None

    try :
        return tag.div.div.text.strip()
    except Exception as e:
        logging.exception(e)
        return None


def get_brand(page):
    specs = page.find('div', attrs= {'class' : 'shop-specifications'})
    if not specs:
        return None
    lis = specs.find_all('li')
    for li in lis:
        print(li)
        try :
            if li.find('div', attrs={'class' : 'row-title'}).text.strip() == 'Brand':
                return li.find_all('div')[2].text
            else :
                continue
        except Exception as e:
            logging.exception(e)
    return None


def get_product_imgs(page):
    tags = page.find('div', attrs={'class' : 'shop-media-gallery'})
    results = []
    if not tags:
        return None

    imgs = tags.find_all('li')
    for li in imgs:
        try :
            results.append(li.img.get('src'))
        except Exception as e:
            logging.exception(e)
            continue

    return results


def get_rating(page):
    tag = page.find('span', attrs = {'class' : 'ugc-c-review-average font-weight-medium order-1'})
    tag2 = page.find('span' ,attrs={'class' : 'c-reviews order-2'})
    if not tag:
        return None

    try:
        return {'stars' : tag.text.strip(), 'Number of reviews': tag2.text.strip()}
    except Exception as e:
        logging.exception(e)
        return None


def get_discount_info(page):
    tag = page.find('div',  attrs = {'class' : 'pricing-price__regular-price'})
    if not tag:
        return None

    try:
        return tag.text.split('Was')[1].strip()
    except Exception as e:
        logging.exception(e)
        return None


def get_all_details(url,q, category):
    page = send_request(url)

    seller_details = {}

    results = {}

    results['productID'] = get_product_id(page)
    results['productPrice'] = get_price(page)
    #results['productShippingFee'] = get_shipping_price(page)
    results['productCategory'] = category
    results['favoritedCount'] = get_rating(page)
    results['lastUpdate'] = str(datetime.timestamp(datetime.now()))
    results['productBrand'] = get_brand(page)
    results['productDescription'] = get_description(page)

    seller_details['sellerID'] = get_seller_id('BestBuy')
    seller_details['sellerName'] = 'BestBuy'
    seller_details['productLink'] = url
    seller_details['productTitle'] = get_title(page)
    seller_details['imageLink'] = get_product_imgs(page)

    results['sellers'] = seller_details

    discount = get_discount_info(page)
    if discount:
        results['productPriceType'] = "Discounted"
        results['lastPrice'] = discount

    return results



"""url = "https://www.bestbuy.com/site/home-audio-systems/home-theater-systems/abcat0203000.c?id=abcat0203000"
url2 = "https://www.bestbuy.com/site/definitive-technology-descend-dn10-10-sub-3xr-architecture-500w-peak-class-d-amplifier-2-10-bass-radiators-black/6467273.p?skuId=6467273"
url3 = "https://www.bestbuy.com/site/martinlogan-motion-4-90-watt-passive-2-way-center-channel-speaker-gloss-black/5870730.p?skuId=5870730"

category = "633a9c09fd7e59f8d05c4743"

print(get_all_details(url2+"&intl=nosplash", multiprocessing.Queue(),category))"""

