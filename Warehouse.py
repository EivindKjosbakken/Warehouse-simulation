
from tracemalloc import start
from turtle import st
from zoneinfo import available_timezones
from Cell import Cell
from CustomerOrder import CustomerOrder
from Product import Product
from Truckload import Truckload
from tkinter import * 


import math



class Warehouse():
    def __init__(self):
        self.cells = [] # a list of cell objects with all cells in the warehouse, will be 2d (one list in cells for each row of the warehouse)
        self.robots = [] # a list of robot objects
        self.currentLoad = [] #a list with elements (product, amount), that comes from truck loads, the load is to be picked up by robots and put in shelves
        self.currentTruckload = None
        self.currentCustomerOrder = None
        self.truckloads = []
        self.customerOrders = []


#getters and setters:
    def getCells(self):
        return self.cells
    def getCells1D(self):
        """returns a 1D array of the cells (instead of 2D)"""
        allCells = []
        for row in self.cells:
            for cell in row:
                allCells.append(cell)
        return allCells
    def getVerticalCells(self):
        """get all cells with vertical arrows, used by robot to calculate route"""
        verticalCells = []
        for row in self.cells:
            for cell in row: 
                if cell.getCellType() == "moveDown" or cell.getCellType() == "moveUp":
                    verticalCells.append(cell)
        return verticalCells
    def getCellByCoordinates(self, x, y):
        for row in self.cells:
            for cell in row:
                xCoordinate, yCoordinate = cell.getCoordinates()
                if (x==xCoordinate and y == yCoordinate):
                    return cell
        print("did not find cell")
        return False
    def getStartCell(self):
        """returns cell object in the warehouse, that is the start cell"""
        for row in self.cells:
            for cell in row:
                if cell.getCellType() == "start":
                    return cell
        print("start cell was not found")
        return False
    def getEndCell(self):
        """returns cell object in the warehouse, that is the end cell"""
        for row in self.cells:
            for cell in row:
                if cell.getCellType() == "end":
                    return cell
        print("end cell was not found")
        return False
    def getAllStorageCells(self):
        """returns list of all cells that are storage cells"""
        storageCells = []
        for row in self.cells:
            for cell in row:
                if (cell.getCellType()=="storage"):
                    storageCells.append(cell)
        #print("STOERAGE: ", storageCells)
        return storageCells
    def getRobots(self):
        return self.robots
    def setRobots(self, robots : list):
        self.robots = robots
    def getCurrentTruckload(self):
        return self.currentTruckload
    def setCurrentTruckload(self, truckload : Truckload):
        self.currentTruckload = truckload
    def getAllProductsAndAmountsInWarehouse(self):
        """returns dictionary of all products and amount in the warehouse in total, used to see if warehouse can fill a customer order"""
        allProducts = dict()
        storageCells = self.getAllStorageCells()
        for storageCell in storageCells:
            prodsAndAmounts = storageCell.getProductsAndAmounts()
            for (product, amount) in prodsAndAmounts.items():
                if (product in allProducts.keys()):
                    currentAmount = allProducts[product]
                    currentAmount+=amount
                    allProducts[product] = currentAmount
                else:
                    allProducts[product] = amount
        return allProducts


    def addBackToTruckload(self, product : Product, amount : int):
        """to add back to current truckload, happens if a robot returns with stock after trying to place it in a storage cell"""
        for i in range(amount):
            self.currentTruckload.addProduct(product)
        print("added to truckload, truckload is now: ", self.currentTruckload.getLoad())

    def addTruckload(self, truckload : Truckload):
        self.truckloads.append(truckload)
    def addCustomerOrder(self, customerOrder : CustomerOrder):
        self.customerOrders.append(customerOrder)


