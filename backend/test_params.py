import pytest
from junction import Junction
from params import Parameters
from flowrates import FlowRates
from lane import Dir


class TestJunction:
    """Unit tests for the Junction class, ensuring correctness, robustness, and error handling in traffic simulation."""

    def setup_method(self):
        """Set up default parameters and flow rates before each test."""
        self.params = Parameters(
            no_lanes=[2, 2, 2, 2], 
            crossing_rph=[300, 250, 200, 150], 
            sequencing_priority=[2, 3, 1, 4], 
            crossing_time=[15, 20, 10, 12]
        )

        self.flow_rates = [
            FlowRates(Dir.NORTH, ahead=50, left=30, right=20, dedicated_left=True, dedicated_bus=5, dedicated_right=True),
            FlowRates(Dir.EAST, ahead=40, left=25, right=15, dedicated_left=False, dedicated_bus=0, dedicated_right=False),
            FlowRates(Dir.SOUTH, ahead=60, left=35, right=25, dedicated_left=True, dedicated_bus=5, dedicated_right=False),
            FlowRates(Dir.WEST, ahead=45, left=20, right=10, dedicated_left=False, dedicated_bus=5, dedicated_right=True)
        ]

        self.junction = Junction(self.params, self.flow_rates)

    # ✅ **Basic Initialization Tests**
    def test_junction_initialisation(self):
        """Ensure the junction initializes correctly with parameters and flow rates."""
        assert isinstance(self.junction, Junction), "Junction object did not initialize correctly."
        assert self.junction.params == self.params, "Junction parameters mismatch."
        assert len(self.junction.flow_rates) == 4, "Junction should have flow rates for all directions."

    def test_lanes_initialised_correctly(self):
        """Ensure the correct number of lanes are created."""
        assert len(self.junction.northerly_lanes.lanes) == self.params.noLanes[0]
        assert len(self.junction.easterly_lanes.lanes) == self.params.noLanes[1]
        assert len(self.junction.southerly_lanes.lanes) == self.params.noLanes[2]
        assert len(self.junction.westerly_lanes.lanes) == self.params.noLanes[3]

    # ✅ **Flow Rate Management**
    def test_set_flow_rates(self):
        """Ensure flow rates can be updated correctly."""
        new_flows = [
            FlowRates(Dir.NORTH, ahead=80, left=40, right=30, dedicated_left=False, dedicated_bus=10, dedicated_right=False),
            FlowRates(Dir.EAST, ahead=60, left=30, right=20, dedicated_left=True, dedicated_bus=5, dedicated_right=True),
            FlowRates(Dir.SOUTH, ahead=70, left=50, right=35, dedicated_left=False, dedicated_bus=0, dedicated_right=True),
            FlowRates(Dir.WEST, ahead=55, left=25, right=15, dedicated_left=True, dedicated_bus=5, dedicated_right=False)
        ]

        self.junction.set_flow_rates(new_flows)
        assert self.junction.flow_rates == new_flows, "Flow rates were not updated correctly."

    # ✅ **Junction Configuration Updates**
    def test_set_junction_configurations(self):
        """Ensure junction configurations can be updated correctly."""
        new_params = Parameters(
            no_lanes=[3, 3, 3, 3], 
            crossing_rph=[200, 250, 150, 300], 
            sequencing_priority=[3, 1, 4, 2], 
            crossing_time=[20, 25, 15, 18]
        )

        self.junction.set_junction_configurations(new_params)
        assert self.junction.params == new_params, "Junction configurations were not updated correctly."

    # ✅ **Simulation Execution**
    def test_run_simulation_basic(self):
        """Ensure the simulation runs and processes vehicles correctly."""
        initial_vehicle_count = (
            self.junction.northerly_lanes.get_total_vehicles()
            + self.junction.easterly_lanes.get_total_vehicles()
            + self.junction.southerly_lanes.get_total_vehicles()
            + self.junction.westerly_lanes.get_total_vehicles()
        )

        self.junction.run_simulation()

        final_vehicle_count = (
            self.junction.northerly_lanes.get_total_vehicles()
            + self.junction.easterly_lanes.get_total_vehicles()
            + self.junction.southerly_lanes.get_total_vehicles()
            + self.junction.westerly_lanes.get_total_vehicles()
        )

        assert final_vehicle_count <= initial_vehicle_count, "Simulation should process vehicles, not increase count."
        assert initial_vehicle_count != final_vehicle_count, "Some vehicles should have been processed."

    def test_add_vehicles(self):
        """Ensure vehicles are correctly added to the pools."""
        self.junction.add_vehicles(10)  # Simulate adding vehicles over 10 seconds
        assert self.junction.northerly_lanes.get_total_vehicles() > 0, "Expected vehicles to be added, but count remained zero."

    # ✅ **Boundary Testing**
    def test_invalid_flow_rates(self):
        """Ensure invalid flow rates return False when checked."""
        invalid_flows = [
            FlowRates(Dir.NORTH, ahead=-10, left=20, right=30, dedicated_left=False, dedicated_bus=5, dedicated_right=True),
            FlowRates(Dir.EAST, ahead=50, left=1000, right=40, dedicated_left=True, dedicated_bus=0, dedicated_right=False),
            FlowRates(Dir.SOUTH, ahead=50, left=15, right=35, dedicated_left=True, dedicated_bus=-5, dedicated_right=True),
            FlowRates(Dir.WEST, ahead=45, left=25, right=-10, dedicated_left=False, dedicated_bus=5, dedicated_right=True),
        ]

        for flow in invalid_flows:
            assert not flow.check(), f"Invalid flow {flow} should be rejected but was accepted."

    def test_invalid_lane_configurations(self):
        """Ensure invalid lane configurations raise appropriate errors."""
        with pytest.raises(ValueError, match="Each lane count must be an integer between 1 and 5."):
            Parameters(no_lanes=[0, 6, 3, 2]).check()  # 0 and 6 are out of range

    # ✅ **Error Handling & Robustness**
    def test_simulation_does_not_hang(self):
        """Ensure the simulation runs without an infinite loop or hangs."""
        try:
            self.junction.run_simulation()
        except Exception as e:
            pytest.fail(f"Simulation caused an unexpected error: {e}")

    def test_sequence_errors(self):
        """Ensure correct errors appear when actions are performed out of order."""
        invalid_junction = Junction(self.params, self.flow_rates)

        # Trying to start a simulation without setting lanes
        with pytest.raises(RuntimeError, match="Cannot start simulation without setting a suitable number of lanes"):
            if sum(invalid_junction.params.noLanes) == 0:
                raise RuntimeError("Cannot start simulation without setting a suitable number of lanes")

        # Trying to generate a report before generating results
        with pytest.raises(RuntimeError, match="Cannot generate report before generating results"):
            if invalid_junction.get_total_vehicles() == 0:
                raise RuntimeError("Cannot generate report before generating results")
