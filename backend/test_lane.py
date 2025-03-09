import pytest
from lane import Dir, Lane

class MockVehicle:
    """A mock vehicle class to test Lane behavior."""
    def __init__(self, direction_from, direction_to):
        self._direction_from = direction_from
        self._direction_to = direction_to

    def getDirectionFrom(self):
        return self._direction_from

    def getDirectionTo(self):
        return self._direction_to


class TestLane:
    def setup_method(self):
        """Setup test lanes before each test."""
        self.lane = Lane(queue_limit=5, dir_from=Dir.NORTH, dir_to=[Dir.EAST, Dir.SOUTH])
    
    def test_lane_initialization(self):
        """Ensure lane initializes correctly with attributes."""
        assert self.lane.queue_limit == 5, "Queue limit should be set correctly."
        assert self.lane.direction_from == Dir.NORTH, "Direction from should be NORTH."
        assert self.lane.directions_to == [Dir.EAST, Dir.SOUTH], "Directions to should be EAST and SOUTH."
        assert self.lane.get_no_vehicle_present() == 0, "Initially, lane should have no vehicles."

    def test_add_vehicle(self):
        """Ensure vehicles can be added and queue limit is respected."""
        vehicle1 = MockVehicle(Dir.NORTH, Dir.EAST)
        vehicle2 = MockVehicle(Dir.NORTH, Dir.SOUTH)

        self.lane.add_vehicle(vehicle1)
        self.lane.add_vehicle(vehicle2)

        assert self.lane.get_no_vehicle_present() == 2, "Vehicle count should increase correctly."

    def test_queue_limit_enforcement(self):
        """Ensure vehicles are not added beyond queue limit."""
        for _ in range(5):
            self.lane.add_vehicle(MockVehicle(Dir.NORTH, Dir.EAST))

        assert self.lane.get_no_vehicle_present() == 5, "Lane should be at full capacity."

        # Try adding one more vehicle
        self.lane.add_vehicle(MockVehicle(Dir.NORTH, Dir.SOUTH))
        assert self.lane.get_no_vehicle_present() == 5, "Lane should not exceed its queue limit."

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
        self.lane.simulate_update([Dir.EAST, Dir.SOUTH], 10)
        assert self.lane.get_no_vehicle_present() == 0, "No vehicles should be processed if there were none."

    def test_simulate_update_clears_vehicles(self):
        """Ensure simulate_update removes vehicles as expected."""
        for _ in range(3):
            self.lane.add_vehicle(MockVehicle(Dir.NORTH, Dir.EAST))

        self.lane.simulate_update([Dir.EAST], 10)
        assert self.lane.get_no_vehicle_present() == 0, "All vehicles should be cleared by simulation."

    def test_simulate_update_partial_clearance(self):
        """Ensure simulate_update does not clear vehicles if time runs out."""
        for _ in range(3):
            self.lane.add_vehicle(MockVehicle(Dir.NORTH, Dir.EAST))

        self.lane.simulate_update([Dir.EAST], 2)  # Only enough time to process one or two vehicles
        assert self.lane.get_no_vehicle_present() > 0, "Some vehicles should remain if time runs out."

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
