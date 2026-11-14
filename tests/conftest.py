import sys
from pathlib import Path

# anomaly-engine/ has a hyphen and is not an importable package name.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "anomaly-engine"))
