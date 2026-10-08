"""Draw molecules and planned routes as images (RDKit + Pillow).

Usage (run in the terminal, from the project folder):
    python draw.py mol "CCO" --name ethanol     -> images/ethanol.png
    python draw.py targets                      -> images/targets.png (grid of all targets)
    python draw.py routes                       -> images/<target>_routeN.png (reaction schemes)
    python draw.py                              -> targets + routes (works with the Run button)
If you get "No module named PIL", run: pip install pillow
"""
import argparse
import re
from pathlib import Path

from PIL import Image, ImageDraw
from rdkit import Chem
from rdkit.Chem import Draw, rdChemReactions

OUT = Path("images")


def _mol(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")
    return mol


def save_molecule(smiles, path, size=(500, 400)):
    Draw.MolToImage(_mol(smiles), size=size).save(path)


def save_grid(smiles_list, legends, path, per_row=3, size=(320, 260)):
    mols = [_mol(s) for s in smiles_list]
    Draw.MolsToGridImage(mols, molsPerRow=per_row, subImgSize=size, legends=legends).save(path)


def _caption(text, width, height=36):
    img = Image.new("RGB", (width, height), "white")
    ImageDraw.Draw(img).text((10, 10), text, fill="black")
    return img


def _step_image(step, size=(260, 200)):
    # The planner works backward (target <- precursors); draw it forward.
    rxn = rdChemReactions.ReactionFromSmarts(
        f"{'.'.join(step.precursors)}>>{step.target}", useSmiles=True
    )
    return Draw.ReactionToImage(rxn, subImgSize=size)


def route_image(route, title):
    """Stack one captioned reaction picture per step, earliest reaction first."""
    parts = []
    ordered = list(reversed(route))  # leaves first, final reaction last
    for i, step in enumerate(ordered, 1):
        parts.append(_caption(f"Step {i}: {step.rule}   ({step.conditions})", 900))
        parts.append(_step_image(step))
    width = max(p.width for p in parts + [_caption(title, 900)])
    banner = _caption(title, width, 44)
    parts.insert(0, banner)
    height = sum(p.height for p in parts)
    canvas = Image.new("RGB", (width, height), "white")
    y = 0
    for p in parts:
        canvas.paste(p, (0, y))
        y += p.height
    return canvas


def _slug(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def draw_targets():
    from stock import TARGETS
    path = OUT / "targets.png"
    save_grid(list(TARGETS.values()), list(TARGETS.keys()), path)
    print("Saved", path)


def draw_routes(max_routes=2):
    from rules.planner import plan
    from stock import STOCK, TARGETS
    for name, smiles in TARGETS.items():
        routes = plan(smiles, STOCK)
        if not routes:
            print(f"{name}: no route, skipped")
            continue
        for i, route in enumerate(routes[:max_routes], 1):
            path = OUT / f"{_slug(name)}_route{i}.png"
            route_image(route, f"{name}: route {i} ({len(route)} step(s))").save(path)
            print("Saved", path)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")  # optional: no command draws everything
    m = sub.add_parser("mol")
    m.add_argument("smiles")
    m.add_argument("--name", default="molecule")
    sub.add_parser("targets")
    r = sub.add_parser("routes")
    r.add_argument("--max-routes", type=int, default=2)
    args = ap.parse_args()

    OUT.mkdir(exist_ok=True)
    if args.cmd == "mol":
        path = OUT / f"{_slug(args.name)}.png"
        save_molecule(args.smiles, path)
        print("Saved", path)
    elif args.cmd == "targets":
        draw_targets()
    elif args.cmd == "routes":
        draw_routes(args.max_routes)
    else:
        draw_targets()
        draw_routes()


if __name__ == "__main__":
    main()