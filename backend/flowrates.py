# for each direction, specify how much traffic goes into each of the other directions
from lane import Dir


class FlowRates:
    def __init__(self, dir_from, ahead: int, left: int, right: int, dedicated_left: bool, dedicated_bus: int,
                 dedicated_right: bool):
        self.dir_from = dir_from
        self.ahead:int = ahead
        self.left:int = left
        self.right:int = right
        self.dedicated_left:bool = dedicated_left  # left dedicated and bus lane are mutually exclusive
        self.dedicated_bus:int = dedicated_bus
        self.dedicated_right:bool = dedicated_right

    def get_direction_from(self):
        return self.dir_from

    def check(self):
        if self.dedicated_bus > 0 and self.dedicated_left:
            return False
        if self.ahead < 0 or self.right < 0 or self.right < 0:
            return False
        return True

    def get_flow_ahead(self):
        return self.ahead

    def get_flow_left(self):
        return self.left

    def get_flow_right(self):
        return self.right

    def get_flow_ded_left(self):
        if self.dedicated_bus:
            return 0
        else:
            return self.dedicated_left

    def get_flow_bus_left(self):
        return self.dedicated_bus * (self.left / (self.ahead + self.left + self.right))

    def get_flow_bus_ahead(self):
        return self.dedicated_bus * (self.ahead / (self.ahead + self.left + self.right))

    def get_flow_bus_total(self):
        return self.dedicated_bus

    def get_flow_bus(self):
        # the flow in the actual bus lane (right turn buses go in other lanes)
        return self.get_flow_bus_ahead() + self.get_flow_bus_left()

    def get_flow_bus_right(self):
        return self.get_flow_bus_total() - self.get_flow_bus()

    def get_flow_ded_right(self):
        return

    def get_flow_total(self):
        # bus flows are not counted in the total for junction but follow same proportion
        return self.right + self.left + self.ahead + self.get_flow_bus_total()
