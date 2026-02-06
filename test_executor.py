"""
Test suite for the Task Executor
"""
import json
import asyncio
from pathlib import Path


def create_mock_plan(output_dir: str = "test_output"):
    """Create a mock action plan for testing"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    plan = {
        "task_description": "Test navigation and verification",
        "steps": [
            {
                "step_number": 1,
                "action_type": "navigate",
                "description": "Navigate to example.com",
                "target": {
                    "url": "https://example.com"
                },
                "expected_outcome": "Page loads successfully",
                "verification": "Check URL contains 'example.com'"
            },
            {
                "step_number": 2,
                "action_type": "verify",
                "description": "Verify page title exists",
                "target": {
                    "text": "Example Domain"
                },
                "expected_outcome": "Title is visible",
                "verification": "Check for 'Example Domain' text"
            },
            {
                "step_number": 3,
                "action_type": "wait",
                "description": "Wait 2 seconds",
                "target": {
                    "duration": 2000
                },
                "expected_outcome": "Wait completes",
                "verification": "No verification needed"
            }
        ],
        "prerequisites": ["Internet connection"],
        "expected_result": "Successfully navigate to example.com and verify content",
        "confidence": 1.0
    }

    plan_file = output_path / "test_plan.json"
    with open(plan_file, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2)

    print(f"[OK] Created mock plan: {plan_file}")
    return str(plan_file)


async def test_executor_initialization():
    """Test TaskExecutor initialization"""
    print("\n=== Testing TaskExecutor Initialization ===")

    from src.executor.task_executor import TaskExecutor

    executor = TaskExecutor(headless=True)

    try:
        await executor.initialize()
        print("[OK] Executor initialized")

        assert executor.page is not None, "Page not initialized"
        assert executor.action_handlers is not None, "Action handlers not initialized"
        assert executor.verifier is not None, "Verifier not initialized"

        print("[OK] All components initialized")

    finally:
        await executor.cleanup()
        print("[OK] Executor cleaned up")


async def test_plan_loading():
    """Test loading a plan from file"""
    print("\n=== Testing Plan Loading ===")

    from src.executor.task_executor import TaskExecutor

    # Create mock plan
    plan_file = create_mock_plan()

    executor = TaskExecutor()

    # Test loading
    plan = executor.load_plan(plan_file)

    assert plan is not None, "Plan not loaded"
    assert 'task_description' in plan, "Missing task_description"
    assert 'steps' in plan, "Missing steps"
    assert len(plan['steps']) > 0, "No steps in plan"

    print(f"[OK] Loaded plan: {plan['task_description']}")
    print(f"[OK] Steps: {len(plan['steps'])}")

    # Clean up
    Path(plan_file).unlink()
    Path(plan_file).parent.rmdir()


async def test_simple_execution():
    """Test executing a simple plan"""
    print("\n=== Testing Simple Plan Execution ===")

    from src.executor.task_executor import TaskExecutor

    # Create mock plan
    plan_file = create_mock_plan()

    executor = TaskExecutor(headless=True, slow_mo=100)

    try:
        await executor.initialize()

        plan = executor.load_plan(plan_file)

        print(f"\nExecuting plan: {plan['task_description']}")

        result = await executor.execute_plan(plan, save_report=False)

        print(f"\n[OK] Execution completed")
        print(f"    Success: {result['success']}")
        print(f"    Steps executed: {result['steps_executed']}/{result['steps_total']}")

        # Verify results
        assert result['steps_executed'] > 0, "No steps executed"
        assert 'step_results' in result, "Missing step results"

        for step_result in result['step_results']:
            step_num = step_result['step_number']
            success = step_result['success']
            action_type = step_result['action_type']

            status = "[OK]" if success else "[FAIL]"
            print(f"    {status} Step {step_num}: {action_type}")

            if not success and step_result.get('error'):
                print(f"        Error: {step_result['error']}")

    finally:
        await executor.cleanup()

        # Clean up
        Path(plan_file).unlink()
        Path(plan_file).parent.rmdir()


async def test_action_handlers():
    """Test individual action handlers"""
    print("\n=== Testing Action Handlers ===")

    from src.executor.task_executor import TaskExecutor

    executor = TaskExecutor(headless=True)

    try:
        await executor.initialize()

        # Test navigate
        print("\n1. Testing NAVIGATE action...")
        nav_step = {
            "action_type": "navigate",
            "target": {"url": "https://example.com"}
        }

        result = await executor.action_handlers.navigate(nav_step)
        assert result['success'], "Navigate failed"
        assert 'example.com' in result['url'], "Wrong URL"
        print("   [OK] Navigate action works")

        # Test wait
        print("\n2. Testing WAIT action...")
        wait_step = {
            "action_type": "wait",
            "target": {"duration": 500}
        }

        result = await executor.action_handlers.wait(wait_step)
        assert result['success'], "Wait failed"
        print("   [OK] Wait action works")

        # Test verify
        print("\n3. Testing VERIFY action...")
        verify_step = {
            "action_type": "verify",
            "target": {"text": "Example Domain"}
        }

        result = await executor.action_handlers.verify(verify_step)
        assert result['success'], "Verify failed"
        print("   [OK] Verify action works")

    finally:
        await executor.cleanup()


async def test_verification():
    """Test verification system"""
    print("\n=== Testing Verification System ===")

    from src.executor.task_executor import TaskExecutor

    executor = TaskExecutor(headless=True)

    try:
        await executor.initialize()

        # Navigate to example.com
        await executor.page.goto("https://example.com")

        # Test URL verification
        print("\n1. Testing URL verification...")
        step = {
            "action_type": "navigate",
            "expected_outcome": "Navigated to example.com"
        }
        result = {"success": True, "status": 200}

        verification = await executor.verifier.verify_step_outcome(step, result)
        assert verification['passed'], "Verification failed"
        print("   [OK] URL verification works")

        # Test page state verification
        print("\n2. Testing page state verification...")
        expected_state = {
            "url": "example.com",
            "text": "Example Domain"
        }

        verification = await executor.verifier.verify_page_state(expected_state)
        assert verification['passed'], "Page state verification failed"
        print("   [OK] Page state verification works")

    finally:
        await executor.cleanup()


def cleanup():
    """Clean up test files"""
    import shutil
    test_dir = "test_output"
    if Path(test_dir).exists():
        shutil.rmtree(test_dir)
        print(f"\n[OK] Cleaned up {test_dir}/")


async def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("COLT Task Executor Test Suite")
    print("=" * 60)

    try:
        await test_executor_initialization()
        await test_plan_loading()
        await test_action_handlers()
        await test_verification()
        await test_simple_execution()

        print("\n" + "=" * 60)
        print("[OK] ALL TESTS PASSED!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()

    except Exception as e:
        print(f"\n[FAIL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        cleanup()


def main():
    """Run tests"""
    asyncio.run(run_all_tests())


if __name__ == "__main__":
    main()
