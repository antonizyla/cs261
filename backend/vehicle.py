from enum import Flag, auto


class VehicleType(Flag):
    CAR = auto()
    BUS = auto()


class Vehicle:
    def __init__(self, direction_from, direction_to, time_entered, t=VehicleType.CAR):
        self.direction_from = direction_from
        self.direction_to = direction_to
        self.time_entered = time_entered
        self.type = t

    def getDirectionFrom(self):
        return self.direction_from

    def getDirectionTo(self):
        return self.direction_to

    def getTimeEntered(self):
        return self.time_entered
