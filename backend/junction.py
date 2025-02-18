from flow_rates import flow_rates
from lane import Lane
from params import Parameters


class Junction:
    def __init__(self, north_lanes: list[Lane], east_lanes: list, south_lanes: list, west_lanes: list, configuration: Parameters):
        self.northLanes = north_lanes
        self.eastLanes = east_lanes
        self.southLanes = south_lanes
        self.westLanes = west_lanes
        self.configuration = configuration
        self.flow_rates = None

    def set_flow_rates(self, rates: flow_rates):
        self.flow_rates = rates
    
    def set_junction_configurations(self, conf: Parameters):
        self.configuration = conf

    def run_simulation(self):
        pass