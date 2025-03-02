from enum import IntEnum, Enum
import sys
from pathlib import Path
sys.path.append((Path(__file__).parent.parent / 'backend').resolve().__str__())
from lane import Dir


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
        # Turn as if heading in cardinal direction
        if not isinstance(other, Turn):
            raise ValueError("Second argument of + must be an instance of Direction")
        return CardinalDirection((self.value + other.value) % 4)
    
    def __sub__(self, other: Turn):
        # Turn as if coming from cardinal direction
        if not isinstance(other, Turn):
            raise ValueError("Second argument of - must be an instance of Direction")
        return CardinalDirection((self.value - other.value) % 4)
    
    @classmethod
    def all_except_clockwise(cls, direction):
        # List of cardinal directions clockwise from exluded
        return [direction + Turn.RIGHT for i in range(3)]
    
    def all_except_anticlockwise(cls, direction):
        # List of cardinal directions clockwise from exluded
        return [direction + Turn.LEFT for i in range(3)]

    def simple_string(self):
        return ['north','east','south','west'][self.index]

    @property
    def index(self):
        return self.value
        