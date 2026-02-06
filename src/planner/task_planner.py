"""
Task Planner - Main orchestrator for converting prompts to action plans
"""
import json
from typing import Dict, Any, Optional
from pathlib import Path

from .context_builder import ContextBuilder
from .llm_client import LLMClient


class TaskPlanner:
    """
    Main Task Planner - Converts natural language prompts into executable action plans
    """

    def __init__(
        self,
        output_dir: str = "output",
        llm_provider: str = "openai",
        llm_model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        """
        Initialize Task Planner

        Args:
            output_dir: Directory containing exploration data
            llm_provider: LLM provider (openai, anthropic, local)
            llm_model: Specific model to use (optional)
            api_key: API key for the LLM provider (optional, uses env vars)
            temperature: LLM temperature (0-1)
            max_tokens: Maximum tokens for LLM response
        """
        self.output_dir = output_dir
        self.context_builder = ContextBuilder(output_dir)
        self.llm_client = LLMClient(
            provider=llm_provider,
            model=llm_model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        self.exploration_loaded = False

    def load_exploration_data(self) -> bool:
        """Load exploration data from output directory"""
        print(f"Loading exploration data from {self.output_dir}...")
        success = self.context_builder.load_exploration_data()

        if success:
            self.exploration_loaded = True
            print("✓ Exploration data loaded successfully")
        else:
            print("✗ Failed to load exploration data")

        return success

    def plan_task(self, user_prompt: str, save_plan: bool = True) -> Dict[str, Any]:
        """
        Generate an action plan for a user's natural language request

        Args:
            user_prompt: User's task description in natural language
            save_plan: Whether to save the generated plan to disk

        Returns:
            Dictionary containing the plan and metadata
        """
        if not self.exploration_loaded:
            raise RuntimeError(
                "Exploration data not loaded. Call load_exploration_data() first."
            )

        print(f"\n{'='*60}")
        print(f"Planning task: {user_prompt}")
        print(f"{'='*60}\n")

        # Step 1: Build context for this specific prompt
        print("1. Building context from exploration data...")
        context = self.context_builder.build_context_for_prompt(user_prompt)
        formatted_context = self.context_builder.format_context_for_llm(context)

        print(f"   - Found {len(context['relevant_actions'])} relevant actions")
        print(f"   - Found {len(context['relevant_pages'])} relevant pages")
        print(f"   - Found {len(context['relevant_flows'])} relevant flows")
        print(f"   - Found {len(context['api_endpoints'])} relevant API endpoints")

        # Step 2: Generate plan using LLM
        print("\n2. Generating action plan with LLM...")
        plan = self.llm_client.generate_structured_plan(
            context=formatted_context,
            user_request=user_prompt,
        )

        print(f"   ✓ Generated plan with {len(plan.get('steps', []))} steps")

        # Step 3: Validate plan
        print("\n3. Validating plan...")
        validation = self.llm_client.validate_plan(
            plan,
            context['relevant_actions']
        )

        if validation["valid"]:
            print("   ✓ Plan is valid")
        else:
            print("   ⚠ Plan has errors:")
            for error in validation["errors"]:
                print(f"     - {error}")

        if validation["warnings"]:
            print("   Warnings:")
            for warning in validation["warnings"]:
                print(f"     - {warning}")

        # Step 4: Package result
        result = {
            "user_prompt": user_prompt,
            "plan": plan,
            "validation": validation,
            "context_summary": {
                "relevant_actions_count": len(context['relevant_actions']),
                "relevant_pages_count": len(context['relevant_pages']),
                "relevant_flows_count": len(context['relevant_flows']),
                "api_endpoints_count": len(context['api_endpoints']),
            },
        }

        # Step 5: Save plan if requested
        if save_plan:
            self._save_plan(result)

        return result

    def explain_plan(self, plan: Dict[str, Any]) -> str:
        """
        Generate a human-readable explanation of the action plan

        Args:
            plan: Action plan dictionary

        Returns:
            Formatted string explanation
        """
        lines = []

        lines.append("=" * 60)
        lines.append("ACTION PLAN")
        lines.append("=" * 60)
        lines.append("")

        lines.append(f"Task: {plan.get('task_description', 'N/A')}")
        lines.append("")

        if plan.get("prerequisites"):
            lines.append("Prerequisites:")
            for prereq in plan["prerequisites"]:
                lines.append(f"  • {prereq}")
            lines.append("")

        lines.append("Steps:")
        for step in plan.get("steps", []):
            step_num = step.get("step_number", "?")
            action_type = step.get("action_type", "unknown").upper()
            description = step.get("description", "N/A")

            lines.append(f"\n{step_num}. [{action_type}] {description}")

            target = step.get("target", {})
            if target.get("url"):
                lines.append(f"   URL: {target['url']}")
            if target.get("selector"):
                lines.append(f"   Selector: {target['selector']}")
            if target.get("text"):
                lines.append(f"   Element: '{target['text']}'")
            if target.get("form_data"):
                lines.append(f"   Form data: {json.dumps(target['form_data'], indent=6)}")

            expected = step.get("expected_outcome", "N/A")
            lines.append(f"   Expected: {expected}")

            verification = step.get("verification", "N/A")
            lines.append(f"   Verify: {verification}")

        lines.append("")
        lines.append(f"Expected Result: {plan.get('expected_result', 'N/A')}")

        if plan.get("potential_errors"):
            lines.append("")
            lines.append("Potential Errors:")
            for error in plan["potential_errors"]:
                lines.append(f"  ⚠ {error}")

        confidence = plan.get("confidence", 0)
        lines.append("")
        lines.append(f"Confidence: {confidence:.1%}")
        lines.append("=" * 60)

        return "\n".join(lines)

    def _save_plan(self, result: Dict[str, Any]):
        """Save the generated plan to disk"""
        output_path = Path(self.output_dir) / "generated_plans"
        output_path.mkdir(exist_ok=True)

        # Generate filename from prompt
        prompt_slug = result["user_prompt"][:50].replace(" ", "_").replace("/", "_")
        filename = f"plan_{prompt_slug}.json"

        file_path = output_path / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Plan saved to: {file_path}")

    def get_app_summary(self) -> str:
        """Get a summary of the explored application"""
        if not self.exploration_loaded:
            return "Exploration data not loaded."

        return self.context_builder.get_full_context_summary()

    def interactive_planning(self):
        """
        Interactive mode - continuously accept prompts and generate plans
        """
        if not self.exploration_loaded:
            print("Error: Exploration data not loaded. Call load_exploration_data() first.")
            return

        print("\n" + "=" * 60)
        print("COLT TASK PLANNER - Interactive Mode")
        print("=" * 60)
        print("\nCommands:")
        print("  - Enter a task description to generate a plan")
        print("  - 'summary' - Show application summary")
        print("  - 'quit' or 'exit' - Exit interactive mode")
        print("=" * 60 + "\n")

        while True:
            try:
                user_input = input("\n> ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nExiting interactive mode. Goodbye!")
                    break

                if user_input.lower() == 'summary':
                    print("\n" + self.get_app_summary())
                    continue

                # Generate plan
                result = self.plan_task(user_input, save_plan=True)

                # Display plan
                print("\n" + self.explain_plan(result["plan"]))

                # Ask if user wants to approve
                approve = input("\nApprove this plan? (yes/no): ").strip().lower()

                if approve in ['yes', 'y']:
                    print("✓ Plan approved! (Note: Execution not yet implemented)")
                else:
                    print("✗ Plan rejected")

            except KeyboardInterrupt:
                print("\n\nInterrupted. Exiting...")
                break
            except Exception as e:
                print(f"\n✗ Error: {e}")
                import traceback
                traceback.print_exc()
