from vehicle import Vehicle
from lane import Lane

class Direction:
    def __init__(self, pools: list[Vehicle], lanes: list[Lane], dedicatedLane: bool, dedicatedLaneFlow: int, maxLength: int, maxWait: float, avgWait: float):
        self.pools = pools
        self.lanes = lanes
        self.dedicatedLane = dedicatedLane
        self.dedicatedLaneFlow = dedicatedLaneFlow
        self.maxLength = maxLength
        self.maxWait = maxWait
        self.avgWait = avgWait

    def empty_constructor(self):
       pass
    
    def simulate_update(self) -> None:
        #TODO
        pass

    def get_max_length(self) -> int:
        return self.maxLength
    
    def get_max_wait(self)-> float:
        return self.maxWait
    
    def get_avg_wait(self) -> float:
        return self.avgWait

    def check(self) -> bool:
        return False