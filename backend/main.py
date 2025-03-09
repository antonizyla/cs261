from backend.flowrates import FlowRates
from backend.lane import Lane, Dir
from backend.params import Parameters
from backend.junction import Junction

# run a basic test configuration
j_params = Parameters([2, 2, 2, 2])
northerly_flow = FlowRates(Dir.NORTH, 5, 5, 5, False, 0, False)
easterly_flow = FlowRates(Dir.EAST, 5, 5, 5, False, 0, False)
southerly_flow = FlowRates(Dir.SOUTH, 5, 5, 5, False, 0, False)
westerly_flow = FlowRates(Dir.WEST, 5, 5, 5, False, 0, False)

print(
    [j_params.check(), [northerly_flow.check(), easterly_flow.check(), southerly_flow.check(), westerly_flow.check()]])

J = Junction(j_params, [northerly_flow, easterly_flow, southerly_flow, westerly_flow])
