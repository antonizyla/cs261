from flowrates import FlowRates
from lane import Lane, Dir
from params import Parameters
from direction import Direction


class Junction:
    def __init__(self, p: Parameters, flows: [FlowRates]):
        self.params = p
        self.flow_rates: [FlowRates] = flows #0-3 indexed North-West
        self.northerly_lanes = Direction(self.flow_rates[0], self.params.noLanes)
        self.easterly_lanes = Direction(self.flow_rates[1], self.params.noLanes)
        self.southerly_lanes = Direction(self.flow_rates[2], self.params.noLanes)
        self.westerly_lanes = Direction(self.flow_rates[3], self.params.noLanes)

    def create_junction(self):
        # create the directions
        directions: [Direction] = []
        for d, i in enumerate(self.flow_rates):
            directions.append(Direction(self.flow_rates[i], self.params.noLanes))
            pass
        pass

    def set_flow_rates(self, rates: FlowRates):
        self.flow_rates = rates
    
    def set_junction_configurations(self, conf: Parameters):
        self.params = conf

    def run_simulation(self):
        pass
