
import requests
from bs4 import BeautifulSoup
import logging
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

# create a user agent
headers = {"User-Agent":"Mozilla/5.0",
           "Accept-Language": "en-US,en;q=0.9"}


def get_proxy_details():
    """
    Gets a list of proxy ips from website : https://free-proxy-list.net/ .
    :return: Returns a list containing dictionaries of details about recent 10 available IP addresses.
    Each dictionary contains : <br>
    All field values are strings. <br>
    'IP Address' :  Ipv4 address <br>
    'Port' :  port <br>
    'Code'	: Country code <br>
    'Country'	: Country <br>
    'Anonymity'	: 'elite proxy' or 'anonymous' <br>
    'Google' : 'yes' or 'no' <br>
    'Https' : 'yes' or 'no' <br>
    'Last Checked ' : last checked time <br>
    """

    url = "https://free-proxy-list.net/"
    page = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(page.content, "html.parser")
    proxy_ips = []

    table = soup.find('table')
    headers = [header.string for header in table.find('thead').find_all('th')]

    proxies = table.find('tbody').find_all('tr')[0:10]
    for proxy in proxies:
        details = [td.string for td in proxy.find_all('td')]
        info = {}
        for i in range(len(details)):
            info[headers[i]] = details[i]
        proxy_ips.append(info)

    return proxy_ips


def get_proxy():
    proxies = get_proxy_details()
    ips = []            # dict : {'http/s' : '<ip>' }
    for proxy in proxies:
        if proxy['Https'] == 'yes' :
            ips.append({'https' : proxy["IP Address"]+':'+proxy["Port"]})
        else :
            ips.append({'http' : proxy["IP Address"]+':'+proxy["Port"]})

    return ips


def send_request(url):

    """ips = get_proxy()
    for ip in ips:
        try :
            page = requests.get(url, headers=HEADERS, proxies=ip)
            if page.status_code != 200:
                print("Non-200 response received. Trying again...")
            else :
                page = BeautifulSoup(page.content, "html.parser")
                return page
        except requests.exceptions.MissingSchema as e:
            print("Invalid url given.")
            return None
        except Exception as e:
            logging.exception(e)
            continue
        print("Sending request unsuccessful. Stopping the crawler...")
        return None"""
    #print(f"Connecting to url : {url}")
    for i in range(5):
        try:
            page = requests.get(url, headers=headers)
            if page.status_code != 200:
                print("Non-200 response received. Trying again...")
            else:
                page = BeautifulSoup(page.content, "html.parser")
                return page
        except Exception as e:
            logging.exception(e)
            print("Could not connect...")
    print("Connection unsuccessful. Please try again after some time.")


