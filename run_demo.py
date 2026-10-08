"""Run the logic-based planner on the multi-step test targets."""
from rules.planner import plan
from stock import STOCK, TARGETS

for name, smiles in TARGETS.items():
    print(f"\n=== {name} ({smiles}) ===")
    routes = plan(smiles, STOCK)
    if not routes:
        print("No route found within the depth limit.")
    for i, route in enumerate(routes[:4], 1):
        print(f"Route {i}: {len(route)} step(s)")
        for s in route:
            print(f"  [{s.rule}] {s.target} <- {' + '.join(s.precursors)}")
            print(f"      why: {s.explanation}  conditions: {s.conditions}")
    if len(routes) > 4:
        print(f"... and {len(routes) - 4} more route(s)")
