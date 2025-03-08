from enum import Flag, auto
from flowrates import FlowRates
from params import Parameters
from direction import Direction, TrafficLights


class Junction:
    def __init__(self, p: Parameters, flows: list[FlowRates]):
        self.params = p
        self.flow_rates: list[FlowRates] = flows  # 0-3 indexed North-West
        self.northerly_lanes = Direction(self.flow_rates[0], self.params.noLanes[0])
        self.easterly_lanes = Direction(self.flow_rates[1], self.params.noLanes[1])
        self.southerly_lanes = Direction(self.flow_rates[2], self.params.noLanes[2])
        self.westerly_lanes = Direction(self.flow_rates[3], self.params.noLanes[3])

    def set_flow_rates(self, rates: FlowRates):
        self.flow_rates = rates

    def set_junction_configurations(self, conf: Parameters):
        self.params = conf

    def run_simulation(self):
        NSR = max(self.flow_rates[0].get_flow_right(), self.flow_rates[2].get_flow_right())
        NSO = max(self.flow_rates[0].get_flow_left() + self.flow_rates[0].get_flow_ahead(),
                  self.flow_rates[2].get_flow_left() + self.flow_rates[2].get_flow_ahead())
        EWR = max(self.flow_rates[1].get_flow_right(), self.flow_rates[3].get_flow_right())
        EWO = max(self.flow_rates[1].get_flow_left() + self.flow_rates[1].get_flow_ahead(),
                  self.flow_rates[3].get_flow_left() + self.flow_rates[3].get_flow_ahead())

        traffic_light_timing: list[int] = [NSR, NSO, EWR, EWO]
        traffic_light_timing.sort(reverse=True)
        traffic_light_order = []
        for i in range(0, 4):
            if (traffic_light_timing[i] == NSR) and (TrafficLights.NORTH_SOUTH_RIGHT not in traffic_light_order):
                traffic_light_order.append(TrafficLights.NORTH_SOUTH_RIGHT)
            elif (traffic_light_timing[i] == NSO) and (TrafficLights.NORTH_SOUTH_OTHER not in traffic_light_order):
                traffic_light_order.append(TrafficLights.NORTH_SOUTH_OTHER)
            elif (traffic_light_timing[i] == EWR) and (TrafficLights.EAST_WEST_RIGHT not in traffic_light_order):
                traffic_light_order.append(TrafficLights.EAST_WEST_RIGHT)
            elif (traffic_light_timing[i] == EWO) and (TrafficLights.EAST_WEST_OTHER not in traffic_light_order):
                traffic_light_order.append(TrafficLights.EAST_WEST_OTHER)

        for i in range(0, 4):  # Value to change during development
            if traffic_light_timing[i % 4] == NSR or traffic_light_timing[i % 4] == NSO:
                seconds_spent = (max(self.params.get_sequencing_priority()[0],
                                     self.params.get_sequencing_priority()[2]) + 1) * 10
            else:
                seconds_spent = (max(self.params.get_sequencing_priority()[1],
                                     self.params.get_sequencing_priority()[3]) + 1) * 10

            for dir in [self.northerly_lanes, self.easterly_lanes, self.southerly_lanes, self.westerly_lanes]:
                dir.simulateUpdate(traffic_light_order[i % 4],
                                   seconds_spent)  # Need to further multiply by some constant - currently is number of cars per minute,

            self.add_vehicles(seconds_spent)

        # Calculating max wait - uses the idea that cars considered later in the simulation will have to wait the same time or longer -> cars at the end of the simulation wait the longest
        self.northerly_lanes.set_calculating_max_wait(True)
        self.easterly_lanes.set_calculating_max_wait(True)
        self.southerly_lanes.set_calculating_max_wait(True)
        self.westerly_lanes.set_calculating_max_wait(True)
        total_vehicles = self.northerly_lanes.get_total_vehicles() + self.easterly_lanes.get_total_vehicles() + self.southerly_lanes.get_total_vehicles() + self.westerly_lanes.get_total_vehicles()
        i = 0

        while total_vehicles > 0 and i < 100:
            self.northerly_lanes.simulateUpdate(traffic_light_order[i % 4], traffic_light_timing[
                i % 4] / 60)  # Need to further multiply by some constant - currently is number of cars per minute,
            self.easterly_lanes.simulateUpdate(traffic_light_order[i % 4], traffic_light_timing[i % 4] / 60)
            self.southerly_lanes.simulateUpdate(traffic_light_order[i % 4], traffic_light_timing[i % 4] / 60)
            self.westerly_lanes.simulateUpdate(traffic_light_order[i % 4], traffic_light_timing[i % 4] / 60)
            i += 1
            total_vehicles = self.northerly_lanes.get_total_vehicles() + self.easterly_lanes.get_total_vehicles() + self.southerly_lanes.get_total_vehicles() + self.westerly_lanes.get_total_vehicles()

        # Generate and Return ResultSet
        # return ResultSet(n, e, s, w, )

    def add_vehicles(self, seconds_spent):
        for dir in [self.northerly_lanes, self.easterly_lanes, self.southerly_lanes, self.westerly_lanes]:
            dir.add_to_pools(seconds_spent)
