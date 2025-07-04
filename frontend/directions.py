from enum import IntEnum, Enum
import sys
from backend.lane import Dir


class Turn(Enum):
    AHEAD = 0
    RIGHT = 1
    BACK = 2
    LEFT = 3
    
    def __neg__(self):
        return Turn((self.value + 2) % 4)
    
class CardinalDirection(Enum):
    # All methods which return a list will return the list in clockwise order
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    def to_Dir(self):
        return [Dir.NORTH, Dir.EAST, Dir.SOUTH, Dir.WEST][self.index]
    
    def __add__(self, other: Turn):
        # Turn as if heading in cardinal direction (right turns clockwise)
        if not isinstance(other, Turn):
            raise ValueError("Second argument of + must be an instance of Direction")
        return CardinalDirection((self.value + other.value) % 4)
    
    def __sub__(self, other: Turn):
        # Turn as if coming from cardinal direction (right turns anticlockwise)
        if not isinstance(other, Turn):
            raise ValueError("Second argument of - must be an instance of Direction")
        return CardinalDirection((self.value - other.value) % 4)
    
    @classmethod
    def all_except_clockwise(cls, direction):
        # List of cardinal directions clockwise from exluded
        TheDs = []
        for i in range(3):
            direction = (direction + Turn.RIGHT)
            TheDs.append(direction)
        return TheDs
        return [direction + Turn.RIGHT for i in range(3)] #This is an error, it has the same direction + right 3 times
    
    def all_except_anticlockwise(cls, direction):
        # List of cardinal directions clockwise from exluded
        TheDs = []
        for i in range(3):
            direction = (direction + Turn.LEFT)
            TheDs.append(direction)
        return TheDs
        return [direction + Turn.LEFT for i in range(3)] #This is an error, it has the same direction + left 3 times

    def simple_string(self):
        return ['north','east','south','west'][self.index]

    @property
    def index(self):
        return self.value
        