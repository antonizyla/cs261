from flow_rates import flow_rates

class TestFlowRates:
    def test_flow_rates_summation(self):
        flows = flow_rates(50, 50, 50, 50, False)
        assert flows.check() == False
    def test_flow_rates_negative(self):
        flows = flow_rates(-10, 0, 50, 40, False)
        assert flows.check() == False
    def test_flow_rates_normal(self):
        flows = flow_rates(40, 40, 30, 0, True)
        assert flows.check() == True