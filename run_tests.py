"""Expectation checks for the planner. Run: python run_tests.py"""
from rules.planner import plan
from stock import STOCK, TARGETS

# name -> (shortest route length or None for 'no route', rule sets that must each appear in some route)
CASES = {
    "N-benzylbenzamide": (1, [{"amide_coupling"}]),
    "4-methylbiphenyl": (1, [{"suzuki_coupling"}]),
    "N-ethylbenzylamine": (1, [{"reductive_amination"},
                               {"reductive_amination", "alcohol_oxidation_aldehyde"}]),
    "2-phenylpropan-2-ol": (2, [{"grignard_addition", "alcohol_oxidation_ketone"}]),
    "N-benzyl tosylamide": (1, [{"sulfonamide_formation"}]),
    "N-ethyl-4-phenylbenzamide": (2, [{"amide_coupling", "suzuki_coupling"}]),
    "caffeine (expect no route)": (None, []),
}

passed = 0
for name, (shortest, rule_sets) in CASES.items():
    routes = plan(TARGETS[name], STOCK)
    used = [{s.rule for s in r} for r in routes]
    if shortest is None:
        ok = not routes
    else:
        ok = bool(routes) and len(routes[0]) == shortest and all(
            any(need <= u for u in used) for need in rule_sets
        )
    passed += ok
    best = len(routes[0]) if routes else "none"
    print(f"{'PASS' if ok else 'FAIL'}  {name}  (routes: {len(routes)}, shortest: {best})")

print(f"\n{passed}/{len(CASES)} passed")
