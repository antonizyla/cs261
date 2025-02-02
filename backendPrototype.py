class Vehicle:
    def __init__(self, direction_from, direction_to):
        self.direction_from = direction_from
        self.direction_to = direction_to

class Lane:
    def __init__(self, currentVehicles, queueLimit, flowing, directionTo, directionFrom, maxLength, maxWait, avgWait):
        self.currentVehicles = []
        self.queueLimit = queueLimit
        self.flowing = False
        self.directionTo = directionTo
        self.directionFrom = directionFrom
        self.maxLength = maxLength
        self.maxWait = maxWait
        self.avgWait = avgWait

    def getMaxLength(self):
        return self.maxLength
    
    def getMaxWait(self):
        return self.maxWait
    
    def getAvgWait(self):
        return self.avgWait
    
class Direction:
    def __init__(self, pools, lanes, dedicatedLane, dedicatedLaneFlow):
        self.pools = pools
        self.lanes = lanes
        self.dedicatedLane = dedicatedLane
        self.dedicatedLaneFlow = dedicatedLaneFlow
    
    def simulateUpdate(self):
        #TODO
        pass

class Parameters:
    def __init__(self, noLanes, dedicatedLane, dedicatedLaneFlow, pedestrianCrossing, crossingTime, crossingRPH, sequencingPriority):
        self.noLanes = noLanes
        self.dedicatedLane = dedicatedLane
        self.dedicatedLaneFlow = dedicatedLaneFlow
        self.pedestrianCrossing = pedestrianCrossing
        self.crossingTime = crossingTime
        self.crossingRPH = crossingRPH
        self.sequencingPriority = sequencingPriority

    def getNoLanes(self):
        return self.noLanes
    
    def getDedicatedLane(self):
        return self.dedicatedLane
    
    def getDedicatedLaneFlow(self):
        return self.dedicatedLaneFlow
    
    def hasPedestrianCrossing(self):
        return self.pedestrianCrossing
    
    def getCrossingTime(self):
        return self.crossingTime
    
    def getCrossingRPH(self):
        return self.crossingRPH
    
    def getSequencingPriority(self):
        return self.sequencingPriority
        

class FlowRates:
    def __init__(self, northRoadFlow, eastRoadFlow, southRoadFlow, westRoadFlow, driveOnLeft):
        self.northRoadFlow = northRoadFlow
        self.eastRoadFlow = eastRoadFlow
        self.southRoadFlow = southRoadFlow
        self.westRoadFlow = westRoadFlow
        self.driveOnLeft = driveOnLeft

    def getNorthRoadFlow(self):
        return self.northRoadFlow
    
    def getEastRoadFlow(self):
        return self.eastRoadFlow
    
    def getSouthRoadFlow(self):
        return self.southRoadFlow
    
    def getWestRoadFlow(self):
        return self.westRoadFlow
    
    def driveOnLeft(self):
        return self.driveOnLeft
       
class Junction:
    def __init__(self, northLanes, eastLanes, southLanes, westLanes, configuration):
        self.northLanes = northLanes
        self.eastLanes = eastLanes
        self.southLanes = southLanes
        self.westLanes = westLanes
        self.configuration = configuration

    def setFlowRates():
        #TODO
        pass
    
    def setJunctionConfiguration():
        #TODO
        pass

    def runSimulation():
        #TODO
        return 0
    

class ResultSet:
    def __init__(self, northRoad, eastRoad, southRoad, westRoad, overallScore):
        self.northRoad = northRoad
        self.eastRoad = eastRoad
        self.southRoad = southRoad
        self.westRoad = westRoad
        self.overallScore = overallScore

    def getNorthRoad(self):
        return self.northRoad
    
    def getEastRoad(self):
        return self.eastRoad
    
    def getSouthRoad(self):
        return self.southRoad
    
    def getWestRoad(self):
        return self.westRoad
    
    def getScore(self):
        return self.overallScore
        