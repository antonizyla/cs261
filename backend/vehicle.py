class Vehicle:
    def __init__(self, direction_from, direction_to):
        self.direction_from = direction_from
        self.direction_to = direction_to

    def getDirectionFrom(self):
        return self.direction_from
    
    def getDirectionTo(self):
        return self.direction_to