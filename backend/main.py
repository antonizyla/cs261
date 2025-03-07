from flowrates import FlowRates
from lane import Lane, Dir
from params import Parameters
from junction import Junction

# run a basic test configuration
j_params = Parameters([5,5,5,5])
northerly_flow = FlowRates(Dir.NORTH, 50, 50, 50, False, 30, False)
easterly_flow = FlowRates(Dir.EAST, 50, 50, 50, False, 30, False)
southerly_flow = FlowRates(Dir.SOUTH, 50, 50, 50, False, 30, False)
westerly_flow = FlowRates(Dir.WEST, 50, 50, 50, False, 30, False)

print([j_params.check(), [northerly_flow.check(), easterly_flow.check(), southerly_flow.check(), westerly_flow.check()]])

J = Junction(j_params, [northerly_flow, easterly_flow, southerly_flow, westerly_flow])

print(J.run_simulation())

