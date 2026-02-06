#!/usr/bin/env python3
"""
COLT Task Planner CLI
Command-line interface for generating action plans from natural language prompts
"""
import sys
import argparse
from pathlib import Path

from src.planner.task_planner import TaskPlanner
from config import Config


def main():
    parser = argparse.ArgumentParser(
        description="COLT Task Planner - Convert natural language to executable action plans",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python planner_cli.py

  # Single task planning
  python planner_cli.py "Submit the contact form with test data"

  # Show app summary
  python planner_cli.py --summary

  # Use different LLM provider
  python planner_cli.py --provider anthropic "Create a new user account"

  # Use local model
  python planner_cli.py --provider local --model llama2 "Login to the app"
        """
    )

    parser.add_argument(
        "prompt",
        nargs="?",
        help="Task description in natural language (if omitted, enters interactive mode)"
    )

    parser.add_argument(
        "--output-dir",
        default=Config.OUTPUT_DIR,
        help=f"Directory containing exploration data (default: {Config.OUTPUT_DIR})"
    )

    parser.add_argument(
        "--provider",
        choices=["openai", "anthropic", "local"],
        default=Config.LLM_PROVIDER,
        help=f"LLM provider to use (default: {Config.LLM_PROVIDER})"
    )

    parser.add_argument(
        "--model",
        default=Config.LLM_MODEL,
        help="Specific LLM model to use (default: provider's default model)"
    )

    parser.add_argument(
        "--api-key",
        default=Config.LLM_API_KEY,
        help="API key for LLM provider (default: from environment variable)"
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=Config.LLM_TEMPERATURE,
        help=f"LLM temperature 0-1 (default: {Config.LLM_TEMPERATURE})"
    )

    parser.add_argument(
        "--max-tokens",
        type=int,
        default=Config.LLM_MAX_TOKENS,
        help=f"Maximum tokens for LLM response (default: {Config.LLM_MAX_TOKENS})"
    )

    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show application summary and exit"
    )

    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save generated plans to disk"
    )

    args = parser.parse_args()

    # Check if output directory exists
    if not Path(args.output_dir).exists():
        print(f"Error: Output directory '{args.output_dir}' does not exist.")
        print("Please run the explorer first to generate exploration data.")
        sys.exit(1)

    # Initialize Task Planner
    print("Initializing COLT Task Planner...")
    planner = TaskPlanner(
        output_dir=args.output_dir,
        llm_provider=args.provider,
        llm_model=args.model,
        api_key=args.api_key,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )

    # Load exploration data
    if not planner.load_exploration_data():
        print("\nError: Could not load exploration data.")
        print("Please ensure the explorer has been run and generated the following files:")
        print("  - output/agent_data.json")
        print("  - output/action_library.json")
        print("  - output/api_map.json")
        print("  - output/state_machine.json")
        sys.exit(1)

    # Show summary if requested
    if args.summary:
        print("\n" + planner.get_app_summary())
        sys.exit(0)

    # Single task mode
    if args.prompt:
        try:
            result = planner.plan_task(args.prompt, save_plan=not args.no_save)
            print("\n" + planner.explain_plan(result["plan"]))

            # Show validation results
            validation = result["validation"]
            if not validation["valid"]:
                print("\n⚠ VALIDATION ERRORS:")
                for error in validation["errors"]:
                    print(f"  - {error}")

            if validation["warnings"]:
                print("\n⚠ WARNINGS:")
                for warning in validation["warnings"]:
                    print(f"  - {warning}")

            print(f"\nConfidence: {result['plan'].get('confidence', 0):.1%}")

        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    # Interactive mode
    else:
        try:
            planner.interactive_planning()
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()
