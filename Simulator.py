
from functools import partial
from CustomerOrder import CustomerOrder
from Product import Product
from Robot import Robot
from Truckload import Truckload
from Warehouse import Warehouse

from tkinter import *


class Simulator():
    def __init__(self):
        self.timeStep = 0
        

    def runSimulation(self, xSize : int, ySize : int, numberOfRobots : int, maxTimeStep : int, displayWarehouse : bool):
        if numberOfRobots>50:
            print("Can't have more than 50 robots, that means caos in the warehouse")
        warehouse = Warehouse()
        #warehouse.createWarehouse(xSize, ySize)
        rootWindow, canvas, zones = warehouse.makeWarehouseInTkinter(xSize, ySize)
        warehouse.printWarehouse()
        robots = []
        for i in range(numberOfRobots):
            robot = Robot(f"robot{i}", warehouse)   
            robots.append(robot)
        warehouse.setRobots(robots)

        #TODO
        #hardcoding Truckload and customerOrder for now
        cheese = Product("cheese", 3)
        chair = Product("chair", 18)
        table = Product("table", 13)
        pen = Product("pen", 6)
        truckload = Truckload("t", 100000)
        load = {cheese : 100, chair : 97, table : 34, pen : 121}
        truckload.setLoad(load)
        warehouse.addTruckload(truckload)
        customerOrder = CustomerOrder("customer1")
        for i in range(10):
            customerOrder.addToOrder(chair)
            customerOrder.addToOrder(cheese)
        warehouse.addCustomerOrder(customerOrder)
 

        for i in range(maxTimeStep):
            print()
            print("___TIMESTEP: ", i, " ____")
            warehouse.nextTimeStep()
            self.timeStep += 1


        #rest of the functions handles the GUI with tkinter:
        self.updateRobotPosition(robots, canvas, zones)
        canvas.create_text(600, 20, text="Yellow cells: where robots are, grey cells: where storage cells are, green cells: where moving cells are. Blue are not cells in the warehouse, black are start/end cells (can not see robots when in start/endcells", fill="black", font=('Helvetica 8 bold'))
        canvas.pack()
        #adding button for going to next timestep, inside tkinter application
        frame = Frame(rootWindow)
        
        button1 = Button(frame, text = "Go to next timestep", command=partial(self.nextTimeStepTkinter, warehouse, robots, canvas, zones)) 
        button1.pack()
        button2 = Button(frame, text = "Go to 10th next timestep", command=partial(self.next10TimeStepsTkinter, warehouse, robots, canvas, zones)) 
        button2.pack()

        frame.pack()
        if (displayWarehouse):
            rootWindow.mainloop()
        return warehouse




#for running with tkinter
    def nextTimeStepTkinter(self, warehouse : Warehouse, robots : list, canvas : Canvas, zones : list):
        print(f"\n ____TIMESTEP {self.timeStep}____")
        self.timeStep+=1
        warehouse.nextTimeStep()
        self.updateRobotPosition(robots, canvas, zones)
 
    def next10TimeStepsTkinter(self, warehouse : Warehouse, robots : list, canvas : Canvas, zones : list):
        for i in range(10):
            print(f"\n ____TIMESTEP {self.timeStep}____")
            self.timeStep+=1
            warehouse.nextTimeStep()
            self.updateRobotPosition(robots, canvas, zones)

    def updateRobotPosition(self, robots : list, canvas : Canvas, zones : list):
        robotPositions = []
        for robot in robots:
            currCell = robot.getCurrentCell()
            if (currCell != None):
                x, y = currCell.getCoordinates()
                robotPositions.append((x,y))

        for robot in robots:
            (x,y) = robot.getCurrentCell().getCoordinates()
            canvas.itemconfig(zones[y-1][x-1], fill="yellow") #-1 because its indexes!
            prevCell = robot.getPreviousCell()
            if (prevCell != None):
                cellType = prevCell.getCellType()
                prevX, prevY = prevCell.getCoordinates()
                if ((prevX, prevY) not in robotPositions): #if another robot is not at same position
                    if (cellType=="moveLeft" or cellType=="moveRight" or cellType=="moveUp" or cellType=="moveDown"):
                        canvas.itemconfig(zones[prevY-1][prevX-1], fill="green") #-1 because its indexes!
                    else:
                        canvas.itemconfig(zones[prevY-1][prevX-1], fill="white") 

            else:
                print("ROBOT DID NOT HAVE PREV")
  