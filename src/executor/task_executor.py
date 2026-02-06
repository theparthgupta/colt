"""
Task Executor - Main orchestrator for executing action plans
"""
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

from .action_handlers import ActionHandlers
from .verification import Verifier


class TaskExecutor:
    """
    Main Task Executor - Executes LLM-generated action plans in the browser
    """

    def __init__(
        self,
        headless: bool = False,
        slow_mo: int = 500,
        timeout: int = 30000,
        screenshot_dir: str = "output/execution_screenshots"
    ):
        """
        Initialize Task Executor

        Args:
            headless: Run browser in headless mode
            slow_mo: Slow down operations by N ms (for visibility)
            timeout: Default timeout for operations in ms
            screenshot_dir: Directory to save screenshots
        """
        self.headless = headless
        self.slow_mo = slow_mo
        self.timeout = timeout
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        self.action_handlers: Optional[ActionHandlers] = None
        self.verifier: Optional[Verifier] = None

        self.execution_log = []

    async def initialize(self):
        """Initialize Playwright and browser"""
        print("Initializing browser...")

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = await self.context.new_page()

        # Initialize handlers
        self.action_handlers = ActionHandlers(self.page, self.timeout)
        self.verifier = Verifier(self.page)

        print(f"[OK] Browser initialized (headless={self.headless})")

    async def cleanup(self):
        """Clean up browser resources"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

        print("[OK] Browser cleaned up")

    async def execute_plan(self, plan: Dict[str, Any], save_report: bool = True) -> Dict[str, Any]:
        """
        Execute an action plan

        Args:
            plan: The action plan dictionary
            save_report: Whether to save execution report

        Returns:
            Execution result with status and details
        """
        if not self.page:
            raise RuntimeError("Browser not initialized. Call initialize() first.")

        print("\n" + "=" * 60)
        print("EXECUTING ACTION PLAN")
        print("=" * 60)

        task_description = plan.get('task_description', 'Unknown task')
        steps = plan.get('steps', [])

        print(f"\nTask: {task_description}")
        print(f"Steps: {len(steps)}")
        print("")

        execution_result = {
            'task': task_description,
            'started_at': datetime.now().isoformat(),
            'completed_at': None,
            'success': False,
            'steps_executed': 0,
            'steps_total': len(steps),
            'step_results': [],
            'errors': [],
            'screenshots': []
        }

        try:
            # Execute each step
            for i, step in enumerate(steps):
                step_num = step.get('step_number', i + 1)
                action_type = step.get('action_type', 'unknown')
                description = step.get('description', 'No description')

                print(f"Step {step_num}/{len(steps)}: [{action_type.upper()}] {description}")

                step_result = await self._execute_step(step, step_num)

                execution_result['step_results'].append(step_result)

                if not step_result['success']:
                    print(f"  X Step failed: {step_result.get('error', 'Unknown error')}")
                    execution_result['errors'].append({
                        'step': step_num,
                        'error': step_result.get('error'),
                        'action_type': action_type
                    })

                    # Decide whether to continue or stop
                    if step_result.get('fatal', False):
                        print(f"\nX Fatal error in step {step_num}. Stopping execution.")
                        break
                else:
                    print(f"  [OK] Step completed successfully")
                    execution_result['steps_executed'] += 1

                # Brief pause between steps
                await asyncio.sleep(1)

            # Determine overall success
            execution_result['success'] = (
                execution_result['steps_executed'] == execution_result['steps_total'] and
                len(execution_result['errors']) == 0
            )

            execution_result['completed_at'] = datetime.now().isoformat()

            print("\n" + "=" * 60)
            if execution_result['success']:
                print("[OK] PLAN EXECUTED SUCCESSFULLY")
            else:
                print(f"X PLAN EXECUTION FAILED")
                print(f"  Executed: {execution_result['steps_executed']}/{execution_result['steps_total']} steps")
                print(f"  Errors: {len(execution_result['errors'])}")
            print("=" * 60)

        except Exception as e:
            execution_result['completed_at'] = datetime.now().isoformat()
            execution_result['errors'].append({
                'step': 'execution',
                'error': str(e),
                'fatal': True
            })
            print(f"\nX Execution error: {str(e)}")

        finally:
            # Save report if requested
            if save_report:
                self._save_execution_report(execution_result, plan)

        return execution_result

    async def _execute_step(self, step: Dict[str, Any], step_num: int) -> Dict[str, Any]:
        """Execute a single step"""
        action_type = step.get('action_type', '').lower()

        step_result = {
            'step_number': step_num,
            'action_type': action_type,
            'success': False,
            'started_at': datetime.now().isoformat(),
            'completed_at': None,
            'action_result': None,
            'verification': None,
            'screenshot': None,
            'error': None,
            'fatal': False
        }

        try:
            # Take before screenshot
            before_screenshot = self.screenshot_dir / f"step_{step_num:02d}_before.png"
            await self.page.screenshot(path=str(before_screenshot), full_page=False)
            step_result['screenshot_before'] = str(before_screenshot)

            # Store URL before action
            url_before = self.page.url

            # Execute the action
            action_result = await self._dispatch_action(action_type, step)
            action_result['url_before'] = url_before
            step_result['action_result'] = action_result

            # Take after screenshot
            after_screenshot = self.screenshot_dir / f"step_{step_num:02d}_after.png"
            await self.page.screenshot(path=str(after_screenshot), full_page=False)
            step_result['screenshot_after'] = str(after_screenshot)

            # Verify the outcome
            verification = await self.verifier.verify_step_outcome(step, action_result)
            step_result['verification'] = verification

            # Determine success
            step_result['success'] = action_result.get('success', False) and verification.get('passed', True)

            if not step_result['success']:
                if verification.get('errors'):
                    step_result['error'] = '; '.join(verification['errors'])
                elif not action_result.get('success'):
                    step_result['error'] = action_result.get('error', 'Action failed')

        except Exception as e:
            step_result['error'] = str(e)
            step_result['fatal'] = True

            # Take error screenshot
            error_screenshot = self.screenshot_dir / f"step_{step_num:02d}_error.png"
            try:
                await self.page.screenshot(path=str(error_screenshot), full_page=False)
                step_result['screenshot_error'] = str(error_screenshot)
            except:
                pass

        finally:
            step_result['completed_at'] = datetime.now().isoformat()

        return step_result

    async def _dispatch_action(self, action_type: str, step: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch action to appropriate handler"""
        handlers_map = {
            'navigate': self.action_handlers.navigate,
            'click': self.action_handlers.click,
            'fill_form': self.action_handlers.fill_form,
            'submit': self.action_handlers.submit,
            'wait': self.action_handlers.wait,
            'verify': self.action_handlers.verify,
            'type': self.action_handlers.type_text,
            'type_text': self.action_handlers.type_text,
        }

        handler = handlers_map.get(action_type)

        if not handler:
            raise ValueError(f"Unknown action type: {action_type}")

        return await handler(step)

    def _save_execution_report(self, execution_result: Dict[str, Any], plan: Dict[str, Any]):
        """Save execution report to disk"""
        output_dir = Path("output/execution_reports")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_slug = plan.get('task_description', 'task')[:50].replace(' ', '_').replace('/', '_')
        filename = f"execution_{task_slug}_{timestamp}.json"

        file_path = output_dir / filename

        # Combine plan and execution result
        report = {
            'plan': plan,
            'execution': execution_result
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n[OK] Execution report saved: {file_path}")

    def load_plan(self, plan_path: str) -> Dict[str, Any]:
        """Load a plan from JSON file"""
        with open(plan_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle both plain plans and result objects from planner
        if 'plan' in data:
            return data['plan']
        return data

    def print_execution_summary(self, execution_result: Dict[str, Any]):
        """Print a human-readable execution summary"""
        print("\n" + "=" * 60)
        print("EXECUTION SUMMARY")
        print("=" * 60)

        print(f"\nTask: {execution_result['task']}")
        print(f"Status: {'SUCCESS' if execution_result['success'] else 'FAILED'}")
        print(f"Steps: {execution_result['steps_executed']}/{execution_result['steps_total']}")
        print(f"Duration: {execution_result['started_at']} to {execution_result['completed_at']}")

        if execution_result['errors']:
            print(f"\nErrors ({len(execution_result['errors'])}):")
            for error in execution_result['errors']:
                print(f"  - Step {error['step']}: {error['error']}")

        print("\nStep Details:")
        for step_result in execution_result['step_results']:
            step_num = step_result['step_number']
            action_type = step_result['action_type']
            success = '[OK]' if step_result['success'] else 'X'

            print(f"  {success} Step {step_num}: {action_type.upper()}")

            if step_result.get('verification'):
                verification = step_result['verification']
                if verification.get('warnings'):
                    for warning in verification['warnings']:
                        print(f"      ⚠ {warning}")

        print("=" * 60)
