from backend.flowrates import FlowRates
from backend.junction import Junction


def front_backend_join(junc_params, flowrates: list[FlowRates]):
    j = Junction(junc_params, flowrates)
    j.run_simulation()
    results = []
    overall_score = 0
    i = 0
    for d in [j.northerly_lanes, j.easterly_lanes, j.southerly_lanes, j.westerly_lanes]:
        results.append([d.get_avg_wait(), d.get_max_length(), d.get_max_wait()])
        overall_score += (flowrates[i].get_flow_total() / (k_wait * (results[i][0] + (results[i][2]**2 / results[i][0])) + results[i][1] * k_len)) 
        i += 1
    #Calculate Overall Score
    return results
