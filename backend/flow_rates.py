class flow_rates:
    def __init__(self, northRoadFlow: int, eastRoadFlow:int, southRoadFlow:int, westRoadFlow:int, driveOnLeft:bool):
        self.northRoadFlow = northRoadFlow
        self.eastRoadFlow = eastRoadFlow
        self.southRoadFlow = southRoadFlow
        self.westRoadFlow = westRoadFlow
        self.driveOnLeft = driveOnLeft

    def getNorthRoadFlow(self)->int:
        return self.northRoadFlow
    
    def getEastRoadFlow(self)->int:
        return self.eastRoadFlow
    
    def getSouthRoadFlow(self)->int:
        return self.southRoadFlow
    
    def getWestRoadFlow(self)->int:
        return self.westRoadFlow
    
    def driveOnLeft(self)->bool:
        return self.driveOnLeft

    def check(self)->bool:
        if self.eastRoadFlow != 0 and self.westRoadFlow != 0 and self.northRoadFlow != 0 and self.southRoadFlow != 0:
            return False
        if self.eastRoadFlow < 0 or self.westRoadFlow <0 or self.southRoadFlow <0 or self.northRoadFlow < 0:
            return False
        return True