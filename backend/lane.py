from enum import Flag, auto


class Dir(Flag):
    WEST = auto()
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()


# left of as if going from direction d
def left_of(d: Dir):
    if d is Dir.NORTH:
        return Dir.EAST
    elif d is Dir.EAST:
        return Dir.SOUTH
    elif d is Dir.SOUTH:
        return Dir.WEST
    elif d is Dir.WEST:
        return Dir.NORTH
    return None


# left of as if facing that direction
def left_of_1(d: Dir):
    if d is Dir.NORTH:
        return Dir.WEST
    elif d is Dir.EAST:
        return Dir.NORTH
    elif d is Dir.SOUTH:
        return Dir.EAST
    else:
        return Dir.SOUTH


def right_of(d: Dir):
    return left_of(left_of(left_of(d)))  # this is too funny to not leave


def opposite_of(d: Dir):
    return left_of(left_of(d))


def contains(l: list[Dir], d: Dir):  # weird flag fuckery I have no idea how it works
    for x in l:
        if x == d:
            return True
    return False


class Lane:
    def __init__(self, queue_limit, dir_from, dir_to, bus=False):
        self.current_vehicles = []
        self.queue_limit = queue_limit
        self.flowing = False
        self.directions_to: list[Dir] = dir_to
        self.direction_from = dir_from
        self.is_bus_lane = bus
        self.maximum_vehicle_wait_time = 0

    def get_num_vehicles(self):
        return len(self.current_vehicles)

    def add_vehicle(self, vehicle):
        self.current_vehicles.append(vehicle)

    def goes_to(self, d: Dir) -> bool:
        return d in self.directions_to

    def simulate_update(self, directions: list[Dir],
                        traffic_light_time: int, time_elapsed):  # work in progress, may need to control range upper limit with traffic light duration
        timer:int = traffic_light_time
        first_flag:bool = True
        earliest_time:int = -1
        total_for_average:int = 0

        while timer > 0:  # Choose more appropriate constants/make dependent on number of lanes
            # if len(self.current_vehicles) > 0 and self.current_vehicles[0].getDirectionTo in directions:
            if len(self.current_vehicles) > 0 and self.current_vehicles[0].get_direction_to() in directions:
                if first_flag:  # First car will take a while to clear, but the cars after it will take less time since they can start moving while the one in front of it is in the junction
                    if self.current_vehicles[0].get_direction_to() == left_of(
                            self.current_vehicles[0].get_direction_from()):
                        timer -= 4
                    elif self.current_vehicles[0].get_direction_to() == opposite_of(
                            self.current_vehicles[0].get_direction_from()):
                        timer -= 6
                    elif self.current_vehicles[0].get_direction_to() == right_of(
                            self.current_vehicles[0].get_direction_from()):
                        timer -= 10

                    first_flag = False
                else:
                    timer -= 1  #Remembered right-turning cars from opposite directions turned before each other rather than after each other 
                    
                vehicle = self.current_vehicles.pop(0)
                total_for_average += (time_elapsed - vehicle.get_time_entered())
                if (time_elapsed - vehicle.get_time_entered()) > self.maximum_vehicle_wait_time:
                    self.maximum_vehicle_wait_time = time_elapsed - vehicle.get_time_entered()
                if not self.current_vehicles:
                    break
            else:
                break

        return [self.maximum_vehicle_wait_time, total_for_average] # [max time any car had to wait, sum of all cars wait times]

    def get_queue_limit(self):
        return self.queue_limit

    def get_no_vehicle_present(self):
        return len(self.current_vehicles)

    def get_no_available_spaces(self):
        return self.queue_limit - len(self.current_vehicles)
