

# database details where products, categories, etc.  are stored
db_products = "tasks_db"
products_table = "products"
products_category_table = "productCategory"
products_sellers_table = "productSellers"


# database details where ratings info is stored
db_rating = "ratings"
settings_table = "settings"
userRating_table = "userRating"


# two user agents to experiment with
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip',
    'DNT': '1',  # Do Not Track Request Header
    'Connection': 'close'
}

headers = {"User-Agent":"Mozilla/5.0",
           "Accept-Language": "en-US,en;q=0.9"}


