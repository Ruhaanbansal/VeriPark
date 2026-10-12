import sys
from pathlib import Path
sys.path.insert(0, str(Path("backend/src").resolve()))
from veripark.vericore.ledger import DecisionLedger

l = DecisionLedger(file_path="committed_ledger.jsonl")
valid, msg = l.verify_chain()
print("Committed ledger valid:", valid)
print("Committed ledger msg:", msg)
