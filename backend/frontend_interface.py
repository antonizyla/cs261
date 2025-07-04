from backend.flowrates import FlowRates
from backend.junction import Junction


def front_backend_join(junc_params, flowrates: list[FlowRates]):
    j = Junction(junc_params, flowrates)

    if not junc_params.check():
        SystemError("Parameters Not Correct format")
    for flow in flowrates:
        if not flow.check():
            SystemError("Flow rate not correct format")

    j.run_simulation()
    results = []
    k_wait = 1
    k_len = 1
    k_pedestrian = 10
    overall_score = 0
    i = 0
    for d in [j.northerly_lanes, j.easterly_lanes, j.southerly_lanes, j.westerly_lanes]:
        results.append([d.get_avg_wait()/60, d.get_max_wait()/60, d.get_max_length()])
        overall_score += ((flowrates[i].get_flow_total() +
                           k_pedestrian *  (1 if junc_params.has_pedestrian_crossing() else 0) * junc_params.get_crossing_time() * junc_params.get_crossing_rph())
                          / (k_wait * ((results[i][0] if results[i][0] != 0 else 1) + ((results[i][1] if results[i][1] != 0 else 1)**2 /( results[i][0] if results[i][0] != 0 else 1))) + (results[i][2] if results[i][2] != 0 else 0) * k_len))
        print(overall_score)
        i += 1
    results.append(overall_score)
    return results
