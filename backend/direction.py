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
    def simulateUpdate(self, trafficLights):
        #Dequeue cars
        spaces = []
        for lane in self.lanes:
            lane.simulateUpdate(trafficLights)
            spaces.append(lane.getQueueLimit() - lane.getNoVehicles()) #How many free spaces are there

        #Enqueue cars
        while (sum(spaces) != 0): #Include condition for if there aren't any more cars to add
            index = 0;
            max = spaces[0]
            for i in range(1, len(spaces)): #Get lane with most empty spaces
                if (spaces[i] > max):
                    max = spaces[i]
                    index = i
            
            #Condition for adding cars
            rand_int = random.randint(0, 3)
            dir = None
            for i in range(0, 4):
                if rand_int == 0:
                    dir = Dir.NORTH
                elif rand_int == 1:
                    dir = Dir.EAST
                elif rand_int == 2:
                    dir = Dir.SOUTH
                elif rand_int == 3:
                    dir = Dir.WEST
                
                if (self.pools[dir] > 0 && lane.goes_to(dir)):
                    self.lanes[index].add_vehicle(Vehicle(self.direction_from, dir))
                    spaces[index] -= 1
                    self.pools[dir] -= 1
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
