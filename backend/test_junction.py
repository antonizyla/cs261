import pytest
from junction import Junction
from params import Parameters
from flowrates import FlowRates
from lane import Dir  # Import only what's needed

class TestJunction:
    def setup_method(self):
        """Initialise parameters and flow rates before each test."""
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

    def test_junction_initialisation(self):
        """Ensure the junction initialises correctly with parameters and flow rates."""
        assert isinstance(self.junction, Junction)
        assert self.junction.params == self.params
        assert len(self.junction.flow_rates) == 4

    def test_set_flow_rates(self):
        """Ensure flow rates can be updated correctly."""
        new_flows = [
            FlowRates(Dir.NORTH, ahead=80, left=40, right=30, dedicated_left=False, dedicated_bus=10, dedicated_right=False),
            FlowRates(Dir.EAST, ahead=60, left=30, right=20, dedicated_left=True, dedicated_bus=5, dedicated_right=True),
            FlowRates(Dir.SOUTH, ahead=70, left=50, right=35, dedicated_left=False, dedicated_bus=0, dedicated_right=True),
            FlowRates(Dir.WEST, ahead=55, left=25, right=15, dedicated_left=True, dedicated_bus=5, dedicated_right=False)
        ]

        self.junction.set_flow_rates(new_flows)
        assert self.junction.flow_rates == new_flows

    def test_set_junction_configurations(self):
        """Ensure junction configurations can be updated correctly."""
        new_params = Parameters(
            no_lanes=[3, 3, 3, 3], 
            crossing_rph=[200, 250, 150, 300], 
            sequencing_priority=[3, 1, 4, 2], 
            crossing_time=[20, 25, 15, 18]
        )

        self.junction.set_junction_configurations(new_params)
        assert self.junction.params == new_params

    def test_run_simulation_basic(self):
        """Ensure the simulation processes vehicles correctly."""
        initial_vehicle_count = (
            self.junction.northerly_lanes.get_total_vehicles() +
            self.junction.easterly_lanes.get_total_vehicles() +
            self.junction.southerly_lanes.get_total_vehicles() +
            self.junction.westerly_lanes.get_total_vehicles()
        )

        self.junction.run_simulation()

        final_vehicle_count = (
            self.junction.northerly_lanes.get_total_vehicles() +
            self.junction.easterly_lanes.get_total_vehicles() +
            self.junction.southerly_lanes.get_total_vehicles() +
            self.junction.westerly_lanes.get_total_vehicles()
        )

        assert final_vehicle_count <= initial_vehicle_count, "Simulation should process vehicles, not increase count."

    def test_add_vehicles(self):
        """Ensure vehicles are correctly added to the pools."""
        self.junction.add_vehicles(10)  # Simulate adding vehicles over 10 seconds
        assert self.junction.northerly_lanes.get_total_vehicles() > 0

    def test_invalid_flow_rates(self):
        """Ensure invalid flow rates return False when checked."""
        invalid_flows = [
            FlowRates(Dir.NORTH, ahead=-10, left=20, right=30, dedicated_left=False, dedicated_bus=5, dedicated_right=True),  # Negative flow
            FlowRates(Dir.EAST, ahead=50, left=1000, right=40, dedicated_left=True, dedicated_bus=0, dedicated_right=False),  # Exceeding range
            FlowRates(Dir.SOUTH, ahead=50, left=15, right=35, dedicated_left=True, dedicated_bus=-5, dedicated_right=True),  # Negative bus lane
            FlowRates(Dir.WEST, ahead=45, left=25, right=-10, dedicated_left=False, dedicated_bus=5, dedicated_right=True),  # Negative right turn
        ]

        for flow in invalid_flows:
            assert not flow.check(), f"Flow {flow} should be invalid but was accepted."

    def test_invalid_lane_configurations(self):
        """Ensure invalid lane configurations raise appropriate errors."""
        with pytest.raises(ValueError, match="Each lane count must be an integer between 1 and 5."):
            Parameters(no_lanes=[0, 6, 3, 2]).check()  # 0 and 6 are out of range

    def test_simulation_does_not_hang(self):
        """Ensure the simulation runs without an infinite loop or hangs."""
        try:
            self.junction.run_simulation()
        except Exception as e:
            pytest.fail(f"Simulation caused an unexpected error: {e}")