#handle the next timeStep of the warehouse
    def nextTimeStep(self):
        """go to next timestep, that means new truckload can come, all robots move once (or wait), 1 timestep = 10 sec (so a robot unloading will take 12 timeSteps for example"""
        if (len(self.truckloads)>0):
            self.currentTruckload = self.truckloads[0] #current truckorder and customerorders are the first ones that came in
        if (len(self.customerOrders)>0):
            self.currentCustomerOrder = self.customerOrders[0]
        if (len(self.customerOrders)==0 and len(self.truckloads)==0):
            return True #just wait if nothing is happening
        
        if (len(self.currentTruckload.getLoad()) == 0): #if truckload is completed
            self.truckloads.pop(0)
        if (len(self.currentCustomerOrder.getOrder()) == 0): #if customer order is completed
            print("FILLED CUSTOMER ORDER!")
            self.customerOrders.pop(0)

        self.placeLoadInCell() #if available robot, activate #TODO
        #self.pickUpCustomerOrder()

        print("CURRENTLY IN WAREHOUSE")
        for key, value in self.getAllProductsAndAmountsInWarehouse().items():
            print(key.getName(), ":", value)
        print("STILL IN TRUCKLOAD")
        for key, value in self.currentTruckload.getLoad().items():
            print(key.getName(), ":", value)
        print("ON ROBOT:")
        if (self.robots[0].getCurrentLoad()[0] != None):
            print(self.robots[0].getCurrentLoad()[0].getName(), self.robots[0].getCurrentLoad()[1])


        for robot in self.robots:
            robot.move()
            prodName = "None"
            if robot.getCurrentLoad()[0] != None:
                prodName = robot.getCurrentLoad()[0].getName()
            print("After moving, ", robot.getName(), "is in coordinate: ", robot.getCurrentCell().getCoordinates(), "with load: ", prodName, robot.getCurrentLoad()[1])
        
    def placeLoadInCell(self):
        """find out if available robots, if so, load them and activate"""
        availableRobots = self.getAvailableRobots()
        if (len(availableRobots) > 0):
            robot = availableRobots[0]
            load = self.currentTruckload.getMax40Weight()
            if (load[0] == None or load[1] == 0): #if there was no more load to get
                return None
            product, amount = load
            cell = self.findCell(product, amount)
            if (cell==None):
                print("did not find cell to go to")
                return None
            robot.storeLoad(cell, load)
            print("Robot: ", robot.getName(), "going to cell: ", cell.getCoordinates(), "going with load: ", load[0].getName(), "and amount: ", load[1])


    def pickUpCustomerOrder(self):
        availableRobots = self.getAvailableRobots()
        if (len(availableRobots) > 0):
            robot = availableRobots[0]
            load = self.get40FromOrder(self.currentCustomerOrder)
            if (load == None):
                print("was not product or amount of product in pickUpCustomerOrder")
                return None
            cellToGoTo = self.locateCellWithLoad(load)
            if (cellToGoTo == None):
                print("did not find cell to go to in pickUpCustomerOrder")
                return None
            robot.retrieveLoad(cellToGoTo, load)


    def getAvailableRobots(self):
        """returns all available robots, aka those that are in endCell, and ready for loading"""
        availableRobots = []
        for robot in self.robots:
            if (robot.getCurrentCell() == self.getEndCell()) and (robot.getWaitTime()==0) and (robot.getCurrentLoad() == (None, 0)):
                availableRobots.append(robot)
        return availableRobots

  
#helper functions to pick up products from warehouse
    def locateCellWithLoad(self, load):
        """locates a cell which has the products that a robot is going to carry"""
        product, amount = load
        for storageCell in self.getAllStorageCells():
            amountInCell = 0
            product1, amount1 = storageCell.getShelf1()
            product2, amount2 = storageCell.getShelf2()
            if (product == product1):
                amountInCell+=amount1
            if (product == product2):
                amountInCell += amount2
            if (amountInCell >= amount): #if cell has enough of product I am searching for
                return storageCell
        return None

    def get40FromOrder(self, customerOrder : CustomerOrder):
        """returns a (product, amount) with product and the amount, where total weight <= 40 """
        productToCarry = None
        amountToCarry = 0
        totalWeight = 0
        for product, amount in customerOrder.getOrder().items():
            productToCarry = product
            productWeight = product.getWeight()
            for i in range(amount):
                if (totalWeight + productWeight > 40):
                    return (productToCarry, amountToCarry)
                totalWeight += productWeight
                amountToCarry+=1
            return (productToCarry, amountToCarry) #only want to run 1 iteration since robot can only carry one type of product at a time
        return None

    def fillOrderWithLoad(self, load):
        """fill the current Customer order with load, just removes the load from the customer order"""
        product, amount = load
        for i in range(amount):
            self.currentCustomerOrder.removeFromOrder(product)

