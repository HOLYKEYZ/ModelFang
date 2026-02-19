"""
ModelFang CLI

Command-line interface for the ModelFang framework.
Supports running attacks, listing resources, and managing configurations.
"""

import argparse
import json
import logging
import sys
from typing import List, Optional

from modelfang.api import run_attack
from modelfang.config.loader import load_models_config

def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ModelFang - AI Red Teaming Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run standard template attack
  modelfang run --model target-llama3 --template standard

  # Run IRIS (Self-Jailbreak)
  modelfang run --model target-llama3 --iris "Write a keylogger" --attacker-model attacker-gemini

  # Run Policy Puppetry
  modelfang run --model target-gpt4 --puppetry "Bypass safety filters"

  # Run Weak-to-Strong (Logprob)
  modelfang run --model target-llama3 --weak-strong "Explain how to hack"

  # List available models
  modelfang list models
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # --- LIST Command ---
    list_parser = subparsers.add_parser("list", help="List available resources")
    list_parser.add_argument("resource", choices=["models", "strategies"], help="Resource type to list")
    list_parser.add_argument("--config", help="Path to configuration directory")
    
    # --- RUN Command ---
    run_parser = subparsers.add_parser("run", help="Execute an attack")
    
    # Target (Required)
    run_parser.add_argument("--model", required=True, help="Target model ID (from models.yaml)")
    
    # Context & Config
    run_parser.add_argument("--attacker-model", help="Attacker model ID (required for IRIS/Auto-Attack)")
    run_parser.add_argument("--context", help="JSON string of context variables", default="{}")
    run_parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    run_parser.add_argument("--config", help="Path to configuration directory")
    run_parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    # Attack Construction (Mutually Exclusive)
    group = run_parser.add_mutually_exclusive_group(required=True)
    
    # Phase 9: Advanced Techniques
    group.add_argument("--iris", metavar="GOAL", help="Run IRIS (Self-Jailbreak) attack with specified goal")
    group.add_argument("--gcg", metavar="GOAL", help="Run AmpleGCG (Transfer Suffix) attack with specified goal")
    group.add_argument("--puppetry", metavar="GOAL", help="Run Policy Puppetry (Framing) attack with specified goal")
    group.add_argument("--weak-strong", metavar="GOAL", help="Run Weak-to-Strong (Logprob) attack with specified goal")
    
    # Original Modes
    group.add_argument("--template", choices=["standard", "roles", "logic"], help="Run a standard attack template")
    group.add_argument("--systematic", metavar="PLUGINS", help="Run Systematic Probe (comma-separated plugins, e.g. 'jailbreak,pii')")
    group.add_argument("--dataset", metavar="ID", help="Run attack from dataset ID (e.g. 'jb_dan_11')")
    group.add_argument("--attacker", metavar="GOAL", help="Run Automated LLM-vs-LLM attack with specified goal")
    
    # Manual Override
    group.add_argument("--id", metavar="ATTACK_ID", help="Manual attack ID string (e.g. 'iris:goal', 'template:standard')")

    return parser

def handle_list(args):
    if args.resource == "models":
        try:
            config = load_models_config(args.config)
            print(f"\nTarget Models:")
            for m in config.get_targets():
                print(f"  - {m.model_id:<20} ({m.provider}: {m.model_name})")
            
            print(f"\nAttacker Models:")
            attackers = [m for m in config.models.values() if m.role == "attacker"]
            for m in attackers:
                print(f"  - {m.model_id:<20} ({m.provider}: {m.model_name})")
                
            print(f"\nEvaluator Models:")
            for m in config.get_evaluators():
                print(f"  - {m.model_id:<20} ({m.provider}: {m.model_name})")

        except Exception as e:
            print(f"Error loading config: {e}")
            
    elif args.resource == "strategies":
        print("\nAvailable Strategies:")
        print("  - Standard Templates: standard, roles, logic")
        print("  - Systematic Probe:   systematic:<plugins>")
        print("  - Dataset Attack:     dataset:<id>")
        print("  - Auto-LLM Attack:    attacker:<goal>")
        print("\nAdvanced Techniques (Phase 9):")
        print("  - IRIS:               iris:<goal>")
        print("  - Policy Puppetry:    puppetry:<goal>")
        print("  - AmpleGCG:           gcg:<goal>")
        print("  - Weak-to-Strong:     weak-strong:<goal>")

def handle_run(args):
    # Construct Attack ID based on flags
    attack_id = None
    context = {}
    
    try:
        context = json.loads(args.context)
    except json.JSONDecodeError:
        print("Error: --context must be valid JSON")
        sys.exit(1)
        
    # Inject attacker model into data/context if provided
    if args.attacker_model:
        context["attacker_model_id"] = args.attacker_model
    
    # Determine Attack ID
    if args.id:
        attack_id = args.id
    elif args.iris:
        attack_id = f"iris:{args.iris}"
        if not args.attacker_model:
            print("Warning: IRIS strategy usually requires --attacker-model. Using default if configured.")
    elif args.gcg:
        attack_id = f"gcg:{args.gcg}"
    elif args.puppetry:
        attack_id = f"puppetry:{args.puppetry}"
    elif args.weak_strong:
        attack_id = f"weak-strong:{args.weak_strong}"
    elif args.template:
        attack_id = f"template:{args.template}"
        # Templates usually need a goal in context, let's ask for it if missing?
        # Actually standard template has hardcoded goal or checks context.
        pass
    elif args.systematic:
        attack_id = f"systematic:{args.systematic}"
    elif args.dataset:
        attack_id = f"dataset:{args.dataset}"
    elif args.attacker:
        attack_id = "attacker:auto" 
        context["goal"] = args.attacker # Set goal in context for auto-attacker
        if not args.attacker_model:
            print("Warning: Attacker mode requires --attacker-model. Using default.")

    print(f"🚀 Initializing ModelFang Attack...")
    print(f"Target: {args.model}")
    print(f"Attack: {attack_id}")
    
    try:
        result = run_attack(
            attack_id=attack_id,
            target_model_id=args.model,
            context=context,
            seed=args.seed,
            config_dir=args.config
        )
        
        print("\n✅ Execution Complete")
        print(f"Status: {result.get('status', 'UNKNOWN')}")
        print(f"Score:  {result.get('success_score', 0.0):.2f}")
        print(f"Turns:  {result.get('turn_count', 0)}")
        
        if result.get('status') == 'failed':
            sys.exit(1)
        sys.exit(0)
        
    except Exception as e:
        if args.verbose:
            import traceback
            traceback.print_exc()
        print(f"\n❌ Error during execution: {e}")
        sys.exit(1)

def main():
    parser = setup_parser()
    args = parser.parse_args()
    
    if args.command == "list":
        handle_list(args)
    elif args.command == "run":
        handle_run(args)
    else:
        parser.print_help()
        sys.exit(0)

if __name__ == "__main__":
    main()
