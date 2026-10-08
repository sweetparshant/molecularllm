"""Goal-directed backward search: from a target molecule to purchasable stock."""
from dataclasses import dataclass
from itertools import product

from rdkit import Chem

from .retro_rules import RULES, get_reaction


@dataclass
class Step:
    rule: str
    conditions: str
    target: str
    precursors: tuple
    explanation: str


def canon(smiles: str) -> str:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")
    return Chem.MolToSmiles(mol)


def apply_rule(rule, smiles: str):
    """Return the distinct precursor sets this rule proposes for a molecule."""
    mol = Chem.MolFromSmiles(smiles)
    outcomes = set()
    for products in get_reaction(rule).RunReactants((mol,)):
        try:
            for p in products:
                Chem.SanitizeMol(p)
            outcomes.add(tuple(sorted(Chem.MolToSmiles(p) for p in products)))
        except Exception:
            continue  # chemically invalid result, discard
    return outcomes


def _routes(smiles, stock, depth, path, cap):
    if smiles in stock:
        return [[]]  # purchasable: no steps needed
    if depth == 0 or smiles in path:
        return []
    found = []
    for rule in RULES:
        for precursors in sorted(apply_rule(rule, smiles)):
            sub_options = [
                _routes(p, stock, depth - 1, path | {smiles}, cap) for p in precursors
            ]
            if any(not s for s in sub_options):
                continue  # at least one precursor cannot be sourced
            for combo in product(*sub_options):
                step = Step(rule.name, rule.conditions, smiles, precursors, rule.explanation)
                found.append([step] + [s for sub in combo for s in sub])
                if len(found) >= cap:
                    return found
    return found


def _signature(route):
    return tuple(sorted((s.rule, s.target, s.precursors) for s in route))


def plan(target_smiles, stock, max_depth=3, cap=50):
    stock = {canon(s) for s in stock}
    routes = _routes(canon(target_smiles), stock, max_depth, frozenset(), cap)
    unique = {_signature(r): r for r in routes}
    return sorted(unique.values(), key=len)  # fewer steps first (model scoring comes next)


def propose(smiles: str):
    """All single-step proposals for a molecule: {precursor_tuple: [rule names]}.

    Used by the benchmark: stock is ignored, so we measure only whether the
    rules can reproduce the documented disconnection.
    """
    proposals = {}
    for rule in RULES:
        for precursors in apply_rule(rule, canon(smiles)):
            proposals.setdefault(precursors, []).append(rule.name)
    return proposals