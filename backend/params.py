from backend.lane import Dir, Lane


class Parameters:
    def __init__(self, no_lanes: list[int] = [2, 2, 2, 2],
                 pedestrian_crossing: list[bool] = [False, False, False, False],
                 crossing_time: int = 0, crossing_rph: float = 0,
                 sequencing_priority: list[int] = [1, 1, 1, 1]):
        self.noLanes = no_lanes
        self.pedestrianCrossing = pedestrian_crossing
        self.crossingTime = crossing_time
        self.crossingRPH = crossing_rph
        self.sequencingPriority = sequencing_priority

        if self.sequencingPriority is None:
            self.sequencingPriority = [1, 1, 1, 1]
        if self.pedestrianCrossing is None:
            self.pedestrianCrossing = [False, False, False, False]

    def check(self):
        # check that sequencing priortiy is good
        if self.sequencingPriority:
            for x in self.sequencingPriority:
                if x < 0 or x > 4 or isinstance(x, float):
                    return False
            if len(self.sequencingPriority) != 4:
                return False
        # print("Sequencing ok")
        # check that noLanes is good
        if len(self.noLanes) != 4:
            return False
        for x in self.noLanes:
            if x < 0 or x > 5 or isinstance(x, float):
                return False
        # print("Lanes ok")
        # check that pedestrian crossings are good
        if len(self.pedestrianCrossing) != 4:
            return False
        for x in self.pedestrianCrossing:
            if x is not True and x is not False:
                return False
        # print("Pedestrian Cross ok")
        # check crossingtimes    
        if self.crossingTime < 0:
            return False
        # print("Crossingtimes ok")
        # check crossingrph
        if self.crossingRPH < 0 or self.crossingRPH > 30:
            return False
        # print("Crossing rph ok")
        return True

    def get_no_lanes(self) -> list[int]:
        return self.noLanes

    def has_pedestrian_crossing(self) -> [bool]:
        return self.pedestrianCrossing

    def get_crossing_time(self) -> int:
        return self.crossingTime

    def get_crossing_rph(self) -> float:
        return self.crossingRPH

    def get_sequencing_priority(self) -> list[int]:
        return self.sequencingPriority

    def is_valid_param_set(self) -> list[bool]:
        pass
