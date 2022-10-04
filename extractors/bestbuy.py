from send_request import send_request
from bs4 import BeautifulSoup
import logging
import requests
logging.basicConfig(filename='scraper.log', level=logging.DEBUG, format="%(name)s:%(levelname)s:%(asctime)s:%(message)s")






# create a user agent
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip',
    'DNT': '1',  # Do Not Track Request Header
    'Connection': 'close'
}



url = "https://www.bestbuy.com/site/speakers/floor-speakers/abcat0205003.c?id=abcat0205003&page=2"
page = send_request(url)
print((page.prettify()))
tags = page.find_all('div', attrs={'class' : 'information'})
print(tags)
for tag in tags:
    print(tag.a)


