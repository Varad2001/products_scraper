import logging
logging.basicConfig(filename='amazon-scraper.log', level=logging.DEBUG, format="%(name)s:%(levelname)s:%(asctime)s:%(message)s")
from sklearn.feature_extraction.text import TfidfVectorizer
from PIL import Image
import imagehash
import requests
from io import BytesIO


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
    r1 = requests.get(url1)
    img1 = Image.open(BytesIO(r1.content))
    r2 = requests.get(url2)
    img2 = Image.open(BytesIO(r2.content))
    hash0 = imagehash.average_hash(img1)
    hash1 = imagehash.average_hash(img2)
    similar = abs(hash0 - hash1)
    print(similar)
    if similar > 20: similar = 20
    similarity_score = 100 - similar ** 2 * 0.5

    return similarity_score


"""url = "https://www.amazon.com/SanDisk-2TB-Extreme-Portable-SDSSDE81-2T00-G25/dp/B08GV4YYV7?th=1"
url3 = 'https://www.amazon.com/AT-DL72219-2-Handset-Cordless-Unsurpassed/dp/B088B1Y75K/ref=sr_1_46?keywords=phone&qid' \
       '=1664287424&qu=eyJxc2MiOiI5LjIwIiwicXNhIjoiOC43MCIsInFzcCI6IjcuOTEifQ%3D%3D&sr=8-46&th=1 '
sample = Product(url)
sample.get_title()
sample.get_description()

item = Product(url)
new = is_similar(sample, item)
if new != False:
    print(new.get_info())"""