"""Retrosynthetic rules: each rule maps a product pattern to its precursors.

Templates are RDKit reaction SMARTS written backward (product >> precursors).
Every rule carries a plain-language explanation and typical conditions, which
is what makes the planner's output explainable. Forming bonds are restricted
to non-ring bonds (-!@) so a disconnection always splits the molecule cleanly.
Bond orders that change are written explicitly (- or =) on purpose.
"""
from dataclasses import dataclass

from rdkit.Chem import AllChem


@dataclass(frozen=True)
class RetroRule:
    name: str
    smarts: str
    explanation: str
    conditions: str


RULES = [
    RetroRule(
        "amide_coupling",
        "[#6:4][CX3:1](=[O:2])-!@[NX3;H1,H2:3]>>[#6:4][C:1](=[O:2])[OH].[N:3]",
        "An amide bond forms between a carboxylic acid and an amine.",
        "coupling reagent (e.g. EDC or HATU), base",
    ),
    RetroRule(
        "esterification",
        "[#6:4][CX3:1](=[O:2])-!@[OX2:3][CX4:5]>>[#6:4][C:1](=[O:2])[OH].[O:3][C:5]",
        "An ester forms from a carboxylic acid and an alcohol.",
        "acid catalyst, heat",
    ),
    RetroRule(
        "williamson_ether",
        "[CX4:1]-!@[OX2:2]-!@[CX4;H2,H3:3]>>[C:1][O:2].[C:3]Br",
        "An ether forms from an alkoxide (from an alcohol) and a primary alkyl bromide.",
        "strong base (e.g. NaH)",
    ),
    RetroRule(
        "suzuki_coupling",
        "[c:1]-!@[c:2]>>[c:1]Br.[c:2]B([OH])[OH]",
        "A biaryl bond forms between an aryl bromide and an arylboronic acid.",
        "palladium catalyst, base",
    ),
    RetroRule(
        "buchwald_amination",
        "[c:1]-!@[NX3;!$(N-C=O);!$(N-S=O):2]>>[c:1]Br.[N:2]",
        "An aryl-nitrogen bond forms between an aryl bromide and an amine.",
        "palladium catalyst, ligand, base",
    ),
    RetroRule(
        "reductive_amination",
        "[CX4;H1,H2:1]-!@[NX3;H0,H1;!$(N-C=O);!$(N-S=O):2]>>[C:1]=O.[N:2]",
        "An amine forms from an aldehyde or ketone and an amine, then reduction.",
        "reducing agent (e.g. NaBH(OAc)3)",
    ),
    RetroRule(
        "alcohol_oxidation_ketone",
        "[#6:1][CX3;H0:2](=[O:3])[#6:4]>>[#6:1][C:2]([#6:4])-[O:3]",
        "A ketone forms by oxidizing a secondary alcohol.",
        "oxidant (e.g. PCC or Dess-Martin periodinane)",
    ),
    RetroRule(
        "alcohol_oxidation_aldehyde",
        "[#6:1][CX3H1:2]=[O:3]>>[#6:1][C:2]-[O:3]",
        "An aldehyde forms by oxidizing a primary alcohol.",
        "mild oxidant (e.g. Dess-Martin periodinane)",
    ),
    RetroRule(
        "grignard_addition",
        "[#6:2][CX4;H0:1]([OH:5])([#6:3])-!@[#6:4]>>[#6:2][C:1](=[O:5])[#6:3].[#6:4]Br",
        "A tertiary alcohol forms when an organomagnesium reagent (made from "
        "the bromide) adds to a ketone.",
        "magnesium, dry ether, then aqueous workup",
    ),
    RetroRule(
        "sulfonamide_formation",
        "[#6:1][SX4:2](=[O:3])(=[O:4])-!@[NX3;H1,H2:5]>>"
        "[#6:1][S:2](=[O:3])(=[O:4])Cl.[N:5]",
        "A sulfonamide forms from a sulfonyl chloride and an amine.",
        "base (e.g. triethylamine)",
    ),
]

_CACHE = {}


def get_reaction(rule: RetroRule):
    if rule.name not in _CACHE:
        _CACHE[rule.name] = AllChem.ReactionFromSmarts(rule.smarts)
    return _CACHE[rule.name]
