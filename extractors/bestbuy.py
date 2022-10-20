import os
import dotenv
import pymongo
from extractors import send_request
import settings
from bson import ObjectId
import logging
logging.basicConfig(filename='scraper.log', level=logging.DEBUG, format="%(name)s:%(levelname)s:%(asctime)s:%(message)s")


def get_bestbuy_url(keywords):
    search_url = "https://www.bestbuy.com/site/searchpage.jsp?st="
    keywords = keywords.replace(' ' , '+')
    url = search_url + keywords
    return url


def next_page_bestbuy(page):

    div = page.find('div', attrs = {'class' : 'footer-pagination'})
    if not div:
        return False

    try :
        next_page_link =div.find('a', attrs = {'class' : 'sku-list-page-next'})
        if next_page_link.get('href'):
            return "https://www.bestbuy.com" + next_page_link.get('href')
        else :
            # print("This is the last page.")
            return False
    except Exception as e:
        logging.exception(e)
        return False


def get_seller_id(name):
    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')
    arg = os.getenv('CLUSTER_ARG')

    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.{arg}.mongodb.net/?retryWrites=true&w=majority")

    try :
        # tasks_db.productCategory
        db_name = settings.db_products
        table_name = settings.products_sellers_table
        db = client[db_name]
        table = db[table_name]

        cursor = table.find({'sellerName' : 'BestBuy'})
        for document in cursor:
            id = document['_id']
            return id
    except Exception as e:
        logging.exception(e)
        print("Failed to retrieve seller if for Bestbuy. Please check your credentials.")


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
        return "NA"

    try :
        return (tag.span.text).replace(',' , '')
    except Exception as e:
        logging.exception(e)
        return "NA"


def get_description(page):
    tag = page.find('div', attrs= {'class' : 'shop-product-description'})
    if not tag:
        return "NA"

    try :
        return tag.div.div.text.strip()
    except Exception as e:
        logging.exception(e)
        return 'NA'


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
        return []

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


def get_shipping_info(page):
    div = page.find("div", attrs= {'class' : 'fulfillment-fulfillment-summary'})
    if not div:
        return "NA"

    try:
        strongs = div.find_all('strong')
        for strong in strongs:
            if 'free shipping' in strong.text.lower():
                return 0
    except Exception as e:
        logging.exception(e)
        return "NA"


def get_discount_info(page):
    tag = page.find('div',  attrs = {'class' : 'pricing-price__regular-price'})
    if not tag:
        return None

    try:
        return tag.text.split('Was')[1].strip()
    except Exception as e:
        logging.exception(e)
        return None


def get_stock_count(page):
    stock = {
        'stockStatus': 1,
        'stockCount': -1
    }
    title = page.find("title")
    if "page not found" in title.text.lower():
        stock['stockStatus'] = -1
        del stock['stockCount']
        return stock

    div = page.find('div', attrs= {'class' : 'fulfillment-add-to-cart-button'})

    try :
        stock_text = div.button.text.strip()
        if 'add to cart' in stock_text.lower():
            stock['stockStatus']  = 1
            del stock['stockCount']
        else :
            stock['stockStatus'] = 0
            del stock['stockCount']
    except Exception as e:
        logging.exception(e)

    return stock


def get_all_details(url):
    page = send_request.send_request(url+ "&intl=nosplash")

    results = {}

    # results['productID'] = ObjectId()
    results['productPrice'] = get_price(page)
    results['userRatings'] = get_rating(page)
    #results['productBrand'] = get_brand(page)
    results['productDescription'] = get_description(page)

    results['sellerID'] = get_seller_id('BestBuy')
    results['sellerName'] = 'BestBuy'
    results['productLink'] = url
    results['productTitle'] = get_title(page)
    results['imageLink'] = get_product_imgs(page)
    results['stockCount'] = get_stock_count(page)
    results['productShippingFee'] = get_shipping_info(page)

    discount = get_discount_info(page)
    if discount:
        results['productPriceType'] = "Discounted"
        results['lastPrice'] = discount
    else :
        results['productPriceType'] = 'Regular'
        results['lastPrice'] = "NA"
    return results



"""url = "https://www.bestbuy.com/site/home-audio-systems/home-theater-systems/abcat0203000.c?id=abcat0203000"
url2 = "https://www.bestbuy.com/site/definitive-technology-descend-dn10-10-sub-3xr-architecture-500w-peak-class-d-amplifier-2-10-bass-radiators-black/6467273.p?skuId=6467273"
url3 = "https://www.bestbuy.com/site/martinlogan-motion-4-90-watt-passive-2-way-center-channel-speaker-gloss-black/5870730.p?skuId=5870730"
url4 = "https://www.bestbuy.com/site/dell-inspiron-27-touch-screen-all-in-one-intel-core-i7-12gb-memory-512gb-ssd-silver/6373025.p?skuId=6373025"
category = "633a9c09fd7e59f8d05c4743"
page = send_request.send_request(url4+"&intl=nosplash")
print(get_stock_count(page))"""