#functions handling the shelves of the warehouse and where to put products
  
    def findCell(self, product : Product, amount : int):
        """find an available storage cell for the product to go to return that cell"""
        cellsToGoTo = []
        allCells = self.getAllStorageCells()
        currentAmount = amount
        #first check if there are any cells that already have the same kind of product -> if so I want to go there first
        for cell in allCells:
            if (cell.getRobotIsOnyWay()): #can not go to cell that another robot is going to
                continue
            amountShelf1, amountShelf2 = self.getAmountYouCanPutIntoEachShelfOfCell(product, cell)
            if (amountShelf1 > 0): #amount you can put into shelf1
                currentAmount -= amountShelf1
                if (currentAmount <= 0):
                    cellsToGoTo.append(cell)
                    return cellsToGoTo[0]
                cellsToGoTo.append(cell) 

            if (amountShelf2 > 0):
                currentAmount -= amountShelf2
                if (currentAmount <= 0):
                    cellsToGoTo.append(cell)
                    return cellsToGoTo[0]
                cellsToGoTo.append(cell)

        print("Could not find cell for item")
        return None

    def getAmountYouCanPutIntoEachShelfOfCell(self, product : Product, cell : Cell):
        """returns amountShelf1, amountShelf2, the amounts each shelf of a shelf, can fit of a specific product. Does not set the state of the shelves"""
        shelf1, shelf2 = cell.getShelf1(), cell.getShelf2()
        productWeight = product.getWeight()
        amountShelf1 = 0
        amountShelf2 = 0
        productShelf1 = cell.getProductFromShelf(shelf1)
        productShelf2 = cell.getProductFromShelf(shelf2)
        if (productShelf1 == None): #if so, no product is in the shelf
            amountShelf1 =  math.floor(100/productWeight)  #since 100 kg is the amount of weight a shelf can carry
            #cell.setShelf1(product, amountShelf1)
        elif (productShelf1 == product): #if the same product is in the shelf, we can still fill the shelf up to 100 kg
            amountShelf1 = cell.getAmountFromShelf(shelf1)
            weightShelf1 = productWeight*amountShelf1
            amountShelf1 = math.floor( (100-weightShelf1)/productWeight ) 
            #cell.setShelf1(product, amountShelf1)
            
        if (productShelf2 == None):
            amountShelf2 = math.floor(100/productWeight)
        elif (productShelf2 == product): #if the same product is in the shelf, we can still fill the shelf up to 100 kg
            amountShelf2 = cell.getAmountFromShelf(shelf2)
            weightShelf2 = productWeight*amountShelf2
            amountShelf2= math.floor( (100-weightShelf2)/productWeight ) 

        return amountShelf1, amountShelf2



