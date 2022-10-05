from bs4 import BeautifulSoup
import requests
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

    cursor = table.find({'sellerName' : 'NewEgg'})
    for document in cursor:
        id = document['_id']
        return id



def find_urls_and_titles_on_page(page):
    title_tags = page.find_all('a', attrs={'class' : 'item-title'})
    results = []

    for title in title_tags:
        try :
            results.append({'url' : title.get('href') , 'title' : title.text})
        except Exception as e:
            logging.exception(e)
            continue

    return results


def get_product_id(page):

    #id = page.find('span', attrs = {'class' : 'product-item-number'})
    id = page.find('em')
    if id:
        return id.string
    else :
        print("No product id found.")
        logging.info("No product id.")
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


def get_product_images(page):
    tags = page.find_all('img' , attrs= {'class' : 'product-view-img-original'})
    links = []
    for tag in tags:
        try :
            links.append(tag.get('src'))
        except Exception as e:
            logging.exception(e)
            print(e)
            continue

    return links


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
    seller_details['imageLink'] = get_product_images(page)

    results['sellers'] = seller_details

    discount = get_discount_info(page)
    if discount :
        results['productPriceType'] = "Discounted"
        results['lastPrice'] = discount


    return results


"""url = "https://www.newegg.com/p/pl?N=100008225%20600030002"
url2 = "https://www.newegg.com/cerwin-vega-xls-215/p/0S6-00AA-00006?quicklink=true"
url3= "https://www.newegg.com/polk-audio-300367-14-00-005/p/N82E16886290064?quicklink=true"
url4 = "https://www.newegg.com/creality-ender-3-v2-black/p/288-00DY-00001"
page = send_request(url2)

print(get_product_images(page))
print(get_product_id(page))
print(get_title(page))
print(get_ratings(page))
print(get_brand(page))
print(get_description(page))
print(get_price(page))
print(get_discount_info(page))
print(get_shipping_price(page))
print(find_urls_and_titles_on_page(page))"""

