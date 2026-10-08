"""Benchmark the rule-based planner on a reaction dataset (single-step).

Usage:
    python benchmark.py data/sample_reactions.csv
    python benchmark.py path/to/raw_test.csv --limit 5000

The file needs one column holding reaction SMILES as 'reactants>reagents>product'
or 'reactants>>product' (atom maps are stripped). Pass --col if your header differs.
For each product we ask: do the rules propose the documented reactant set?
"""
import argparse
from collections import Counter

import pandas as pd
from rdkit import Chem

from rules.planner import propose


def clean(smiles: str) -> str:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(smiles)
    for atom in mol.GetAtoms():
        atom.SetAtomMapNum(0)
    return Chem.MolToSmiles(mol)


def parse(rxn: str):
    parts = rxn.strip().split(">")
    reactants = tuple(sorted(clean(s) for s in parts[0].split(".")))
    product = clean(parts[-1])
    return reactants, product


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--col", default="reactants>reagents>production")
    ap.add_argument("--limit", type=int, default=5000)
    ap.add_argument("--out", default="benchmark_results.csv")
    args = ap.parse_args()

    df = pd.read_csv(args.path)
    if args.col not in df.columns:
        raise SystemExit(f"Column '{args.col}' not found. Columns: {list(df.columns)}. Use --col.")
    df = df.head(args.limit)

    rows, hits_by_rule, bad = [], Counter(), 0
    for rxn in df[args.col]:
        try:
            reactants, product = parse(rxn)
            proposals = propose(product)
        except Exception:
            bad += 1
            continue
        correct = reactants in proposals
        rule_hits = proposals.get(reactants, [])
        for r in rule_hits:
            hits_by_rule[r] += 1
        rows.append({"product": product, "truth": ".".join(reactants),
                     "n_proposals": len(proposals), "covered": bool(proposals),
                     "correct": correct, "rules": ";".join(rule_hits)})

    res = pd.DataFrame(rows)
    n, covered, correct = len(res), int(res["covered"].sum()), int(res["correct"].sum())
    print(f"Reactions evaluated : {n}  (skipped unparsable: {bad})")
    print(f"Coverage (any rule fires)        : {covered}/{n} = {100 * covered / max(n, 1):.1f}%")
    print(f"Exact match, all reactions       : {correct}/{n} = {100 * correct / max(n, 1):.1f}%")
    print(f"Exact match, covered reactions   : {correct}/{max(covered, 1)} = {100 * correct / max(covered, 1):.1f}%")
    if covered:
        print(f"Avg proposals per covered product: {res.loc[res.covered, 'n_proposals'].mean():.2f}")
    print("Correct matches by rule:", dict(hits_by_rule) or "none")
    res.to_csv(args.out, index=False)
    print(f"Per-reaction results saved to {args.out}")


if __name__ == "__main__":
    main()