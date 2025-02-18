from enum import Flag, auto

class Dir(Flag):
    WEST = auto()
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()


class Lane:
    def __init__(self, queue_limit, dir_from, dir_to):
        self.currentVehicles = []
        self.queueLimit = queue_limit
        self.flowing = False
        self.directionTo = dir_to
        self.directionFrom = dir_from

    def get_num_vehicles(self):
        return len(self.currentVehicles)
    
    def add_vehicle(self, vehicle):
        self.currentVehicles.append(vehicle)

    def goes_to(self, d: Dir) -> bool:
        return d in self.directionTo

    def simulate_update(self):
        #TODO
        pass