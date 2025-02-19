from flowrates import FlowRates

class TestFlowRates:
    def test_flow_rates_summation(self):
        flows = FlowRates(50, 50, 50, 50, False)
        assert flows.check() == False
    def test_flow_rates_negative(self):
        flows = FlowRates(-10, 0, 50, 40, False)
        assert flows.check() == False
    def test_flow_rates_normal(self):
        flows = FlowRates(40, 40, 30, 0, True)
        assert flows.check() == True