"""
ModelFang CLI

Command-line interface for the ModelFang framework.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List

from modelfang.api import run_attack


def parse_args(args: List[str]):
    parser = argparse.ArgumentParser(description="ModelFang - AI Red Teaming Framework")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # RUN Command
    run_parser = subparsers.add_parser("run", help="Execute an attack")
    run_parser.add_argument("--attack", required=True, help="Attack ID or template:name")
    run_parser.add_argument("--model", required=True, help="Target model ID (from models.yaml)")
    run_parser.add_argument("--context", help="JSON string of context variables", default="{}")
    run_parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    run_parser.add_argument("--config", help="Path to configuration directory")
    run_parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])
    
    if args.command == "run":
        try:
            context = json.loads(args.context)
        except json.JSONDecodeError:
            print("Error: --context must be valid JSON")
            sys.exit(1)
            
        print(f"🚀 Initializing ModelFang Attack...")
        print(f"Target: {args.model}")
        print(f"Attack: {args.attack}")
        
        try:
            result = run_attack(
                attack_id=args.attack,
                target_model_id=args.model,
                context=context,
                seed=args.seed,
                config_dir=args.config
            )
            
            print("\n✅ Execution Complete")
            print(f"Status: {result['status']}")
            print(f"Score:  {result['success_score']:.2f}")
            print(f"Turns:  {result['turn_count']}")
            print(f"\nFull report saved to output directory.")
            
            if result['status'] == 'failed':
                sys.exit(1)
            sys.exit(0)
            
        except Exception as e:
            if args.verbose:
                import traceback
                traceback.print_exc()
            print(f"\n❌ Error during execution: {e}")
            sys.exit(1)
            
    else:
        print("ModelFang v0.3.0")
        print("Usage: modelfang run --attack <id> --model <id>")
        sys.exit(0)

if __name__ == "__main__":
    main()
