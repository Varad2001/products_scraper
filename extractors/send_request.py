
import requests
from bs4 import BeautifulSoup
import settings
import logging
logging.basicConfig(filename='scraper.log', level=logging.DEBUG, format="%(name)s:%(levelname)s:%(asctime)s:%(message)s")


# get proxy from scraperapi
def get_proxy():
    proxies =  {
  "http": "http://scraperapi.render=true.country_code=us:e64ba69d552fdfcc057457832473e72b@proxy-server.scraperapi.com:8001"
    }

    return proxies


# this function can be used if the get_proxy() function does not work for any reason
def get_proxy_alternate():
    username = "geonode_Pctp7P4IXd-country-US"
    password = "39453242-2f35-4083-8a5e-d11a0b68ac36"
    GEONODE_DNS = "rotating-residential.geonode.com:10000"
    proxy = {"http": "http://{}:{}@{}".format(username, password, GEONODE_DNS)}
    return proxy


def send_request(url):
    try :
        proxy = get_proxy()
    except Exception as e:
        print("Connecting to proxy ip failed. Please check if you have proper proxy services enabled and that you have "
              "entered right credentials.")
        print(e)
        return
    try :
        r = requests.get(url, proxies=proxy, headers=settings.headers)
        page = BeautifulSoup(r.content, "html.parser")
        return page
    except Exception as e:
        print("Sending request failed to url : ", url)
        print(e)
        return False



