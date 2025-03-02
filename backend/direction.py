import random
from flowrates import FlowRates
from lane import Lane, left_of, right_of, opposite_of, Dir
from params import Parameters
from vehicle import Vehicle, VehicleType
from Junction import TrafficLights


class Direction:
    def __init__(self, flows: FlowRates, num_lanes: int):
        self.flows = FlowRates
        self.pools: list[int] = [0, 0, 0]
        self.pools_bus: list[int] = [0,0,0]
        self.max_wait = None
        self.max_length = None
        self.avg_wait = None
        self.lanes = []
        if num_lanes == 1:
            self.lanes.append(Lane(60, flows.direction_from, [left_of(flows.direction_from), right_of(flows.direction_from), opposite_of(flows.direction_from)]))
        else:
            if flows.dedicated_left:
                self.lanes.append(Lane(60, flows.direction_from, [left_of(flows.direction_from)]))
                num_lanes -= 1
            elif flows.dedicated_right:
                self.lanes.append(Lane(60, flows.direction_from, [right_of(flows.direction_from)]))
                num_lanes -= 1
            for i in range(num_lanes - len(self.lanes)):
                self.lanes.append(Lane(60, flows.direction_from, [opposite_of(flows.direction_from)]))

    # hourly/longer period update
    def simulate_hourly(self):
        # working on assumption that bus flows are on top of flow for the direction
        self.pools[0] += self.flows.get_flow_left()
        self.pools_bus[0] += self.flows.get_flow_bus_left()

        self.pools[1] += self.flows.get_flow_ahead()
        self.pools_bus[1] += self.flows.get_flow_bus_ahead()

        self.pools[2] += self.flows.get_flow_right()
        self.pools_bus[2] += self.flows.get_flow_bus_right()

    # tick based update
    def simulateUpdate(self, trafficLights, trafficlight_timing):
        #Dequeue cars
        spaces = []
        for lane in self.lanes:
            if (trafficLights in TrafficLights.NORTH_SOUTH_RIGHT) and (self.flows.get_direction_from() in Dir.NORTH | Dir.SOUTH):
                lane.simulate_update(right_of(self.flows.get_direction_from()), 60)
            elif (trafficLights in TrafficLights.NORTH_SOUTH_OTHER) and (self.flows.get_direction_from() in Dir.NORTH | Dir.SOUTH):
                lane.simulate_update(left_of(self.flows.get_direction_from()) | opposite_of(self.flows.get_direction_from()), 60)
            elif (trafficLights in TrafficLights.EAST_WEST_RIGHT) and (self.flows.get_direction_from() in Dir.EAST | Dir.WEST):
                lane.simulate_update(right_of(self.flows.get_direction_from()), 60)
            elif (trafficLights in TrafficLights.EAST_WEST_OTHER) and (self.flows.get_direction_from() in Dir.EAST | Dir.WEST):
                lane.simulate_update(left_of(self.flows.get_direction_from()) | opposite_of(self.flows.get_direction_from()), 60)
            
            spaces.append(lane.get_queue_limit() - lane.get_no_vehicle_present()) #How many free spaces are there

        #Enqueue cars
        while sum(spaces) != 0: #Include condition for if there aren't any more cars to add
            index = 0
            max = spaces[0]
            for i in range(1, len(spaces)): #Get lane with most empty spaces
                if spaces[i] > max:
                    max = spaces[i]
                    index = i
            
            #Condition for adding cars
            lane = self.lanes[index]

            if (lane.goes_to(left_of(self.flows.get_direction_from())) and not lane.goes_to(right_of(self.flows.get_direction_from()))): #Lane with left turn but no right turn (might have ahead)
                if self.pools[0] > 0 and not lane.is_bus_lane:
                    lane.add_vehicle(Vehicle(self.flows.get_direction_from(), left_of(self.flows.get_direction_from()), VehicleType.CAR))
                    spaces[index] -= 1
                    self.pools[0] -= 1
                elif (lane.goes_to(opposite_of(self.flows.get_direction_from())) and self.pools[1] > 0 and not lane.is_bus_lane):
                    lane.add_vehicle(Vehicle(self.flows.get_direction_from(), opposite_of(self.flows.get_direction_from()), VehicleType.CAR))
                    spaces[index] -= 1
                    self.pools[1] -= 1
                elif self.pools_bus[0] > 0 and lane.is_bus_lane:
                    lane.add_vehicle(Vehicle(self.flows.get_direction_from(), left_of(self.flows.get_direction_from()), VehicleType.BUS))
                    spaces[index] -= 1
                    self.pools_bus[0] -= 1
                elif (lane.goes_to(opposite_of(self.flows.get_direction_from())) and self.pools_bus[1] > 0 and lane.is_bus_lane):
                    lane.add_vehicle(Vehicle(self.flows.get_direction_from(), opposite_of(self.flows.get_direction_from()), VehicleType.BUS))
                    spaces[index] -= 1
                    self.pools_bus[1] -= 1
                else:
                    spaces[index] = 0 #If we couldn't add anything to the lane, pretened the lane is full
            elif (lane.goes_to(right_of(self.flows.get_direction_from())) and not lane.goes_to(left_of(self.flows.get_direction_from()))): #Lane with right turn but no left turn (might have ahead)
                if self.pools[2] > 0 or self.pools_bus[2] > 0:
                    vehicle = None
                    if self.pools[2] > 0 and self.pools_bus[2] > 0:
                        vehicle = random.choice([VehicleType.CAR, VehicleType.BUS])
                    elif self.pools[2] > 0:
                        vehicle = VehicleType.CAR
                    else:
                        vehicle = VehicleType.BUS
                    
                    lane.add_vehicle(Vehicle(self.flows.get_direction_from(), right_of(self.flows.get_direction_from()), vehicle))
                    spaces[index] -= 1
                    if vehicle == VehicleType.CAR:
                        self.pools[2] -= 1
                    else:
                        self.pools_bus[2] -= 1
                elif (lane.goes_to(opposite_of(self.flows.get_direction_from())) and self.pools[1] > 0 and not lane.is_bus_lane): #Don't technically need the third condition since we don't have right turning bus lanes
                    lane.add_vehicle(Vehicle(self.flows.get_direction_from(), opposite_of(self.flows.get_direction_from()), VehicleType.CAR))
                    spaces[index] -= 1
                    self.pools[1] -= 1
                else:
                    spaces[index] = 0 #If we couldn't add anything to the lane, pretened the lane is full
            elif (not lane.goes_to(left_of(self.flows.get_direction_from())) and not lane.goes_to(right_of(self.flows.get_direction_from()))): #Lane with only ahead (no left turn nor right turn)
                if (lane.goes_to(opposite_of(self.flows.get_direction_from())) and self.pools[1] > 0 and not lane.is_bus_lane):
                    lane.add_vehicle(Vehicle(self.flows.get_direction_from(), opposite_of(self.flows.get_direction_from()), VehicleType.CAR))
                    spaces[index] -= 1
                    self.pools[1] -= 1
                elif (lane.goes_to(opposite_of(self.flows.get_direction_from())) and self.pools_bus[1] > 0 and lane.is_bus_lane):
                    lane.add_vehicle(Vehicle(self.flows.get_direction_from(), opposite_of(self.flows.get_direction_from()), VehicleType.BUS))
                    spaces[index] -= 1
                    self.pools_bus[1] -= 1
                else:
                    spaces[index] = 0 #If we couldn't add anything to the lane, pretened the lane is full
            else: #Lane with left, ahead and right
                directions = []
                if self.pools[0] > 0:
                    directions.append(left_of(self.flows.get_direction_from()))
                if self.pools[1] > 0:
                    directions.append(opposite_of(self.flows.get_direction_from()))
                if self.pools[2] > 0:
                    directions.append(right_of(self.flows.get_direction_from()))

                if directions != []:
                    direction = random.choice(directions)
                    lane.add_vehicle(Vehicle(self.flows.get_direction_from(), direction, VehicleType.CAR))
                    spaces[index] -= 1
                    if direction == left_of(self.flows.get_direction_from()):
                        self.pools[0] -= 1
                    elif direction == opposite_of(self.flows.get_direction_from()):
                        self.pools[1] -= 1
                    else:
                        self.pools[2] -= 1
                else:
                    spaces[index] = 0
    
        #Calculating max length
        max_lane = 0
        for lane in self.lanes:
            if lane.get_num_vehicles() > max_lane:
                max_lane = lane.get_num_vehicles()

        if max_lane + math.ceil(sum(self.pools) / len(self.lanes)) > self.max_length:
            self.max_length = max_lane + math.ceil(sum(self.pools) / len(self.lanes))

    def get_max_length(self) -> int:
        return self.max_length
    def get_max_wait(self)-> float:
        return self.max_wait
    def get_avg_wait(self) -> float:
        return self.avg_wait
