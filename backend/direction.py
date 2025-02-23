import random
from flowrates import FlowRates
from lane import Lane, left_of, right_of, opposite_of, Dir
from params import Parameters
from vehicle import Vehicle, VehicleType
from Junction import TrafficLights


class Direction:
    def __init__(self, flows: FlowRates, num_lanes: int):
        self.flows = FlowRates
        self.ahead_pool = []
        self.left_pool = []
        self.right_pool = []
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
        direction_from: Dir = self.flows.get_direction_from()
        going_left = left_of(direction_from)
        going_right = right_of(direction_from)
        going_ahead = opposite_of(direction_from)

        # ahead, bus and cars
        self.ahead_pool.append([Vehicle(direction_from, going_ahead, VehicleType.BUS) for x in range(self.flows.get_flow_bus_ahead())])
        self.ahead_pool.append([Vehicle(direction_from, going_ahead) for x in range(self.flows.get_flow_ahead())])
        # left going traffic
        self.left_pool.append([Vehicle(direction_from, going_left) for x in range(self.flows.get_flow_left())])
        self.left_pool.append([Vehicle(direction_from, going_left, VehicleType.BUS) for x in range(self.flows.get_flow_bus_left())])
        # right going traffic
        self.right_pool.append([Vehicle(direction_from, going_right, VehicleType.BUS) for x in range(self.flows.get_flow_bus_right())])
        self.right_pool.append([Vehicle(direction_from, going_right) for x in range(self.flows.get_flow_right())])

    # tick based update
    def simulateUpdate(self, trafficLights):
        #Dequeue cars
        spaces = []
        for lane in self.lanes:
            if (trafficLights in TrafficLights.NORTH_SOUTH_RIGHT) && (self.flows.get_direction_from() in Dir.NORTH || Dir.SOUTH):
                lane.simulate_update(right_of(self.flows.get_direction_from()))
            elif (trafficLights in TrafficLights.NORTH_SOUTH_OTHER) && (self.flows.get_direction_from() in Dir.NORTH || Dir.SOUTH):
                lane.simulate_update(left_of(self.flows.get_direction_from()) || opposite_of(self.flows.get_direction_from()))
            elif (trafficLights in TrafficLights.EAST_WEST_RIGHT) && (self.flows.get_direction_from() in Dir.EAST || Dir.WEST):
                lane.simulate_update(right_of(self.flows.get_direction_from()))
            elif (trafficLights in TrafficLights.EAST_WEST_OTHER) && (self.flows.get_direction_from() in Dir.EAST || Dir.WEST):
                lane.simulate_update(left_of(self.flows.get_direction_from()) || opposite_of(self.flows.get_direction_from()))
            
            spaces.append(lane.get_queue_limit() - lane.get_no_vehicle_present()) #How many free spaces are there

        #Enqueue cars
        while sum(spaces) != 0: #Include condition for if there aren't any more cars to add
            index = 0;
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
                
                if self.pools[direction] > 0 and lane.goes_to(direction):
                    self.lanes[index].add_vehicle(Vehicle(self.flows.get_direction_from(), direction))
                    spaces[index] -= 1
                    self.pools[direction] -= 1
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
