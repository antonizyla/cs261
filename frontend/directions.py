from enum import IntEnum, Enum
import sys
import sys
from pathlib import Path
sys.path.append((Path(__file__).parent.parent / 'backend').resolve().__str__())
from flowrates import FlowRates
from lane import Dir
# Parameters and list of FlowRates [coming from north, east, south, west]

class CardinalDirection(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    def to_Dir(self):
        if self.value == Direction.NORTH.value:
            return Dir.NORTH
        elif self.value == Direction.EAST.value:
            return Dir.EAST
        elif self.value == Direction.SOUTH.value:
            return Dir.SOUTH
        else:
            return Dir.WEST
    
    def __add__(self, other):
        if not isinstance(other, int):
            raise ValueError("Second argument of + must be of type: int")
        return CardinalDirection((self.value + other) % 4)
    
    def __sub__(self, other):
        if not isinstance(other, int):
            raise ValueError("Second argument of - must be of type: int")
        return CardinalDirection((self.value - other) % 4)
    
    def get_opposite(self):
        return self + 2

    def get_left(self):
        return self + 1
    
    def get_right(self):
        return self - 1
    
    def get_other_directions(self):
        return [self + i for i in range(1,4)]
    
    def index_from(self, other):
        return (self - other) % 4  
    
    def get_index_from_direction(self, base):
        return (self-base-1) % 4      

    def simple_string(self):
        return ['north','east','south','west'][self.index]

    @property
    def index(self):
        return self.value
        

class JunctionDetails():
    arms = []

    def __iter__(self):
        return iter(self.arms)
    
    def __getitem__(self, index):
        return self.arms[index]
    
    def get_FlowRate_list(self):
        return self.arms

print(Direction.NORTH)