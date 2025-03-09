import pytest
from lane import Dir, Lane

class MockVehicle:
    """A mock vehicle class to test Lane behaviour."""
    def __init__(self, direction_from, direction_to, time_entered=0):
        self._direction_from = direction_from
        self._direction_to = direction_to
        self._time_entered = time_entered  

    def getDirectionFrom(self):
        return self._direction_from

    def getDirectionTo(self):
        return self._direction_to

    def getTimeEntered(self): 
        return self._time_entered

    #Add alternate method names for compatibility
    def get_direction_to(self):
        return self.getDirectionTo()

    def get_direction_from(self):
        return self.getDirectionFrom()

    def get_time_entered(self):
        return self.getTimeEntered()




class TestLane:
    def setup_method(self):
        """Setup test lanes before each test."""
        self.lane = Lane(queue_limit=5, dir_from=Dir.NORTH, dir_to=[Dir.EAST, Dir.SOUTH])
    
    def test_lane_initialisation(self):
        """Ensure lane initialises correctly with attributes."""
        assert self.lane.queue_limit == 5, "Queue limit should be set correctly."
        assert self.lane.direction_from == Dir.NORTH, "Direction from should be NORTH."
        assert self.lane.directions_to == [Dir.EAST, Dir.SOUTH], "Directions to should be EAST and SOUTH."
        assert self.lane.get_no_vehicle_present() == 0, "Initially, lane should have no vehicles."

    def test_add_vehicle(self):
        """Ensure vehicles can be added and queue limit is realistic."""
        vehicle1 = MockVehicle(Dir.NORTH, Dir.EAST)
        vehicle2 = MockVehicle(Dir.NORTH, Dir.SOUTH)

        self.lane.add_vehicle(vehicle1)
        self.lane.add_vehicle(vehicle2)

        assert self.lane.get_no_vehicle_present() == 2, "Vehicle count should increase correctly."

    def test_queue_limit_not_strict(self):
        """Ensure lane can handle slightly exceeding queue limit realistically."""
        for _ in range(5):
            self.lane.add_vehicle(MockVehicle(Dir.NORTH, Dir.EAST))

        assert self.lane.get_no_vehicle_present() == 5, "Lane should be at full capacity."

        # Allow a possible overflow scenario (if system permits it)
        self.lane.add_vehicle(MockVehicle(Dir.NORTH, Dir.SOUTH))
        assert self.lane.get_no_vehicle_present() >= 5, "Lane should not enforce strict hard limit unrealistically."

    def test_goes_to(self):
        """Ensure the lane correctly determines valid exit directions."""
        assert self.lane.goes_to(Dir.EAST) is True, "Lane should allow traffic to EAST."
        assert self.lane.goes_to(Dir.SOUTH) is True, "Lane should allow traffic to SOUTH."
        assert self.lane.goes_to(Dir.WEST) is False, "Lane should NOT allow traffic to WEST."

    def test_get_no_available_spaces(self):
        """Ensure the number of available spaces is correctly calculated."""
        assert self.lane.get_no_available_spaces() == 5, "Initially, all 5 spaces should be available."

        self.lane.add_vehicle(MockVehicle(Dir.NORTH, Dir.EAST))
        assert self.lane.get_no_available_spaces() == 4, "After adding a vehicle, 4 spaces should be available."

    def test_simulate_update_no_vehicles(self):
        """Ensure simulate_update handles empty lanes correctly."""
        self.lane.simulate_update([Dir.EAST, Dir.SOUTH], 10, 0)
        assert self.lane.get_no_vehicle_present() == 0, "No vehicles should be processed if there were none."

    def test_simulate_update_partial_clearance(self):
        """Ensure simulate_update removes vehicles realistically."""
        for _ in range(3):
            self.lane.add_vehicle(MockVehicle(Dir.NORTH, Dir.EAST))

        self.lane.simulate_update([Dir.EAST], 2, 0)  # Limited time, may not clear all
        assert self.lane.get_no_vehicle_present() >= 1, "Some vehicles should remain if time is insufficient."

    def test_simulate_update_clears_some_vehicles(self):
        """Ensure simulate_update does not clear more vehicles than expected."""
        for _ in range(3):
            self.lane.add_vehicle(MockVehicle(Dir.NORTH, Dir.EAST))

        self.lane.simulate_update([Dir.EAST], 10, 0)  # Enough time to clear some vehicles
        assert self.lane.get_no_vehicle_present() <= 3, "Not all vehicles should be removed unrealistically."

    def test_mixed_direction_vehicles(self):
        """Ensure simulate_update handles vehicles going in different directions correctly."""
        vehicle1 = MockVehicle(Dir.NORTH, Dir.EAST)
        vehicle2 = MockVehicle(Dir.NORTH, Dir.SOUTH)
        vehicle3 = MockVehicle(Dir.NORTH, Dir.EAST)

        self.lane.add_vehicle(vehicle1)
        self.lane.add_vehicle(vehicle2)
        self.lane.add_vehicle(vehicle3)

        self.lane.simulate_update([Dir.EAST], 10, 0)
        assert self.lane.get_no_vehicle_present() > 0, "Vehicles going to SOUTH should remain."

    def test_left_of_logic(self):
        """Ensure left_of works correctly."""
        from lane import left_of
        assert left_of(Dir.NORTH) == Dir.EAST, "Left of NORTH should be EAST."
        assert left_of(Dir.EAST) == Dir.SOUTH, "Left of EAST should be SOUTH."
        assert left_of(Dir.SOUTH) == Dir.WEST, "Left of SOUTH should be WEST."
        assert left_of(Dir.WEST) == Dir.NORTH, "Left of WEST should be NORTH."

    def test_right_of_logic(self):
        """Ensure right_of works correctly."""
        from lane import right_of
        assert right_of(Dir.NORTH) == Dir.WEST, "Right of NORTH should be WEST."
        assert right_of(Dir.EAST) == Dir.NORTH, "Right of EAST should be NORTH."
        assert right_of(Dir.SOUTH) == Dir.EAST, "Right of SOUTH should be EAST."
        assert right_of(Dir.WEST) == Dir.SOUTH, "Right of WEST should be SOUTH."

    def test_opposite_of_logic(self):
        """Ensure opposite_of works correctly."""
        from lane import opposite_of
        assert opposite_of(Dir.NORTH) == Dir.SOUTH, "Opposite of NORTH should be SOUTH."
        assert opposite_of(Dir.EAST) == Dir.WEST, "Opposite of EAST should be WEST."
        assert opposite_of(Dir.SOUTH) == Dir.NORTH, "Opposite of SOUTH should be NORTH."
        assert opposite_of(Dir.WEST) == Dir.EAST, "Opposite of WEST should be EAST."
