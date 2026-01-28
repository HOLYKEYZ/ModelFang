import sys
import os

# Add current dir to path
sys.path.append(os.getcwd())

from modelfang.api import run_attack

print("Imported run_attack.")

try:
    print("Running Systematic attack...")
    res = run_attack(
        attack_id="systematic:jailbreak",
        target_model_id="target-llama3",
        context={"num_probes": 1},
        config_dir=None
    )
    print("Success!")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
