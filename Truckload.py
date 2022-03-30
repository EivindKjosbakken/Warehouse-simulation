

import math
from Product import Product


class Truckload():
    def __init__(self, name : str, maxCapacity : int):
        self.name = name
        self.load =dict() # key is Product object, and the value is the amount of the product in the truckload
        self.maxCapacity = maxCapacity


    def getName(self):
        return self.name
    def getLoad(self):
        return self.load
    def setProducts(self, products : list):
        self.load = products
    def setName(self, name : str):
        self.name = name
    def getMaxCapacity(self):
        return self.maxCapacity
    def setMaxCapacity(self, maxCapacity : int):
        if (maxCapacity>=1):
            self.maxCapacity = maxCapacity
            return True
        print("maxCapacity must be bigger than 1")
        return False

    def get40Weight(self):
        """returns first product it finds, and an amount so its less than or equal to 40"""
        for product, amount in self.load.items():
            amountToGet = math.floor(40/product.getWeight())
            if amount>= amountToGet: #if truckload has enough
                self.removeProducts(product, amountToGet)
                return (product, amountToGet)
            self.removeProducts(product, amount)
            return (product, amount)

    def getTotalWeight(self):
        totalWeight = 0
        for productObject, amount in self.load.items():
            totalWeight+= (productObject.getWeight() * amount)
        return totalWeight
             
    def addProduct(self, product : Product):
        if ( (self.getTotalWeight() + product.getWeight()) > self.maxCapacity):
            print("Weight limit is reached, can't add product", product.getName())
            return False 
        if (isinstance(product, Product)):
            if (product in self.load.keys()):
                amount = self.load[product]
                amount += 1
                self.load[product] = amount 
            else: 
                self.load[product] = 1
            return True
        print("Product must be product type to add")
        return False

    def removeProducts(self, product : Product, amount):
        if product in self.load.keys():
            productAmount = self.load[product]
            if (amount<=productAmount):
                productAmount-=amount
                self.load[product] = productAmount
            else:
                print("do not have that many products in truckload")

    def printTruckload(self):
        """print truckload out nicely"""
        print("The following products and amount are in the truckload")
        for product, amount in self.load.items():
            print(product.getName(), "which weighs", product.getWeight(), ", there is", amount, "units of the porudct")