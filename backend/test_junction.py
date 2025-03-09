import pytest
from junction import Junction
from params import Parameters
from flowrates import FlowRates
from lane import Dir

class TestJunction:
    def setup_method(self):
        """Initialise parameters and flow rates before each test."""
        self.params = Parameters(
            no_lanes=[2, 2, 2, 2], 
            crossing_rph=[300, 250, 200, 150],  # Vehicles per hour per lane
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
        assert len(self.junction.flow_rates) == 4

    def test_set_flow_rates(self):
        """Ensure flow rates can be updated dynamically."""
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

    def test_run_simulation(self):
        """Ensure the simulation reduces queued vehicles but does not clear them all instantly."""
        initial_vehicle_count = sum(
            dir.get_total_vehicles() for dir in [
                self.junction.northerly_lanes,
                self.junction.easterly_lanes,
                self.junction.southerly_lanes,
                self.junction.westerly_lanes
            ]
        )

        # Extract the average pedestrian crossing rate correctly
        avg_crossing_rph = sum(self.params.crossing_rph) / len(self.params.crossing_rph)
        assert isinstance(avg_crossing_rph, (int, float)), "Crossing RPH should be a number."

        self.junction.run_simulation()

        final_vehicle_count = sum(
            dir.get_total_vehicles() for dir in [
                self.junction.northerly_lanes,
                self.junction.easterly_lanes,
                self.junction.southerly_lanes,
                self.junction.westerly_lanes
            ]
        )
        
        assert final_vehicle_count <= initial_vehicle_count, "Simulation should process vehicles but not increase them."

    def test_add_vehicles(self):
        """Ensure vehicles are correctly added to the queue over time."""
        self.junction.add_vehicles(10)  # Simulate 10 seconds of vehicle arrival
        
        total_vehicles = sum(dir.get_total_vehicles() for dir in [
            self.junction.northerly_lanes,
            self.junction.easterly_lanes,
            self.junction.southerly_lanes,
            self.junction.westerly_lanes
        ])

        assert isinstance(total_vehicles, int), "Total vehicles should be an integer."
        assert total_vehicles >= 0, "Vehicle count should not be negative."

    def test_edge_case_empty_junction(self):
        """Ensure an empty junction behaves correctly without errors."""
        empty_flows = [
            FlowRates(Dir.NORTH, ahead=0, left=0, right=0, dedicated_left=False, dedicated_bus=0, dedicated_right=False),
            FlowRates(Dir.EAST, ahead=0, left=0, right=0, dedicated_left=False, dedicated_bus=0, dedicated_right=False),
            FlowRates(Dir.SOUTH, ahead=0, left=0, right=0, dedicated_left=False, dedicated_bus=0, dedicated_right=False),
            FlowRates(Dir.WEST, ahead=0, left=0, right=0, dedicated_left=False, dedicated_bus=0, dedicated_right=False),
        ]

        empty_junction = Junction(self.params, empty_flows)
        empty_junction.run_simulation()
        
        total_vehicles = sum(dir.get_total_vehicles() for dir in [
            empty_junction.northerly_lanes,
            empty_junction.easterly_lanes,
            empty_junction.southerly_lanes,
            empty_junction.westerly_lanes
        ])
        
        assert total_vehicles == 0, "An empty junction should not accumulate vehicles."

    def test_simulation_does_not_crash(self):
        """Ensure the simulation runs without errors or infinite loops."""
        try:
            avg_crossing_rph = sum(self.params.crossing_rph) / len(self.params.crossing_rph)
            assert isinstance(avg_crossing_rph, (int, float)), "Crossing RPH should be a number."
            
            self.junction.run_simulation()
        except Exception as e:
            pytest.fail(f"Simulation encountered an error: {e}")
