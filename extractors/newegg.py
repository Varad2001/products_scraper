
import dotenv
import os
import pymongo
import settings
from bson import ObjectId
from extractors import send_request
import logging
logging.basicConfig(filename='scraper.log', level=logging.DEBUG, format="%(name)s:%(levelname)s:%(asctime)s:%(message)s")


def get_newegg_url(keywords):
    search_url = "https://www.newegg.com/p/pl?d="
    keywords = keywords.replace(' ' , '+')
    url = search_url + keywords
    return url


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

        cursor = table.find({'sellerName' : 'NewEgg'})
        for document in cursor:
            id = document['_id']
            return id
    except Exception as e:
        logging.exception(e)
        print("Failed to retrieve the seller id for Newegg. Please check your credentials.")


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
        try:
            rating_num = rating_num.string
            rating = rating.string
            return {'Rating' : rating, 'Number_of_ratings' : rating_num}
        except:
            return None
    else :
        return None


def get_brand(page):
    rows = page.find_all('tr')
    for row in rows:
        try:
            if row.th and row.td:
                if 'Brand' in row.th:
                    return row.td.string
        except:
            continue
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

    return "NA"


def get_price(page):
    price_tag = page.find('li', attrs={'class' : 'price-current'})
    if price_tag:
        try:
            price = price_tag.strong.string + price_tag.sup.string
            return price.replace(',', '')
        except:
            return "NA"
    else :
        return "NA"


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
    else :
        return 0


def get_product_images(page):
    div = page.find('div' , attrs={'class' : 'swiper-gallery-thumbs'})
    if not div:
        return []
    tags = div.find_all('img' , attrs= {'class' : 'product-view-img-original'})
    links = []
    for tag in tags:
        try :
            links.append(tag.get('src'))
        except Exception as e:
            logging.exception(e)
            print(e)
            continue

    return links


def get_stock_count(page):
    stock = {
        'stockStatus': 1,
        'stockCount': -1
    }
    title = page.find('title')
    if 'page not found' in title.text.lower():
        stock['stockStatus'] = -1
        del stock['stockCount']

    div = page.find("div", attrs=  {'class' : 'product-inventory'})
    try :
        stock_text = div.strong.text
        if 'in stock' in stock_text.lower():
            stock['stockStatus'] = 1
            del stock['stockCount']
        else:
            stock['stockStatus'] = 0
            del stock['stockCount']
    except Exception as e:
        logging.exception(e)

    return stock


def get_all_details(url):
    page = send_request.send_request(url)

    results = dict()

    # results['productID'] = ObjectId()
    results['productPrice'] =  get_price(page)
    results['productShippingFee'] = get_shipping_price(page)
    results['userRatings'] = get_ratings(page)
    #results['productBrand'] = get_brand(page)
    results['productDescription'] = get_description(page)

    results['sellerID'] = get_seller_id('NewEgg')
    results['sellerName'] = 'NewEgg'
    results['productLink'] = url
    results['productTitle'] = get_title(page)
    results['imageLink'] = get_product_images(page)
    results['stockCount'] = get_stock_count(page)
    results['productShippingFee'] = get_shipping_price(page)

    discount = get_discount_info(page)
    if discount :
        results['productPriceType'] = "Discounted"
        results['lastPrice'] = discount
    else :
        results['productPriceType'] = 'Regular'
        results['lastPrice'] = "NA"
    return results


"""url = "https://www.newegg.com/p/pl?N=100008225%20600030002"
url2 = "https://www.newegg.com/cerwin-vega-xls-215/p/0S6-00AA-00006?quicklink=true"
url3= "https://www.newegg.com/polk-audio-300367-14-00-005/p/N82E16886290064?quicklink=true"
url4 = "https://www.newegg.com/creality-ender-3-v2-black/p/288-00DY-00001"
page = send_request.send_request(url3)


print(get_stock_count(page))"""

