from backend.flowrates import FlowRates
from backend.junction import Junction


def front_backend_join(junc_params, flowrates: list[FlowRates]):
    j = Junction(junc_params, flowrates)
    j.run_simulation()
    results = []
    for d in [j.northerly_lanes, j.easterly_lanes, j.southerly_lanes, j.westerly_lanes]:
        results.append([d.get_avg_wait, d.get_max_length, d.get_max_wait])
    return results
