class Product:

    def __init__(self, productID, productCategory, favoritedCount, lastUpdate, productBrand, productDescription,
                 sellers):

        self.productId = productID
        self.productCategory = productCategory
        self.favoritedCount = favoritedCount
        self.lastUpdate = lastUpdate
        self.productBrand = productBrand
        self.productDescription = productDescription
        self.sellers = sellers


class Seller:

    def __init__(self, id, name, link, url, title, stock):
        self.sellerID = id
        self.sellerName = name
        self.imageLink = link
        self.productLink = url
        self.productTitle = title
        self.stockCount = stock







