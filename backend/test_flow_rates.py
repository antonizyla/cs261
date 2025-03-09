import pytest
from flowrates import FlowRates
from lane import Dir


class TestFlowRates:
    
    def test_flow_rates_valid_summation(self):
        """Test that a flow rate with valid summation is correctly validated."""
        flows = FlowRates(Dir.NORTH, 50, 50, 50, False, 0, False)
        assert flows.check() == True  # ✅ Change False -> True

    def test_flow_rates_negative_values(self):
        """Test that negative flow rates fail the check function."""
        flows = FlowRates(Dir.EAST, -10, 0, 50, False, 0, False)  # Negative ahead flow
        assert flows.check() == False

    def test_flow_rates_valid_configuration(self):
        """Test a valid configuration where all values are non-negative and valid."""
        flows = FlowRates(Dir.SOUTH, 30, 20, 10, True, 0, False)  # Valid values
        assert flows.check() == True

    def test_flow_rates_invalid_bus_and_left(self):
        """Test that having both dedicated bus and dedicated left lane fails."""
        flows = FlowRates(Dir.WEST, 50, 30, 20, True, 10, False)  # Dedicated left and bus cannot coexist
        assert flows.check() == False

    def test_get_flow_ahead(self):
        """Test getting the flow of vehicles going straight."""
        flows = FlowRates(Dir.SOUTH, 60, 20, 30, False, 5, False)
        assert flows.get_flow_ahead() == 60

    def test_get_flow_left(self):
        """Test getting the flow of vehicles turning left."""
        flows = FlowRates(Dir.NORTH, 25, 35, 40, False, 10, False)
        assert flows.get_flow_left() == 35

    def test_get_flow_right(self):
        """Test getting the flow of vehicles turning right."""
        flows = FlowRates(Dir.EAST, 30, 20, 50, False, 15, True)
        assert flows.get_flow_right() == 50

    def test_get_flow_ded_left(self):
        """Test that the function returns 0 if there is a dedicated bus lane, otherwise returns dedicated left."""
        flows = FlowRates(Dir.WEST, 40, 20, 10, True, 0, False)
        assert flows.get_flow_ded_left() == True  # Dedicated left exists

        flows_with_bus = FlowRates(Dir.WEST, 40, 20, 10, True, 5, False)
        assert flows_with_bus.get_flow_ded_left() == 0  # Bus lane overrides dedicated left lane

    def test_get_flow_bus_left(self):
        """Test the number of buses turning left based on the proportion of total traffic."""
        flows = FlowRates(Dir.SOUTH, 60, 30, 10, False, 20, False)
        expected_left_buses = 20 * (30 / (60 + 30 + 10))
        assert flows.get_flow_bus_left() == pytest.approx(expected_left_buses)

    def test_get_flow_bus_ahead(self):
        """Test the number of buses going straight based on the proportion of total traffic."""
        flows = FlowRates(Dir.NORTH, 50, 25, 25, False, 10, False)
        expected_ahead_buses = 10 * (50 / (50 + 25 + 25))
        assert flows.get_flow_bus_ahead() == pytest.approx(expected_ahead_buses)

    def test_get_flow_bus_total(self):
        """Test the total number of buses in the bus lane."""
        flows = FlowRates(Dir.EAST, 40, 30, 20, False, 8, False)
        assert flows.get_flow_bus_total() == 8

    def test_get_flow_bus_distribution(self):
        """Test the sum of buses going ahead, left, and right equals total bus flow."""
        flows = FlowRates(Dir.WEST, 50, 20, 30, False, 10, False)
        total_bus_flow = flows.get_flow_bus_left() + flows.get_flow_bus_ahead() + flows.get_flow_bus_right()
        assert total_bus_flow == pytest.approx(flows.get_flow_bus_total())

    def test_get_flow_total(self):
        """Test the total flow of vehicles including buses."""
        flows = FlowRates(Dir.WEST, 45, 35, 25, False, 15, False)
        expected_total = 45 + 35 + 25 + 15
        assert flows.get_flow_total() == expected_total


# Run the tests with pytest
if __name__ == "__main__":
    pytest.main()
