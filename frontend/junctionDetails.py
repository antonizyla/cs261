from enum import Enum
import sys
sys.path.append('../backend')
from flowrates import FlowRates
from lane import Dir
# Parameters and list of FlowRates [coming from north, east, south, west]

class Directions(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    def to_Dir(self):
        if self == Directions.NORTH:
            return Dir.NORTH
        elif self == Directions.EAST:
            return Dir.EAST
        elif self == Directions.SOUTH:
            return Dir.SOUTH
        else:
            return Dir.WEST

class JunctionDetails():
    arms = []

    def __iter__(self):
        return self.arms
    
    def __getitem__(self, index):
        return self.arms[index]