import direction
from flow_rates import flow_rates
from lane import Lane, Dir
from params import Parameters


class Junction:
    def __init__(self, north_lanes: list[Lane], east_lanes: list, south_lanes: list, west_lanes: list, configuration: Parameters):
        self.northLanes: direction = north_lanes
        self.eastLanes  = east_lanes
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

    # Create a junction based on parameters
    def generate_junction_params(self, p: Parameters):
        self.set_junction_configurations(p)
        self.generate_junction()

    # create a junction based on parameters
    def generate_junction(self):
        north_lanes = []
        east_lanes = []
        south_lanes = []
        west_lanes = []
        if self.configuration.dedicatedLane:
            north_lanes.append(Lane(5, Dir.NORTH, [Dir.SOUTH, Dir.WEST]))
            east_lanes.append(Lane(5, Dir.EAST, [Dir.SOUTH, Dir.WEST]))
            south_lanes.append(Lane(5, Dir.SOUTH, [Dir.NORTH, Dir.WEST]))
            west_lanes.append(Lane(5, Dir.WEST, [Dir.NORTH, Dir.WEST]))
        lanes_to_gen = self.configuration.noLanes - 1 if self.configuration.dedicatedLane else self.configuration.noLanes
        if lanes_to_gen == 1:
            north_lanes.append(Lane(5, Dir.NORTH, [Dir.SOUTH, Dir.WEST, Dir.EAST]))
            # todo rest of this for east, south, west
        else:
            for i in range(lanes_to_gen-2):
                north_lanes.append(Lane(5, Dir.NORTH, [Dir.SOUTH]))
            north_lanes.append(Lane(5, Dir.NORTH, [Dir.SOUTH, Dir.EAST]))
            north_lanes.append(Lane(5, Dir.NORTH, [Dir.SOUTH, Dir.WEST]))
            # todo rest of this for east, south, west
        pass