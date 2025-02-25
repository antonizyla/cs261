import random
from flowrates import FlowRates
from lane import Lane, left_of, right_of, opposite_of, Dir
from params import Parameters
from vehicle import Vehicle, VehicleType
from Junction import TrafficLights


class Direction:
    def __init__(self, flows: FlowRates, num_lanes: int):
        self.flows = FlowRates
        self.pools: [int] = [0, 0, 0]
        self.pools_bus: [int] = [0,0,0]
        self.max_wait = None
        self.max_length = None
        self.avg_wait = None
        self.lanes = []
        if num_lanes == 1:
            self.lanes.append(Lane(5, flows.direction_from, [left_of(flows.direction_from), right_of(flows.direction_from), opposite_of(flows.direction_from)]))
        else:
            if flows.dedicated_left:
                self.lanes.append(Lane(5, flows.direction_from, [left_of(flows.direction_from)]))
                num_lanes -= 1
            elif flows.dedicated_right:
                self.lanes.append(Lane(5, flows.direction_from, [right_of(flows.direction_from)]))
                num_lanes -= 1
            for i in range(num_lanes - len(self.lanes)):
                self.lanes.append(Lane(5, flows.direction_from, [opposite_of(flows.direction_from)]))

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
                lane.simulate_update(right_of(self.flows.get_direction_from()), trafficlight_timing)
            elif (trafficLights in TrafficLights.NORTH_SOUTH_OTHER) and (self.flows.get_direction_from() in Dir.NORTH | Dir.SOUTH):
                lane.simulate_update(left_of(self.flows.get_direction_from()) | opposite_of(self.flows.get_direction_from()), trafficlight_timing)
            elif (trafficLights in TrafficLights.EAST_WEST_RIGHT) and (self.flows.get_direction_from() in Dir.EAST | Dir.WEST):
                lane.simulate_update(right_of(self.flows.get_direction_from()), trafficlight_timing)
            elif (trafficLights in TrafficLights.EAST_WEST_OTHER) and (self.flows.get_direction_from() in Dir.EAST | Dir.WEST):
                lane.simulate_update(left_of(self.flows.get_direction_from()) | opposite_of(self.flows.get_direction_from()), trafficlight_timing)
            
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
            rand_int = random.randint(0, 3)
            direction = None
            for i in range(0, 4):
                if rand_int == 0:
                    direction = Dir.NORTH
                elif rand_int == 1:
                    direction = Dir.EAST
                elif rand_int == 2:
                    direction = Dir.SOUTH
                elif rand_int == 3:
                    direction = Dir.WEST
                
                #Need to consider busses heading right - extra condition?
                #Still need to consider giving priority to left if left and ahead lane
                if self.pools[direction] > 0 and (not lane.is_bus_lane) and lane.goes_to(direction): #NEED TO DEFINE LANE SOMEWHERE
                    self.lanes[index].add_vehicle(Vehicle(self.flows.get_direction_from(), direction, VehicleType.CAR))
                    spaces[index] -= 1
                    self.pools[direction] -= 1
                    break
                elif self.pools_bus[direction] > 0 and lane.is_bus_lane and lane.goes_to(direction): #NEED TO DEFINE LANE SOMEWHERE
                    self.lanes[index].add_vehicle(Vehicle(self.flows.get_direction_from(), direction, VehicleType.BUS))
                    spaces[index] -= 1
                    self.pools_bus[direction] -= 1
                    break
                else:
                    rand_int = (rand_int + 1) % 4
                    if (i == 3): #If we couldn't add anything to the lane, pretened the lane is full
                        spaces[index] = 0

    def get_max_length(self) -> int:
        return self.max_length
    def get_max_wait(self)-> float:
        return self.max_wait
    def get_avg_wait(self) -> float:
        return self.avg_wait
