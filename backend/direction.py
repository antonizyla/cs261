from flowrates import FlowRates
from lane import Lane, left_of, right_of, opposite_of
from params import Parameters
from vehicle import Vehicle

class Direction:
    def __init__(self, flows: FlowRates, num_lanes: int):
        self.flows = FlowRates
        self.pool: [Vehicle] = None
        self.max_wait = None
        self.max_length = None
        self.avg_wait = None
        self.lanes = []
        self.num_lanes_to_generate = num_lanes
        if self.num_lanes_to_generate == 1:
            self.lanes.append(Lane(5, flows.direction_from, [left_of(flows.direction_from), right_of(flows.direction_from), opposite_of(flows.direction_from)]))
        else:
            # todo generate rest of lanes based on lanes and dedicated lanes
            pass

    # hourly/longer period update
    def simulate_hourly(self):
        # todo
        # top up pools and report on stats
        pass

    # tick based update
    def simulate_update(self) -> None:
        #TODO
        pass

    def get_max_length(self) -> int:
        return self.max_length
    def get_max_wait(self)-> float:
        return self.max_wait
    def get_avg_wait(self) -> float:
        return self.avg_wait