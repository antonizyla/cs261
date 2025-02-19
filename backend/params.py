from junction import Junction
from lane import Dir, Lane


class Parameters:
    def __init__(self, no_lanes:int, dedicated_lane:bool, dedicated_lane_flow: list[int], pedestrian_crossing:bool, crossing_time:int, crossing_rph:float, sequencing_priority:list[int]):
        self.noLanes = no_lanes
        self.dedicatedLane = dedicated_lane
        self.dedicatedLaneFlow = dedicated_lane_flow
        self.pedestrianCrossing = pedestrian_crossing
        self.crossingTime = crossing_time
        self.crossingRPH = crossing_rph
        self.sequencingPriority = sequencing_priority


    def getNoLanes(self)->list[int]:
        return self.noLanes
    
    def getDedicatedLane(self)->list[LaneData]:
        return self.dedicatedLane
    
    def getDedicatedLaneFlow(self)->list[int]:
        return self.dedicatedLaneFlow
    
    def hasPedestrianCrossing(self)->list[bool]:
        return self.pedestrianCrossing
    
    def getCrossingTime(self)->list[int]:
        return self.crossingTime
    
    def getCrossingRPH(self)->list[float]:
        return self.crossingRPH
    
    def getSequencingPriority(self)->list[int]:
        return self.sequencingPriority

    def isValidParamSet(self) -> list[bool]:
        pass
