from enum import Flag, auto

class Dir(Flag):
    WEST = auto()
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()

def left_of(d: Dir):
    if d is Dir.NORTH:
        return Dir.WEST
    elif d is Dir.EAST:
        return Dir.NORTH
    elif d is Dir.SOUTH:
        return Dir.EAST
    else:
        return Dir.SOUTH

def right_of(d: Dir):
    return left_of(left_of(left_of(d))) # this is too funny to not leave

def opposite_of(d : Dir):
    return left_of(left_of(d))


class Lane:
    def __init__(self, queue_limit, dir_from, dir_to, bus=False):
        self.current_vehicles = []
        self.queue_limit = queue_limit
        self.flowing = False
        self.directions_to = dir_to
        self.direction_from = dir_from
        self.is_bus_lane = bus

    def get_num_vehicles(self):
        return len(self.current_vehicles)
    
    def add_vehicle(self, vehicle):
        self.current_vehicles.append(vehicle)

    def goes_to(self, d: Dir) -> bool:
        return d in self.directions_to

    def simulate_update(self, directions): #work in progress, may need to control range upper limit with traffic light duration
        for i in range(0, len(self.current_vehicles)):
            if self.current_vehicles[0].getDirectionTo in directions:
                self.current_vehicles[0].pop(0)
            else:
                break

    def get_queue_limit(self):
        return self.queue_limit

    def get_no_vehicle_present(self):
        return len(self.current_vehicles)