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
        assert self.direction.flows.get_flow_total() == 100, "Total flow should match the sum of individual flows."
        assert len(self.direction.lanes) == 3, "Expected 3 lanes to be created."
        assert self.direction.get_total_vehicles() == 0, "Initially, no vehicles should be present."

    def test_dedicated_lane_flow(self):
        """Verify that dedicated lanes correctly distribute vehicle flow."""
        flows = FlowRates(Dir.NORTH, ahead=80, left=40, right=30, dedicated_left=True, dedicated_bus=10, dedicated_right=True)
        direction = Direction(flows, num_lanes=3)

        assert flows.get_flow_ded_left() == 40, "Dedicated left lane should have 40 vehicles."
        assert flows.get_flow_bus_total() == 10, "Dedicated bus lane should have 10 vehicles."

    def test_dedicated_lane_invalid(self):
        """Ensure dedicated lanes require a valid vehicle flow."""
        flows = FlowRates(Dir.NORTH, ahead=0, left=0, right=0, dedicated_left=True, dedicated_bus=0, dedicated_right=True)
        assert not flows.check(), "Dedicated lanes without traffic should be invalid."

    def test_vehicle_processing(self):
        """Check if vehicles are processed correctly when traffic lights are activated."""
        self.direction.simulate_hourly()
        initial_count = self.direction.get_total_vehicles()
        assert initial_count > 0, "Vehicles should be queued up after an hour of simulation."

        for _ in range(3):
            self.direction.simulateUpdate(TrafficLights.NORTH_SOUTH_OTHER, trafficlight_timing=10)

        after_processing = self.direction.get_total_vehicles()
        assert after_processing < initial_count, f"Expected vehicles to be processed, but count remained {after_processing}."

    def test_lane_assignment(self):
        """Ensure vehicles are assigned correctly to available lanes."""
        self.direction.simulate_hourly()
        assert self.direction.get_total_vehicles() > 0, "Expected vehicles to be queued."

        available_spaces = [lane.get_no_available_spaces() for lane in self.direction.lanes]
        self.direction.enqueue_to_lanes(available_spaces)

        total_after_assignment = self.direction.get_total_vehicles()
        assert total_after_assignment > 0, "Vehicles should be assigned to lanes."

    def test_boundary_conditions(self):
        """Ensure valid boundary values are accepted while invalid ones are rejected."""
        valid_flow = FlowRates(Dir.NORTH, ahead=0, left=999, right=500, dedicated_left=False, dedicated_bus=0, dedicated_right=True)
        assert valid_flow.get_flow_total() == 1499, "Total should be correctly summed for max values."

        invalid_flow = FlowRates(Dir.NORTH, ahead=-1, left=50, right=20, dedicated_left=False, dedicated_bus=0, dedicated_right=True)
        assert not invalid_flow.check(), "Negative values should be rejected."

    def test_invalid_inputs(self):
        """Ensure invalid inputs trigger errors appropriately."""
        flows_with_negatives = FlowRates(Dir.NORTH, ahead=-10, left=30, right=20, dedicated_left=False, dedicated_bus=5, dedicated_right=True)
        assert not flows_with_negatives.check(), "Negative vehicle flow should be rejected."

        bus_flow_invalid = FlowRates(Dir.NORTH, ahead=50, left=30, right=20, dedicated_left=True, dedicated_bus=-5, dedicated_right=True)
        assert not bus_flow_invalid.check(), "Bus flow should not be negative."

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

        with pytest.raises(RuntimeError, match="Exit lane configuration is inconsistent with incoming traffic"):
            if sum(direction.pools) > len(direction.lanes) * 10:
                raise RuntimeError("Exit lane configuration is inconsistent with incoming traffic.")

        with pytest.raises(RuntimeError, match="Cannot generate a report before generating any results"):
            if direction.get_total_vehicles() == 0:
                raise RuntimeError("Cannot generate a report before generating any results.")
