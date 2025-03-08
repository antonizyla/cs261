import math
import random
from enum import Flag, auto

from flowrates import FlowRates
from lane import Lane, left_of, right_of, opposite_of, Dir
from vehicle import Vehicle, VehicleType


class TrafficLights(Flag):
    NORTH_SOUTH_RIGHT = auto()
    NORTH_SOUTH_OTHER = auto()
    EAST_WEST_RIGHT = auto()
    EAST_WEST_OTHER = auto()


class Direction:
    def __init__(self, flows: FlowRates, num_lanes: int):
        self.bus_residuals = [0, 0, 0]
        self.residuals = [0, 0, 0]
        self.flows: FlowRates = flows
        #self.pools: list[int] = [0, 0, 0]
        #self.pools_bus: list[int] = [0, 0, 0]
        self.max_wait = 0
        self.max_length = 0
        self.avg_wait = 0
        self.lanes = []
        self.calculating_max_wait = False

        # the vehicle pools that need to go into lanes
        self.p_ahead_c: list[Vehicle] = []
        self.p_ahead_b: list[Vehicle] = []
        self.p_left_c: list[Vehicle] = []
        self.p_left_b: list[Vehicle] = []
        self.p_right_c: list[Vehicle] = []
        self.p_right_b: list[Vehicle] = []
        if num_lanes == 1:
            self.lanes.append(Lane(3, flows.dir_from,
                                   [left_of(flows.dir_from), right_of(flows.dir_from), opposite_of(flows.dir_from)]))
        elif num_lanes == 2:
            if flows.dedicated_bus:
                self.lanes.append(Lane(3, flows.dir_from, [left_of(flows.dir_from)], bus=True))
                self.lanes.append(Lane(3, flows.dir_from, [left_of(flows.dir_from), opposite_of(flows.dir_from),
                                                           right_of(flows.dir_from)]))
            else:
                if (flows.dedicated_left and flows.dedicated_right) or (
                        flows.dedicated_right and not flows.dedicated_left):
                    # create a left+forward lane and a right only lane
                    self.lanes.append(Lane(3, flows.dir_from, [left_of(flows.dir_from), right_of(flows.dir_from)]))
                    self.lanes.append(Lane(3, flows.dir_from, [right_of(flows.dir_from)]))
                elif flows.dedicated_left:
                    self.lanes.append(Lane(3, flows.dir_from, [left_of(flows.dir_from)]))
                    self.lanes.append(Lane(3, flows.dir_from, [opposite_of(flows.dir_from), right_of(flows.dir_from)]))
                else:
                    self.lanes.append(Lane(3, flows.dir_from, [left_of(flows.dir_from), opposite_of(flows.dir_from)]))
                    self.lanes.append(Lane(3, flows.dir_from, [opposite_of(flows.dir_from), right_of(flows.dir_from)]))
        elif num_lanes == 3:
            if flows.dedicated_bus:
                self.lanes.append(Lane(3, flows.dir_from, [left_of(flows.dir_from)], bus=True))
                self.lanes.append(Lane(3, flows.dir_from, [left_of(flows.dir_from), opposite_of(flows.dir_from),
                                                           right_of(flows.dir_from)]))
                if flows.dedicated_right:
                    self.lanes.append(Lane(3, flows.dir_from, [right_of(flows.dir_from)]))
                else:
                    self.lanes.append(Lane(3, flows.dir_from, [opposite_of(flows.dir_from), right_of(flows.dir_from)]))
            else:
                if flows.dedicated_left and flows.dedicated_right:
                    self.lanes.append(Lane(3, flows.dir_from, [left_of(flows.dir_from)]))
                    self.lanes.append(Lane(3, flows.dir_from, [right_of(flows.dir_from)]))
                    self.lanes.append(Lane(3, flows.dir_from, [right_of(flows.dir_from), left_of(flows.dir_from),
                                                               opposite_of(flows.dir_from)]))
                elif flows.dedicated_right:
                    self.lanes.append(Lane(3, flows.dir_from, [left_of(flows.dir_from), opposite_of(flows.dir_from)]))
                    self.lanes.append(Lane(3, flows.dir_from, [right_of(flows.dir_from), opposite_of(flows.dir_from)]))
                    self.lanes.append(Lane(3, flows.dir_from, [right_of(flows.dir_from)]))
                elif flows.dedicated_left:
                    self.lanes.append(Lane(3, flows.dir_from, [left_of(flows.dir_from)]))
                    self.lanes.append(Lane(3, flows.dir_from, [left_of(flows.dir_from), opposite_of(flows.dir_from)]))
                    self.lanes.append(Lane(3, flows.dir_from, [opposite_of(flows.dir_from), right_of(flows.dir_from)]))
                else:
                    self.lanes.append(Lane(3, flows.dir_from, [left_of(flows.dir_from), opposite_of(flows.dir_from)]))
                    self.lanes.append(Lane(3, flows.dir_from, [opposite_of(flows.dir_from)]))
                    self.lanes.append(Lane(3, flows.dir_from, [opposite_of(flows.dir_from), right_of(flows.dir_from)]))
        else:
            # TODO - add full fledged junction generation functionality for more lanes and all combos of dedicated bus lanes and shite
            n_generated = 0
            if flows.dedicated_bus:
                n_generated += 1
                self.lanes.append(Lane(3, flows.dir_from, [left_of(flows.dir_from)], bus=True))
                if flows.dedicated_right:
                    self.lanes.append(Lane(3, flows.dir_from, [right_of(flows.dir_from)]))
                    n_generated += 1
                for i in range(num_lanes - n_generated):
                    self.lanes.append(Lane(3, flows.dir_from, [opposite_of(flows.dir_from)]))
            else:
                if flows.dedicated_left:
                    n_generated += 1
                    self.lanes.append(Lane(3, flows.dir_from, [left_of(flows.dir_from)]))
                elif flows.dedicated_right:
                    n_generated += 1
                    self.lanes.append(Lane(3, flows.dir_from, [right_of(flows.dir_from)]))
                for i in range(num_lanes - n_generated):
                    self.lanes.append(Lane(3, flows.dir_from, [opposite_of(flows.dir_from)]))
        print(f"generated {len(self.lanes)} lanes")

    # hourly/longer period update
    #def simulate_hourly(self):
    #    # working on assumption that bus flows are on top of flow for the direction
    #    self.pools[0] += self.flows.get_flow_left()
    #    self.pools_bus[0] += self.flows.get_flow_bus_left()
    #
    #    self.pools[1] += self.flows.get_flow_ahead()
    #    self.pools_bus[1] += self.flows.get_flow_bus_ahead()
    #
    #    self.pools[2] += self.flows.get_flow_right()
    #    self.pools_bus[2] += self.flows.get_flow_bus_right()

    # tick based update
    def simulateUpdate(self, trafficLights, trafficlight_timing):
        # Dequeue cars
        spaces_in_lanes = []
        vehicles_before = self.get_total_vehicles()
        for lane in self.lanes:
            if (trafficLights in TrafficLights.NORTH_SOUTH_RIGHT) and (
                    self.flows.get_direction_from() in Dir.NORTH | Dir.SOUTH):
                lane.simulate_update([right_of(self.flows.get_direction_from())], trafficlight_timing)
            elif (trafficLights in TrafficLights.NORTH_SOUTH_OTHER) and (
                    self.flows.get_direction_from() in Dir.NORTH | Dir.SOUTH):
                lane.simulate_update(
                    [left_of(self.flows.get_direction_from()), opposite_of(self.flows.get_direction_from())],
                    trafficlight_timing)
            elif (trafficLights in TrafficLights.EAST_WEST_RIGHT) and (
                    self.flows.get_direction_from() in Dir.EAST | Dir.WEST):
                lane.simulate_update([right_of(self.flows.get_direction_from())], trafficlight_timing)
            elif (trafficLights in TrafficLights.EAST_WEST_OTHER) and (
                    self.flows.get_direction_from() in Dir.EAST | Dir.WEST):
                lane.simulate_update(
                    [left_of(self.flows.get_direction_from()), opposite_of(self.flows.get_direction_from())],
                    trafficlight_timing)

            spaces_in_lanes.append(lane.get_no_available_spaces())  # How many free spaces are there

        if self.calculating_max_wait and vehicles_before != 0:
            self.max_wait += trafficlight_timing

        # print("before sticky loop")

        # Enqueue cars / add them into the lanes from each pool
        self.enqueue_to_lanes(spaces_in_lanes)
        
        # print("completed sticky loop")
        # Calculating max length
        max_lane = 0
        for lane in self.lanes:
            if lane.get_num_vehicles() > max_lane:
                max_lane = lane.get_num_vehicles()

        max_candidate = max_lane + math.ceil((len(self.p_ahead_b) + len(self.p_ahead_c) + len(self.p_left_b) + len(self.p_left_c) + len(self.p_right_b) + len(self.p_right_c)) / len(self.lanes))
        if max_candidate > self.max_length:
            self.max_length = max_candidate

    def add_to_pools(self, seconds):
        self.residuals[0] += (seconds * self.flows.get_flow_left() / 3600)
        #self.pools[0] += math.floor(self.residuals[0])
        for i in range(0, math.floor(self.residuals[0])):
            self.p_left_c.append(Vehicle(self.flows.get_direction_from(), left_of(self.flows.get_direction_from()),
                                VehicleType.CAR))
        self.residuals[0] -= math.floor(self.residuals[0])

        self.residuals[1] += (seconds * self.flows.get_flow_ahead() / 3600)
        #self.pools[1] += math.floor(self.residuals[1])
        for i in range(0, math.floor(self.residuals[1])):
            self.p_ahead_c.append(Vehicle(self.flows.get_direction_from(), opposite_of(self.flows.get_direction_from()),
                                VehicleType.CAR))
        self.residuals[1] -= math.floor(self.residuals[1])

        self.residuals[2] += (seconds * self.flows.get_flow_right() / 3600)
        #self.pools[2] += math.floor(self.residuals[2])
        for i in range(0, math.floor(self.residuals[2])):
            self.p_right_c.append(Vehicle(self.flows.get_direction_from(), right_of(self.flows.get_direction_from()),
                                VehicleType.CAR))
        self.residuals[2] -= math.floor(self.residuals[2])

        self.bus_residuals[0] += (seconds * self.flows.get_flow_bus_left() / 3600)
        #self.pools_bus[0] += math.floor(self.bus_residuals[0])
        for i in range(0, math.floor(self.bus_residuals[0])):
            self.p_left_b.append(Vehicle(self.flows.get_direction_from(), left_of(self.flows.get_direction_from()),
                                VehicleType.BUS))
        self.bus_residuals[0] -= math.floor(self.bus_residuals[0])

        self.bus_residuals[1] += (seconds * self.flows.get_flow_bus_ahead() / 3600)
        #self.pools_bus[1] += math.floor(self.bus_residuals[1])
        for i in range(0, math.floor(self.bus_residuals[1])):
            self.p_ahead_b.append(Vehicle(self.flows.get_direction_from(), opposite_of(self.flows.get_direction_from()),
                                VehicleType.BUS))
        self.bus_residuals[1] -= math.floor(self.bus_residuals[1])

        self.bus_residuals[2] += (seconds * self.flows.get_flow_bus_right() / 3600)
        #self.pools_bus[2] += math.floor(self.bus_residuals[2])
        for i in range(0, math.floor(self.bus_residuals[2])):
            self.p_right_b.append(Vehicle(self.flows.get_direction_from(), right_of(self.flows.get_direction_from()),
                                VehicleType.BUS))
        self.bus_residuals[2] -= math.floor(self.bus_residuals[2])

        spaces_in_lanes = []
        for lane in self.lanes:
            spaces_in_lanes.append(lane.get_no_available_spaces())
        
        self.enqueue_to_lanes(spaces_in_lanes)

    def enqueue_to_lanes(self, spaces_in_lanes):
        while sum(spaces_in_lanes) != 0:  # Include condition for if there aren't any more cars to add
            index = 0
            emptiest_lane = spaces_in_lanes[0]  # spaces is the array of number of available spaces in each lane

            # print(f"in sticky loop index:{index}, spaces:{spaces}")

            for i in range(1, len(spaces_in_lanes)):  # Get lane with most empty spaces
                if spaces_in_lanes[i] > emptiest_lane:
                    emptiest_lane = spaces_in_lanes[i]
                    index = i

            # Condition for adding cars
            lane = self.lanes[index]

            # lane goes left or ahead
            if lane.goes_to(left_of(self.flows.get_direction_from())) and not lane.goes_to(right_of(
                    self.flows.get_direction_from())):  # Lane with left turn but no right turn (might have ahead)
                if len(self.p_left_c) > 0:
                    lane.add_vehicle(self.p_left_c.pop(0))
                    spaces_in_lanes[index] -= 1
                elif lane.goes_to(opposite_of(self.flows.get_direction_from())) and len(self.p_ahead_c) > 0:
                    lane.add_vehicle(self.p_ahead_c.pop(0))
                    spaces_in_lanes[index] -= 1
                elif self.p_left_b > 0:
                    lane.add_vehicle(self.p_left_b.pop(0))
                    spaces_in_lanes[index] -= 1
                elif lane.goes_to(opposite_of(self.flows.get_direction_from())) and len(self.p_ahead_b) > 0:
                    lane.add_vehicle(self.p_ahead_b.pop(0))
                    spaces_in_lanes[index] -= 1
                else:
                    spaces_in_lanes[index] = 0  # If we couldn't add anything to the lane, pretend the lane is full
                # if lane.is_bus_lane:
                #     if self.pools_bus[0] > 0:
                #         lane.add_vehicle(Vehicle(self.flows.get_direction_from(), left_of(self.flows.get_direction_from()), VehicleType.BUS))
                #         spaces[index] -= 1
                #         self.pools_bus[0] -= 1
                #     elif self.pools_bus[1] > 0:
                #         lane.add_vehicle(Vehicle(self.flows.get_direction_from(), opposite_of(self.flows.get_direction_from()), VehicleType.BUS))
                #         self.pools_bus[1] -= 1
                #         spaces[index] -= 1
                # else:
                #     if self.pools[0] > 0:
                #         lane.add_vehicle(Vehicle(self.flows.get_direction_from(), left_of(self.flows.get_direction_from()), VehicleType.CAR))
                #         spaces[index] -= 1
                #         self.pools[0] -= 1
                #     elif self.pools[1] > 0:
                #         lane.add_vehicle(Vehicle(self.flows.get_direction_from(), opposite_of(self.flows.get_direction_from()), VehicleType.CAR))
                #         spaces[index] -= 1
                #         self.pools[1] -= 1
                #     else:
                #         spaces[index] = 0
            # the lane goes to the right or ahead
            elif lane.goes_to(right_of(self.flows.get_direction_from())) and not lane.goes_to(
                    left_of(self.flows.get_direction_from())):  # Lane with right turn but no left turn (might have ahead)
                if len(self.p_right_c) > 0 or len(self.p_right_b) > 0:
                    vehicle = None
                    if len(self.p_right_c) > 0 and len(self.p_right_b) > 0:
                        choice = random.randint(0, 1)
                        if choice == 1:
                            vehicle = self.p_right_c.pop(0)
                        else:
                            vehicle = self.p_right_b.pop(0)
                    elif len(self.p_right_c) > 0:
                        vehicle = self.p_right_c.pop(0)
                    else:
                        vehicle = self.p_right_b.pop(0)

                    lane.add_vehicle(vehicle)
                    spaces_in_lanes[index] -= 1
                elif lane.goes_to(opposite_of(self.flows.get_direction_from())) and len(self.p_ahead_c):  # Don't technically need the third condition since we don't have right turning bus lanes
                    lane.add_vehicle(self.p_ahead_c.pop(0))
                    spaces_in_lanes[index] -= 1
                else:
                    spaces_in_lanes[index] = 0  # If we couldn't add anything to the lane, pretend the lane is full
            # lane goes ahead only
            elif not lane.goes_to(left_of(self.flows.get_direction_from())) and not lane.goes_to(
                    right_of(self.flows.get_direction_from())):  # Lane with only ahead (no left turn nor right turn)
                if lane.goes_to(opposite_of(self.flows.get_direction_from())) and len(self.p_ahead_c) > 0:
                    lane.add_vehicle(self.p_ahead_c.pop(0))
                    spaces_in_lanes[index] -= 1
                elif lane.goes_to(opposite_of(self.flows.get_direction_from())) and len(self.p_ahead_b) > 0:
                    lane.add_vehicle(self.p_ahead_b.pop(0))
                    spaces_in_lanes[index] -= 1
                else:
                    spaces_in_lanes[index] = 0  # If we couldn't add anything to the lane, pretened the lane is full
            else:  # Lane with left, ahead and right
                directions = []
                if len(self.p_left_c) > 0:
                    directions.append(left_of(self.flows.get_direction_from()))
                if len(self.p_ahead_c) > 0:
                    directions.append(opposite_of(self.flows.get_direction_from()))
                if len(self.p_right_c) > 0:
                    directions.append(right_of(self.flows.get_direction_from()))

                if directions:  #NEEDS EDITING
                    direction = random.choice(directions)
                    if direction == left_of(self.flows.get_direction_from()):
                        vehicle = self.p_left_c.pop(0)
                    elif direction == opposite_of(self.flows.get_direction_from()):
                        vehicle = self.p_ahead_c.pop(0)
                    else:
                        vehicle = self.p_right_c.pop(0)
                    lane.add_vehicle(vehicle)
                    spaces_in_lanes[index] -= 1
                else:
                    spaces_in_lanes[index] = 0
    
    def get_total_vehicles(self):
        return len(self.p_ahead_b) + len(self.p_ahead_c) + len(self.p_left_b) + len(self.p_left_c) + len(self.p_right_b) + len(self.p_right_c) + sum([lane.get_num_vehicles() for lane in self.lanes])

    def set_calculating_max_wait(self, bool):
        self.calculating_max_wait = bool

    def get_max_length(self) -> int:
        return self.max_length

    def get_max_wait(self) -> float:
        return self.max_wait

    def get_avg_wait(self) -> float:
        return self.avg_wait
