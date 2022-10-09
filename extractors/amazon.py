import logging
logging.basicConfig(filename='scraper.log', level=logging.DEBUG, format="%(name)s:%(levelname)s:%(asctime)s:%(message)s")
import dotenv
import os
import pymongo
from extractors import send_request


def get_seller_id(name):
    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')

    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.x6statp.mongodb.net/?retryWrites=true&w=majority")

    try :
        # tasks_db.productCategory
        db = client['tasks_db']
        table = db['productSellers']

        cursor = table.find({'sellerName' : 'NewEgg'})
        for document in cursor:
            id = document['_id']
            return id
    except Exception as e:
        logging.exception(e)
        print("Failed to retrieve the seller id for Newegg. Please check your credentials.")


def get_titles_urls_on_page(page):
    print("Getting titles and urls of the sample items from amazon...")
    tags =  page.find_all('a', attrs={'class' : 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})
    results = []
    #print(f"{len(tags)} 'a' tags found on this page.")
    for tag in tags:
        try :
            url = "https://www.amazon.com" + tag.get('href')
            title = tag.span.text
            results.append({'url' : url, 'title' : title})
        except Exception as e:
            logging.exception(e)
            continue
    print(f"{len(results)} sample items found on this amazon page...")
    return results


def get_description(page):
    features = page.find('div', attrs={'id' : 'feature-bullets'})
    if not features:
        return "NA"

    points = features.find_all('span', attrs={'class' : 'a-list-item'})
    desc = ""
    for li in points[1:]:
        try :
            desc += li.text.strip() + "\n"
        except :
            continue

    if desc != "":
        return desc
    else:
        return "NA"


def get_title(page):
    try :
        title = page.find('div', attrs={'id': 'title_feature_div'}).div.h1.span.string
        title = title.strip()
        return title
    except Exception as e:
        return None

def get_price(page):
    price_tag = page.find('span', attrs={'class' : 'a-offscreen'})
    if price_tag == None:
        price = "NA"
    else :
        try :
            price = float(price_tag.string.replace('$', ''))
        except Exception as e:
            logging.exception(e)
            price = 'NA'

    return price


def get_brand(page):
    tag = page.find('div', attrs={'id' : 'productOverview_feature_div'})
    if not tag:
        return None

    trs = tag.find_all('tr')
    for tr in trs:
        try :
            tds = tr.find_all('td')
            if tds[0].text.strip() == 'Brand':
                return tds[1].text.strip()
        except :
            continue
    return None

def get_img_links(page):
    tag = page.find('div', attrs={'id' : 'altImages'})
    if not tag:
        return None

    links = []
    imgs = tag.find_all('img')
    for img in imgs[1:]:
        links.append(img.get('src'))

    return links


def get_ratings(page):
    rating = {}
    stars = page.find('div', attrs={'id': 'averageCustomerReviews'})
    if stars:
        try:
            rating['Stars' ]=stars.i.text.strip()
        except:
            pass

    reviews_count = page.find('span', attrs={'id' : 'acrCustomerReviewText'})
    if reviews_count:
        try:
            rating['Ratings_count'] = reviews_count.text.strip()
        except :
            pass

    return rating


def get_product_id(page):
    tag = page.find('div', attrs={'id' : 'prodDetails'})
    if not tag:
        return None

    trs = tag.find_all('tr')
    for tr in trs:
        try:
            if tr.th.text.strip() == 'ASIN':
                return tr.td.text.strip()
        except:
            continue

    return None


def get_all_details(url):      # queue : reserved for the future use of multiprocessing
    page = send_request.send_request(url)


    results = dict()
    #productID, productCategory, favoritedCount, lastUpdate, productBrand, productDescription,
    results['productID'] = get_product_id(page)
    results['productPrice'] =  get_price(page)
    #results['productCategory'] = category
    results['favoritedCount'] = get_ratings(page)
    results['productBrand'] = get_brand(page)
    results['productDescription'] = get_description(page)

    results['sellerID'] = str(get_seller_id('Amazon'))
    results['sellerName'] = 'Amazon'
    results['productLink'] = url
    results['productTitle'] = get_title(page)
    results['imageLink'] = get_img_links(page)


    return results


"""from extractors import send_request
url = "https://www.amazon.com/JVC-EXOFIELD-Personal-Multi-Channel-Surround/dp/B0899NS7NV/ref=sr_1_19?qid=1665223097&rnid=9977442011&s=electronics&sr=1-19"
page = send_request.send_request(url)


print(get_description(page))"""

