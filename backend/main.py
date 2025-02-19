from junction import Junction
from lane import Lane, Dir
from params import Parameters

if __name__ == "main":
    # run a basic test configuration

    # create a basic junction
    northerly_lanes = [Lane(5, Dir.NORTH, [Dir.SOUTH, Dir.EAST]), Lane(5, Dir.NORTH, [Dir.SOUTH, Dir.EAST])]
    easterly_lanes = [Lane(5, Dir.EAST, [Dir.NORTH, Dir.WEST]), Lane(5, Dir.EAST, [Dir.WEST, Dir.SOUTH])]
    westerly_lanes= [Lane(5, Dir.WEST, [Dir.SOUTH, Dir.EAST]), Lane(5, Dir.NORTH, [Dir.NORTH, Dir.EAST])]
    southerly_lanes = [Lane(5, Dir.SOUTH, [Dir.NORTH, Dir.WEST]), Lane(5, Dir.EAST, [Dir.NORTH, Dir.EAST])]

    p = Parameters(3, False, None, False, None, None)
    p.generate_junction()

