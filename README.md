reactlab

An explainable, logic-based retrosynthesis planner that can also learn from reaction data.

Give it a target molecule and a list of available building blocks. It works backward, step by step, and returns candidate synthesis routes where every step says which rule was used, why it applies, and under what typical conditions.

Research software. Output is a computational suggestion, not laboratory advice. Have a qualified chemist review any route before anyone attempts it.

What it does
Plans routes from a target molecule (SMILES) back to available building blocks, with multi-step search.
Explains every step with the rule or template applied, a plain-language reason, and typical conditions.
Combines knowledge sources: hand-written reaction rules, templates learned from reaction datasets (such as USPTO-50k), or both.
Accepts your own inputs: any target and any building-block list, with optional PubChem lookup.
Draws molecules and route schemes as images.
Evaluates itself on held-out reaction data with coverage and top-k accuracy.
Screens requests against a small set of safety alerts.

Some features arrived in later releases (for example learned templates and the command-line planner). If a command below is missing in your copy, check the Releases page for the version you have.

How it works
target SMILES ──► proposers ──► search ──► routes ──► ranking ──► explanation + images
                  │                │
                  ├ hand-written   └ stops at molecules that are
                  │  rules           available (your list / PubChem)
                  └ learned templates
A proposer suggests ways to break a molecule into simpler precursors. Proposers are interchangeable: hand-written rules, learned templates, or both.
A depth-limited search applies proposers recursively until every precursor is an available building block.
Routes are ranked by step count and, when learned templates are used, by how often the template appears in the training data.
Each route is printed with its reasoning and can be drawn as an image.
Installation

Requirements: Python 3.11, RDKit. A GPU is optional and only needed for the Hugging Face model checks and future model-based ranking.

Option A: conda

conda create -n reactlab -c conda-forge python=3.11 rdkit pip
conda activate reactlab
pip install transformers accelerate peft pandas pillow

Option B: pip and a virtual environment

python -m venv .venv
.venv\Scripts\activate          # Windows (use: source .venv/bin/activate on Linux/macOS)
pip install rdkit transformers accelerate peft pandas pillow

Optional pieces

Learned templates: pip install rdchiral --no-deps
GPU PyTorch: install the build matching your driver from https://pytorch.org/get-started/locally/

Verify the setup:

python check_setup.py
python run_tests.py
Quick start

Plan a route for any molecule:

python plan.py --target "CCNC(=O)c1ccc(-c2ccccc2)cc1" --blocks my_blocks.txt --draw

Run python plan.py with no arguments and it asks for the target and building blocks.

my_blocks.txt is a plain text file with one SMILES per line (# starts a comment):

CC(=O)O      # acetic acid
CCN          # ethylamine
OC(=O)c1ccc(Br)cc1

Other useful commands:

python plan.py --target "<SMILES>" --pubchem          # also use PubChem (see caveat below)
python draw.py                                        # draw example targets and routes
python draw.py mol "CCO" --name ethanol               # draw one molecule
python run_demo.py                                    # example routes for built-in targets
Learning from data

Train on one file, test on a different one, so the results are honest.

python learn_templates.py path/to/raw_train.csv --min-count 2
python benchmark.py path/to/raw_test.csv --rules both --templates models/templates.json
python plan.py --target "<SMILES>" --blocks my_blocks.txt --templates models/templates.json
Input: a CSV with atom-mapped reaction SMILES in the form reactants>reagents>product. USPTO-50k files work (raw_train.csv, raw_val.csv, raw_test.csv). If your column name differs, pass --col.
This repository does not include or redistribute any dataset. Download it yourself and check its license.
Options such as --top-templates and --beam trade completeness for speed.
Project layout
reactlab/
├── plan.py               command-line planner (any target, any building blocks)
├── learn_templates.py    learn templates from a reaction dataset
├── benchmark.py          coverage and top-k accuracy on a reaction file
├── draw.py               molecule, grid and route images
├── check_setup.py        GPU, RDKit and model-loading check
├── run_tests.py          expectation checks for the planner and safety screen
├── run_demo.py           example routes
├── stock.py              example targets and building blocks (demo and tests only)
├── my_blocks.txt         your building blocks (edit freely)
├── rules/
│   ├── retro_rules.py    hand-written rules with explanations and conditions
│   ├── proposers.py      rule sources (hand-written, learned, combined)
│   ├── planner.py        backward search
│   ├── availability.py   building-block sources (your list, PubChem)
│   ├── safety.py         structural-alert screen
│   └── chem.py           shared helpers
├── data/                 small sample reaction file
├── models/               learned templates (created by learn_templates.py)
└── cache/, images/       created automatically

Files may differ slightly between releases.

Evaluation

benchmark.py reports:

Coverage: how often any rule or template proposes something.
Top-k exact match (k = 1, 3, 5, 10): whether the documented reactants appear among the top k proposals.
Which rules or templates produced the correct answers.

Top-k is meaningful for learned templates, because hand-written rules all score equally. Results depend on the dataset, the split, and your settings, so report them together with those details.

Safety and responsible use
A structural-alert screen blocks targets and intermediates containing a few well-known chemical-weapon classes. It is intentionally minimal and not exhaustive. A real deployment needs a vetted, maintained list and human review.
There is no option to disable the screen.
Do not use this tool to plan the synthesis of harmful substances.
PubChem lookup is an assumption, not a purchasing check. A compound being listed in PubChem means it is known, not that it can be bought. Hits are limited to small molecules and are reported so you can verify them with a supplier.
Limitations
The hand-written rule set is small and each rule assumes specific leaving groups, so real-world coverage is limited.
Learned templates depend on the quality and scope of the training data (patent reactions) and ignore reaction conditions and yields.
Routes are ranked by step count and template frequency, not by predicted yield or cost.
Searches with many templates can be slow. Use --beam and --top-templates.
No stereochemistry or protein-level reasoning is guaranteed. Protein-related features are exploratory.
Versions

Each release has its own notes on the Releases page, including what changed and any upgrade steps. The commands in this README describe the full feature set; earlier releases may not include every file or option.

Roadmap
Neural route ranker using molecular embeddings (ChemBERTa)
More rules and leaving-group variants
Expanded, vetted safety list
Protein-side reactivity and structure visualization
Data, models and credits
RDKit for cheminformatics.
rdchiral for template extraction and application (Coley, Green, Jensen; J. Chem. Inf. Model. 2019).
USPTO reaction data (not included): users download and license-check their own copy.
Hugging Face models used for embeddings: ChemBERTa (seyonec/ChemBERTa-zinc-base-v1) and ESM-2 (facebook/esm2_t12_35M_UR50D). Check each model card for its license.
PubChem PUG REST service for optional lookups. Keep requests polite; the tool already throttles them.
Contributing

Issues and pull requests are welcome. Please run python run_tests.py before submitting changes, and describe any new rule with its explanation and typical conditions.

License

Apache 3

Citation

If you use this software in academic work, please cite it:

[Your name]. reactlab: an explainable, learnable retrosynthesis planner. GitHub, [year].
https://github.com/[your-username]/[repository]
