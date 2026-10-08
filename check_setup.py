"""Step 1: verify GPU, RDKit and both Hugging Face models load within 6 GB VRAM."""
import torch
from transformers import AutoModel, AutoTokenizer

CHEM_MODEL = "seyonec/ChemBERTa-zinc-base-v1"   # SMILES model
PROT_MODEL = "facebook/esm2_t12_35M_UR50D"      # protein sequence model (35M)


def vram_gb():
    return torch.cuda.memory_allocated() / 1e9 if torch.cuda.is_available() else 0.0


def embed(name, text, device, dtype):
    tok = AutoTokenizer.from_pretrained(name)
    model = AutoModel.from_pretrained(name, dtype=dtype).to(device).eval()
    with torch.no_grad():
        batch = tok(text, return_tensors="pt").to(device)
        vec = model(**batch).last_hidden_state.mean(dim=1)
    print(f"{name}: embedding shape {tuple(vec.shape)}, VRAM in use {vram_gb():.2f} GB")
    return vec.float().cpu()


if __name__ == "__main__":
    cuda = torch.cuda.is_available()
    print("torch", torch.__version__, "| CUDA available:", cuda)
    if cuda:
        props = torch.cuda.get_device_properties(0)
        print("GPU:", props.name, f"| total VRAM {props.total_memory / 1e9:.1f} GB")

    from rdkit import Chem
    print("RDKit OK, ethanol canonical SMILES:", Chem.MolToSmiles(Chem.MolFromSmiles("OCC")))

    device = "cuda" if cuda else "cpu"
    dtype = torch.float16 if cuda else torch.float32
    chem = embed(CHEM_MODEL, "CC(=O)NCC", device, dtype)
    prot = embed(PROT_MODEL, "MKTAYIAKQRQISFVKSHFSRQ", device, dtype)
    print("Fused vector size:", torch.cat([chem, prot], dim=1).shape[1])
