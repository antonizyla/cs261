from junction import Junction
from lane import Dir, Lane


class Parameters:
    def __init__(self, no_lanes:int, pedestrian_crossing:bool, crossing_time:int, crossing_rph:float):
        self.noLanes = no_lanes
        self.pedestrianCrossing = pedestrian_crossing
        self.crossingTime = crossing_time
        self.crossingRPH = crossing_rph

    def getNoLanes(self)->int:
        return self.noLanes
    
    def hasPedestrianCrossing(self)->bool:
        return self.pedestrianCrossing
    
    def getCrossingTime(self)->int:
        return self.crossingTime
    
    def getCrossingRPH(self)->float:
        return self.crossingRPH
    
    def isValidParamSet(self) -> bool:
        pass