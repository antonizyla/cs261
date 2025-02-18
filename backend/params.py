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

    def generate_junction(self)->Junction:
        north_lanes = []
        east_lanes = []
        south_lanes = []
        west_lanes = []
        if self.dedicatedLane:
            north_lanes.append(Lane(5, Dir.NORTH, [Dir.SOUTH, Dir.WEST]))
            east_lanes.append(Lane(5, Dir.EAST, [Dir.SOUTH, Dir.WEST]))
            south_lanes.append(Lane(5, Dir.SOUTH, [Dir.NORTH, Dir.WEST]))
            west_lanes.append(Lane(5, Dir.WEST, [Dir.NORTH, Dir.WEST]))
        lanes_to_gen = self.noLanes - 1 if self.dedicatedLane else self.noLanes
        if lanes_to_gen == 1:
            north_lanes.append(Lane(5, Dir.NORTH, [Dir.SOUTH, Dir.WEST, Dir.EAST]))
            # todo rest of this for east, south, west
        else:
            for i in range(lanes_to_gen-2):
                north_lanes.append(Lane(5, Dir.NORTH, [Dir.SOUTH]))
            north_lanes.append(Lane(5, Dir.NORTH, [Dir.SOUTH, Dir.EAST]))
            north_lanes.append(Lane(5, Dir.NORTH, [Dir.SOUTH, Dir.WEST]))
            # todo rest of this for east, south, west
        return Junction(north_lanes, east_lanes, south_lanes, west_lanes, self)

    def getNoLanes(self)->int:
        return self.noLanes
    
    def getDedicatedLane(self)->bool:
        return self.dedicatedLane
    
    def getDedicatedLaneFlow(self)->list[int]:
        return self.dedicatedLaneFlow
    
    def hasPedestrianCrossing(self)->bool:
        return self.pedestrianCrossing
    
    def getCrossingTime(self)->int:
        return self.crossingTime
    
    def getCrossingRPH(self)->float:
        return self.crossingRPH
    
    def getSequencingPriority(self)->list[int]:
        return self.sequencingPriority

    def isValidParamSet(self) -> bool:
        pass