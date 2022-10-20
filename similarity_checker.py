
from sklearn.feature_extraction.text import TfidfVectorizer
from PIL import Image
import imagehash
import requests
from io import BytesIO
import settings
from extractors.send_request import  get_proxy
import logging
logging.basicConfig(filename='amazon-scraper.log', level=logging.DEBUG, format="%(name)s:%(levelname)s:%(asctime)s:%(message)s")

def check_similarity(statements:list):
    try :
        corpus = statements

        vect = TfidfVectorizer(min_df=1, stop_words="english")

        tfidf = vect.fit_transform(corpus)
        pairwise_similarity = tfidf * tfidf.T
        return float(pairwise_similarity.toarray()[0][1])
    except Exception as e:
        logging.exception(e)
        print("Could not check the similarity score.")
        return -1


def check_image_similarity(url1, url2):
    """
    Checks how much two images are similar to each other. Returns value ranging from -100 to 100.
    100 means 100% similar,  and -100 means not similar at all.
    :param url1:
    :param url2:
    :return:
    """
    r1 = requests.get(url1, proxies=get_proxy(), headers=settings.headers)
    img1 = Image.open(BytesIO(r1.content))
    r2 = requests.get(url2, proxies=get_proxy(), headers=settings.headers)
    img2 = Image.open(BytesIO(r2.content))
    hash0 = imagehash.average_hash(img1)
    hash1 = imagehash.average_hash(img2)
    similar = abs(hash0 - hash1)
    if similar > 20: similar = 20
    similarity_score = 100 - similar ** 2 * 0.5

    return similarity_score


def images_are_similar(sample_item_imgs_urls, item_imgs_urls, score):

    #print("checking image similarity..")
    total_comparisons = 0       # number total comparisons done
    similar_imgs = 0            # number similar imgs found

    # compare each image of sample item with each image of other  item
    for sample_url in sample_item_imgs_urls:
        for item_url in item_imgs_urls:
            try :
                if check_image_similarity(sample_url, item_url) > score:
                    similar_imgs += 1
                total_comparisons += 1
            except Exception as e:
                continue

    #print(f"Total comparisons : {total_comparisons}   Similar images: {similar_imgs}")
    if not total_comparisons:       # if no comparisons were made, that is, no images were available, return true
        return True

    # calculate the percentage of similar imgs found
    avg_weight = similar_imgs / total_comparisons * 100

    #print(f"Avg weight : {avg_weight}")
    # if the weight is greater than 50, the images are considered as similar
    if avg_weight > 50:
        return True
    else :
        return False


"""from extractors import amazon, bestbuy, send_request
url1 = "https://www.bestbuy.com/site/polk-audio-monitor-xt60-tower-speaker-midnight-black/6477931.p?skuId=6477931"
url2 = "https://www.amazon.com/JVC-EXOFIELD-Personal-Multi-Channel-Surround/dp/B0899NS7NV/ref=sr_1_19?qid=1665223097&rnid=9977442011&s=electronics&sr=1-19"

page1 = send_request.send_request(url1+ "&intl=nosplash")
page2 = send_request.send_request(url2)
img1 = amazon.get_img_links(page2)
print(img1)
img2 = bestbuy.get_product_imgs(page1)
print(img2)

print(images_are_similar(img1, img2, 0))"""

