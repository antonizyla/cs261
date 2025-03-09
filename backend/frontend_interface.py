from flowrates import FlowRates
from junction import Junction


def front_backend_join(junc_params, flowrates: list[FlowRates]):
    j = Junction(junc_params, flowrates)
    j.run_simulation()
    results = []
    k_wait = 1
    k_len = 1
    k_pedestrian = 10
    overall_score = 0
    i = 0
    for d in [j.northerly_lanes, j.easterly_lanes, j.southerly_lanes, j.westerly_lanes]:
        results.append([d.get_avg_wait(), d.get_max_length(), d.get_max_wait()])
        overall_score += ((flowrates[i].get_flow_total() + k_pedestrian *  (1 if junc_params.has_pedestrian_crossing()[i] else 0) * junc_params.get_crossing_time()[i] * junc_params.get_crossing_rph()[i]) / (k_wait * ((results[i][0] if results[i][0] != 0 else 0.01) + ((results[i][2] if results[i][2] != 0 else 0.01)**2 /( results[i][0] if results[i][0] != 0 else 0.01))) + (results[i][1] if results[i][1] != 0 else 0) * k_len))
        i += 1
    results.append(overall_score)
    return results
