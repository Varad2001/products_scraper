import logging
logging.basicConfig(filename='amazon-scraper.log', level=logging.DEBUG, format="%(name)s:%(levelname)s:%(asctime)s:%(message)s")
from sklearn.feature_extraction.text import TfidfVectorizer


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