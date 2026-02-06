#!/usr/bin/env python3
"""
COLT Plan Executor CLI
Execute LLM-generated action plans in the browser
"""
import sys
import argparse
import asyncio
from pathlib import Path

from src.executor.task_executor import TaskExecutor
from config import Config


async def execute_plan_async(args):
    """Execute a plan asynchronously"""
    # Check if plan file exists
    plan_path = Path(args.plan_file)
    if not plan_path.exists():
        print(f"Error: Plan file not found: {plan_path}")
        sys.exit(1)

    # Initialize executor
    print(f"Initializing Task Executor...")
    executor = TaskExecutor(
        headless=args.headless,
        slow_mo=args.slow_mo,
        timeout=args.timeout,
        screenshot_dir=args.screenshot_dir
    )

    try:
        # Initialize browser
        await executor.initialize()

        # Load plan
        print(f"\nLoading plan from: {plan_path}")
        plan = executor.load_plan(str(plan_path))

        print(f"Plan loaded: {plan.get('task_description', 'Unknown task')}")
        print(f"Steps: {len(plan.get('steps', []))}")

        # Show plan if requested
        if args.show_plan:
            print("\n" + "=" * 60)
            print("PLAN DETAILS")
            print("=" * 60)
            print(f"\nTask: {plan.get('task_description')}")
            print(f"\nSteps:")
            for i, step in enumerate(plan.get('steps', [])):
                step_num = step.get('step_number', i + 1)
                action_type = step.get('action_type', 'unknown')
                description = step.get('description', 'No description')
                print(f"  {step_num}. [{action_type.upper()}] {description}")

            print("\n" + "=" * 60)

            if not args.yes:
                response = input("\nProceed with execution? (yes/no): ").strip().lower()
                if response not in ['yes', 'y']:
                    print("Execution cancelled.")
                    return

        # Execute plan
        result = await executor.execute_plan(plan, save_report=not args.no_save)

        # Print summary
        executor.print_execution_summary(result)

        # Return exit code based on success
        return 0 if result['success'] else 1

    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user.")
        return 130

    except Exception as e:
        print(f"\nError during execution: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        # Cleanup
        await executor.cleanup()


def main():
    parser = argparse.ArgumentParser(
        description="COLT Plan Executor - Execute LLM-generated action plans",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Execute a plan with browser visible
  python execute_plan.py output/generated_plans/plan_submit_form.json

  # Execute in headless mode
  python execute_plan.py plan.json --headless

  # Show plan before executing
  python execute_plan.py plan.json --show-plan

  # Execute without confirmation
  python execute_plan.py plan.json --yes

  # Custom screenshot directory
  python execute_plan.py plan.json --screenshot-dir my_screenshots/
        """
    )

    parser.add_argument(
        "plan_file",
        help="Path to the plan JSON file"
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode (default: visible)"
    )

    parser.add_argument(
        "--slow-mo",
        type=int,
        default=Config.SLOW_MO,
        help=f"Slow down operations by N milliseconds (default: {Config.SLOW_MO})"
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=Config.TIMEOUT,
        help=f"Timeout for operations in milliseconds (default: {Config.TIMEOUT})"
    )

    parser.add_argument(
        "--screenshot-dir",
        default="output/execution_screenshots",
        help="Directory to save screenshots (default: output/execution_screenshots)"
    )

    parser.add_argument(
        "--show-plan",
        action="store_true",
        help="Show plan details before execution"
    )

    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip confirmation prompt"
    )

    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save execution report"
    )

    args = parser.parse_args()

    # Run async executor
    exit_code = asyncio.run(execute_plan_async(args))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
