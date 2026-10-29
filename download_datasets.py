"""Download the datasets used by the skin-analysis training workflow."""
from pathlib import Path
from urllib.request import urlretrieve

from datasets import load_dataset


ROOT = Path(__file__).parent / "datasets"
ROOT.mkdir(exist_ok=True)

print("Downloading ACNE04 (the complete package is about 1.13 GB)...")
acne = load_dataset("Layered-Labs/ACNE04")
acne_path = ROOT / "ACNE04"
acne.save_to_disk(str(acne_path))
print(f"Saved ACNE04 to {acne_path}")

skincon_path = ROOT / "SkinCon"
skincon_path.mkdir(exist_ok=True)
for name in ("annotations_fitzpatrick17k.csv", "annotations_ddi.csv"):
    url = f"https://skincon-dataset.github.io/files/{name}"
    destination = skincon_path / name
    print(f"Downloading {name}...")
    urlretrieve(url, destination)
    print(f"Saved {destination}")

print("Done. Fitzpatrick17k and DDI source images require their separate access procedures.")
