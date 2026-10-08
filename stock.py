"""Toy library of purchasable building blocks shared by the demo and the tests."""
STOCK = [
    "CC(=O)O",                   # acetic acid
    "CCN", "CN",                 # ethylamine, methylamine
    "CCO", "CO",                 # ethanol, methanol
    "CBr", "CCBr",               # bromomethane, bromoethane
    "Brc1ccccc1",                # bromobenzene
    "OB(O)c1ccccc1",             # phenylboronic acid
    "Brc1ccc(C)cc1",             # 4-bromotoluene
    "Cc1ccc(B(O)O)cc1",          # 4-tolylboronic acid
    "OC(=O)c1ccccc1",            # benzoic acid
    "OC(=O)c1ccc(Br)cc1",        # 4-bromobenzoic acid
    "NCc1ccccc1",                # benzylamine
    "O=Cc1ccccc1",               # benzaldehyde
    "CC(O)c1ccccc1",             # 1-phenylethanol
    "Cc1ccc(S(=O)(=O)Cl)cc1",    # tosyl chloride
]

TARGETS = {
    "N-benzylbenzamide": "O=C(NCc1ccccc1)c1ccccc1",
    "4-methylbiphenyl": "Cc1ccc(-c2ccccc2)cc1",
    "N-ethylbenzylamine": "CCNCc1ccccc1",
    "2-phenylpropan-2-ol": "CC(C)(O)c1ccccc1",
    "N-benzyl tosylamide": "Cc1ccc(S(=O)(=O)NCc2ccccc2)cc1",
    "N-ethyl-4-phenylbenzamide": "CCNC(=O)c1ccc(-c2ccccc2)cc1",
    "caffeine (expect no route)": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
}