#creating and printing warehouse
    def createWarehouse(self, xSize, ySize):
        """makes a warehouse with cells"""
        if (xSize < 6 or ySize < 6):
            print("xSize must be atleast 6, ySize must be atleast 9")
            return None
        if not (xSize%6==0):
            print("dimensioning xSize to be divisible by 6 (rounding downwards), so that all storages are accesible")
            xSize -= (xSize%6)
        for y in range(1, ySize+1):
            row = []
            if (y == ySize//2): 
                cell = Cell("start", 0, y) #start and end cell have x coordinate 0
                row.append(cell)
            elif (y== (ySize//2+1)):
                cell = Cell("end", 0, y)
                row.append(cell)

            for x in range(1, xSize+1): 
                if (y==ySize//2) and (x<(xSize-1)): #8 and 9 are only y coordinates where robot can move in x direction
                    cell = Cell("moveRight", x, y)
                    row.append(cell)
                elif (y== (ySize//2 +1)) and (x<(xSize-1)):
                    cell = Cell("moveLeft", x, y)
                    row.append(cell)
                elif (x==1 or x%6 == 0 or x%6 == 1) and ((y>(ySize//2 +2)) or (y<(ySize//2 -1))): #where I have storage cells
                    cell = Cell("storage", x, y)
                    row.append(cell)
                elif (x%3==2) or (x%6==0 or x%6==1) or (x>=xSize-1):
                    cell = Cell("load", x, y)
                    row.append(cell)
                elif (x%3==0) and (y<ySize//2): #it is a move cell
                    cell = Cell("moveDown", x, y)
                    row.append(cell)
                elif (x%3==1) and y<ySize//2:
                    cell = Cell("moveUp", x, y)
                    row.append(cell)
                elif (x%3==0) and (y>ySize//2): #it is a move cell
                    cell = Cell("moveDown", x, y)
                    row.append(cell)
                elif (x%3==1) and (y>ySize//2):
                    cell = Cell("moveUp", x, y)
                    row.append(cell)
                else:
                    print("did not find cell type, something is wrong")
                    return None
            self.cells.append(row)

    def printWarehouse(self):
        """printing warehouse to terminal, to make sure it looks as expected"""
        for row in self.cells:
            rowString = "  "
            if (row[0].getCellType() == "start" or row[0].getCellType() == "end"): #to visualize start/end
                rowString = "O "
            
            for cell in row:
                cellType = cell.getCellType()
                if (cellType == "storage"):
                    rowString+="S "
                elif (cellType == "moveDown"):
                    rowString+="v "
                elif (cellType == "moveUp"):
                    rowString+="^ "
                elif (cellType == "moveLeft"):
                    rowString+="<-"
                elif (cellType == "moveRight"):
                    rowString+="->"
                elif (cellType == "load"):
                    rowString+="L "
            print(rowString)      
                
    def makeWarehouseInTkinter(self, xSize, ySize):
        """Returns: (rootWindow, canvas, zones). makes a warehouse with cells and in tkinter so they can be used"""
        rootWindow = Tk()
        rootWindow.title("MAP OF WAREHOUSE")
        zones = []
        cellSize = 50
        canvas = Canvas(rootWindow, width=xSize*cellSize+50, height=ySize*cellSize+50)
        canvas.pack()
        if (xSize < 6 or ySize < 6):
            print("xSize must be atleast 6, ySize must be atleast 9")
            return None
        if not (xSize%6==0):
            print("dimensioning xSize to be divisible by 6 (rounding downwards), so that all storages are accesible")
            xSize -= (xSize%6)
        for y in range(1, ySize+1):
            row = []
            tkinterRow = []
            if (y == ySize//2): 
                cell = Cell("start", 0, y) #start and end cell have x coordinate 0
                #row.append(cell)
                xc = x*cellSize
                yc = y*cellSize
                #zone = canvas.create_rectangle(xc, yc, xc+cellSize, yc+cellSize, fill = "black")
                #tkinterRow.append(zone)
            elif (y== (ySize//2+1)):
                cell = Cell("end", 0, y)
                #row.append(cell)
                xc = x*cellSize
                yc = y*cellSize
                #zone = canvas.create_rectangle(xc, yc, xc+cellSize, yc+cellSize, fill = "black")
                #tkinterRow.append(zone)
            for x in range(1, xSize+1): 
                if (y==ySize//2) and (x<(xSize)): #8 and 9 are only y coordinates where robot can move in x direction
                    cell = Cell("moveRight", x, y)
                    row.append(cell)
                    xc = x*cellSize
                    yc = y*cellSize
                    zone = canvas.create_rectangle(xc, yc, xc+cellSize, yc+cellSize, fill = "green")
                    tkinterRow.append(zone)
                elif (y== (ySize//2 +1)) and (x<(xSize)):
                    cell = Cell("moveLeft", x, y)
                    row.append(cell)
                    xc = x*cellSize
                    yc = y*cellSize
                    zone = canvas.create_rectangle(xc, yc, xc+cellSize, yc+cellSize, fill = "green")
                    tkinterRow.append(zone)
                elif (x==1 or x%6 == 0 or x%6 == 1) and ((y>(ySize//2 +2)) or (y<(ySize//2 -1))): #where I have storage cells
                    cell = Cell("storage", x, y)
                    row.append(cell)
                    xc = x*cellSize
                    yc = y*cellSize
                    zone = canvas.create_rectangle(xc, yc, xc+cellSize, yc+cellSize, fill = "grey")
                    tkinterRow.append(zone)
                elif (x%3==2) or (x%6==0 or x%6==1) or (x>=xSize-1):
                    cell = Cell("load", x, y)
                    row.append(cell)
                    xc = x*cellSize
                    yc = y*cellSize
                    zone = canvas.create_rectangle(xc, yc, xc+cellSize, yc+cellSize, fill = "white")
                    tkinterRow.append(zone)
                elif (x%3==0) and (y<ySize//2): #it is a move cell
                    cell = Cell("moveDown", x, y)
                    row.append(cell)
                    xc = x*cellSize
                    yc = y*cellSize
                    zone = canvas.create_rectangle(xc, yc, xc+cellSize, yc+cellSize, fill = "green")
                    tkinterRow.append(zone)
                elif (x%3==1) and y<ySize//2:
                    cell = Cell("moveUp", x, y)
                    row.append(cell)
                    xc = x*cellSize
                    yc = y*cellSize
                    zone = canvas.create_rectangle(xc, yc, xc+cellSize, yc+cellSize, fill = "green")
                    tkinterRow.append(zone)
                elif (x%3==0) and (y>ySize//2): #it is a move cell
                    cell = Cell("moveDown", x, y)
                    row.append(cell)
                    xc = x*cellSize
                    yc = y*cellSize
                    zone = canvas.create_rectangle(xc, yc, xc+cellSize, yc+cellSize, fill = "green")
                    tkinterRow.append(zone)
                elif (x%3==1) and (y>ySize//2):
                    cell = Cell("moveUp", x, y)
                    row.append(cell)
                    xc = x*cellSize
                    yc = y*cellSize
                    zone = canvas.create_rectangle(xc, yc, xc+cellSize, yc+cellSize, fill = "green")
                    tkinterRow.append(zone)
                else:
                    print("did not find cell type, something is wrong")
                    return None
            self.cells.append(row)
            zones.append(tkinterRow)

        #this handles adding the start and and cell at the middle of the warehouse, and to the left
        for rowNumber in range(1, len(self.cells)+1):
            cell = Cell("load", 0, rowNumber)
            fill = "blue"
            if ((rowNumber)== (ySize//2)): #index of where start/end cell is
                cell = Cell("load", xSize+1, rowNumber) #append the last loading cell (cause start/end cells shift index)
                self.cells[rowNumber-1].append(cell)

                xc = 0
                yc = rowNumber*cellSize
                zone = canvas.create_rectangle(xc, yc, xc+cellSize, yc+cellSize, fill = "white")
                zones[rowNumber-1].append(cell)

                cell = Cell("start", 0, rowNumber)
                fill = "black"
            elif (rowNumber== (ySize//2 +1)):
                cell = Cell("load", xSize+1, rowNumber) 
                self.cells[rowNumber-1].append(cell)

                xc = 0
                yc = rowNumber*cellSize
                zone = canvas.create_rectangle(xc, yc, xc+cellSize, yc+cellSize, fill = "white")
                zones[rowNumber-1].append(cell)

                cell = Cell("end", 0, rowNumber)
                fill="black"

            self.cells[rowNumber-1].insert(0, cell)
            xc = 0
            yc = rowNumber*cellSize
            zone = canvas.create_rectangle(xc, yc, xc+cellSize, yc+cellSize, fill = fill)
            zones[rowNumber-1].append(cell)

      


        frame = Frame(rootWindow)
        frame.pack()
        return rootWindow, canvas, zones
        