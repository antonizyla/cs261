from enum import Flag, auto


class VehicleType(Flag):
    CAR = auto()
    BUS = auto()


class Vehicle:
    def __init__(self, direction_from, direction_to, time_entered, t=VehicleType.CAR):
        self.direction_from = direction_from
        self.direction_to = direction_to
        self.time_entered:int = time_entered
        self.type = t

    def get_direction_from(self):
        return self.direction_from

    def get_direction_to(self):
        return self.direction_to

    def get_time_entered(self) -> int:
        return self.time_entered
