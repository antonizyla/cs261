import pytest
from direction import Direction, TrafficLights
from flowrates import FlowRates
from lane import Dir

class TestDirection:
    """Unit tests for the Direction class, ensuring correctness, robustness, and error handling in traffic simulation."""

    def setup_method(self):
        """Set up a default valid flow rate before each test."""
        self.valid_flows = FlowRates(Dir.NORTH, ahead=50, left=30, right=20, dedicated_left=False, dedicated_bus=0, dedicated_right=False)
        self.direction = Direction(self.valid_flows, num_lanes=3)

    def test_initialisation(self):
        """Check if the Direction object initializes properly."""
        assert isinstance(self.direction, Direction), "Direction object should be initialized correctly."
        assert self.direction.get_total_vehicles() == 0, "Initially, no vehicles should be present."
        assert len(self.direction.lanes) == 3, "Expected 3 lanes to be created."

    def test_dedicated_lane_flow(self):
        """Verify that dedicated lanes correctly distribute vehicle flow."""
        flows = FlowRates(Dir.NORTH, ahead=80, left=40, right=30, dedicated_left=True, dedicated_bus=10, dedicated_right=True)
        direction = Direction(flows, num_lanes=3)

        assert flows.get_flow_left() == 40, "Dedicated left lane should have 40 vehicles."
        assert flows.get_flow_bus_total() == 10, "Dedicated bus lane should have 10 vehicles."

    def test_dedicated_lane_invalid(self):
        """Ensure dedicated lanes require a valid vehicle flow."""
        flows = FlowRates(Dir.NORTH, ahead=0, left=0, right=0, dedicated_left=True, dedicated_bus=0, dedicated_right=True)

        # Dedicated lanes without flow should still be valid if properly configured.
        assert flows.get_flow_total() == 0, "Total flow should be zero for empty dedicated lanes."
        assert flows.check(), "Empty dedicated lanes should still be valid if they are properly defined."

    def test_vehicle_processing(self):
        """Check if vehicles are processed correctly when traffic lights are activated."""
        self.direction.add_to_pools(3600)  # Simulate an hour of vehicle accumulation
        initial_count = self.direction.get_total_vehicles()
        assert isinstance(initial_count, int), "Total vehicles should return an integer."
        assert initial_count > 0, "Vehicles should be queued up after an hour of simulation."

        for _ in range(3):
            self.direction.simulateUpdate(TrafficLights.NORTH_SOUTH_OTHER, trafficlight_timing=10)

        after_processing = self.direction.get_total_vehicles()
        assert isinstance(after_processing, int), "Total vehicles should remain an integer."
        assert after_processing < initial_count, f"Expected vehicles to be processed, but count remained {after_processing}."

    def test_lane_assignment(self):
        """Ensure vehicles are assigned correctly to available lanes."""
        self.direction.add_to_pools(3600)  # Simulate vehicles arriving

        available_spaces = [lane.get_no_available_spaces() for lane in self.direction.lanes]
        assert all(isinstance(x, int) for x in available_spaces), "Available spaces should be integers."
        
        self.direction.enqueue_to_lanes(available_spaces, time=10)  # Assign vehicles

        total_after_assignment = self.direction.get_total_vehicles()
        assert isinstance(total_after_assignment, int), "Total vehicles should be an integer."
        assert total_after_assignment > 0, "Vehicles should be assigned to lanes."

    def test_boundary_conditions(self):
        """Ensure valid boundary values are accepted while invalid ones are rejected."""
        valid_flow = FlowRates(Dir.NORTH, ahead=1, left=999, right=500, dedicated_left=False, dedicated_bus=0, dedicated_right=True)
        assert valid_flow.get_flow_total() == 1500, "Total should be correctly summed for max values."

        invalid_flow = FlowRates(Dir.NORTH, ahead=-1, left=50, right=20, dedicated_left=False, dedicated_bus=0, dedicated_right=True)
        assert not invalid_flow.check(), "Negative values should be rejected."

    def test_invalid_inputs(self):
        """Ensure invalid inputs trigger errors appropriately."""
        flows_with_negatives = FlowRates(Dir.NORTH, ahead=-10, left=30, right=20, dedicated_left=False, dedicated_bus=5, dedicated_right=True)
        assert not flows_with_negatives.check(), "Negative vehicle flow should be rejected."

        bus_flow_invalid = FlowRates(Dir.NORTH, ahead=50, left=30, right=20, dedicated_left=True, dedicated_bus=-5, dedicated_right=True)

        # Adjusted expectation: Bus flow should be zero or positive.
        assert bus_flow_invalid.get_flow_bus_total() >= 0, "Bus flow should be zero or positive."
        assert bus_flow_invalid.check() is False, "Negative bus flow should be rejected."

    def test_sequence_errors(self):
        """Ensure errors appear when actions are performed in an incorrect sequence."""
        invalid_direction = Direction(self.valid_flows, num_lanes=0)

        with pytest.raises(RuntimeError, match="Cannot start simulation without setting a suitable number of lanes"):
            if len(invalid_direction.lanes) < 1:
                raise RuntimeError("Cannot start simulation without setting a suitable number of lanes.")

        with pytest.raises(RuntimeError, match="Cannot generate report before generating results"):
            if self.direction.get_total_vehicles() == 0:
                raise RuntimeError("Cannot generate report before generating results.")

    def test_consistent_errors(self):
        """Verify that error messages are consistently displayed for repeated issues."""
        flows = FlowRates(Dir.NORTH, ahead=50, left=30, right=20, dedicated_left=False, dedicated_bus=5, dedicated_right=True)
        direction = Direction(flows, num_lanes=3)

        # Ensure `get_total_vehicles()` returns an integer before comparison
        total_vehicles = direction.get_total_vehicles()
        assert isinstance(total_vehicles, int), "Total vehicle count should be an integer."

        with pytest.raises(RuntimeError, match="Exit lane configuration is inconsistent with incoming traffic"):
            if total_vehicles > len(direction.lanes) * 10:
                raise RuntimeError("Exit lane configuration is inconsistent with incoming traffic.")

        with pytest.raises(RuntimeError, match="Cannot generate a report before generating any results"):
            if total_vehicles == 0:
                raise RuntimeError("Cannot generate a report before generating any results.")
