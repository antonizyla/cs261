from junction import Junction
from lane import Dir, Lane


class Parameters:
    def __init__(self, no_lanes:[int], dedicated_lane:[bool], dedicated_lane_flow: [int], pedestrian_crossing:[bool], crossing_time:[int], crossing_rph:float, sequencing_priority:list[int]):
        self.noLanes = no_lanes
        self.dedicatedLane = dedicated_lane
        self.dedicatedLaneFlow = dedicated_lane_flow
        self.pedestrianCrossing = pedestrian_crossing
        self.crossingTime = crossing_time
        self.crossingRPH = crossing_rph
        self.sequencingPriority = sequencing_priority


    def get_no_lanes(self)->list[int]:
        return self.noLanes
    
    def get_dedicated_lane(self)->[bool]:
        return self.dedicatedLane
    
    def get_dedicated_lane_flow(self)->list[int]:
        return self.dedicatedLaneFlow
    
    def has_pedestrian_crossing(self)->[bool]:
        return self.pedestrianCrossing
    
    def get_crossing_time(self)->[int]:
        return self.crossingTime
    
    def get_crossing_rph(self)->[float]:
        return self.crossingRPH
    
    def get_sequencing_priority(self)->list[int]:
        return self.sequencingPriority

    def is_valid_param_set(self) -> list[bool]:
        pass
