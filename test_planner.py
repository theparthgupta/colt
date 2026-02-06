"""
Test suite for the LLM Task Planner
"""
import json
import os
from pathlib import Path
from src.planner.context_builder import ContextBuilder
from src.planner.llm_client import LLMClient
from src.planner.task_planner import TaskPlanner


def create_mock_exploration_data(output_dir: str):
    """Create mock exploration data for testing"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Mock agent data
    agent_data = {
        "auth_flows": {
            "has_login": True,
            "login_url": "http://localhost:3000/login",
            "login_method": "POST"
        },
        "validation_rules": [
            {
                "field": "email",
                "required": True,
                "email_format": True
            },
            {
                "field": "password",
                "required": True,
                "min": "8"
            }
        ]
    }

    # Mock action library
    action_library = [
        {
            "id": 0,
            "type": "click",
            "element": {
                "tag": "button",
                "text": "Submit",
                "selector": "#submit-btn",
                "class": "btn btn-primary"
            },
            "page_url": "http://localhost:3000/contact",
            "result": {
                "navigated": False,
                "changes": {"content_changed": True}
            }
        },
        {
            "id": 1,
            "type": "form_submission",
            "form": {
                "action": "/api/contact",
                "method": "POST",
                "fields": [
                    {"name": "name", "type": "text", "required": True},
                    {"name": "email", "type": "email", "required": True},
                    {"name": "message", "type": "textarea", "required": True}
                ]
            },
            "page_url": "http://localhost:3000/contact"
        },
        {
            "id": 2,
            "type": "click",
            "element": {
                "tag": "a",
                "text": "Login",
                "selector": "a[href='/login']",
                "class": "nav-link"
            },
            "page_url": "http://localhost:3000/",
            "result": {
                "navigated": True,
                "url_after": "http://localhost:3000/login"
            }
        }
    ]

    # Mock API map
    api_map = {
        "endpoints": [
            {
                "endpoint": "/api/contact",
                "method": "POST",
                "full_url": "http://localhost:3000/api/contact"
            },
            {
                "endpoint": "/api/auth/login",
                "method": "POST",
                "full_url": "http://localhost:3000/api/auth/login"
            },
            {
                "endpoint": "/api/users/:id",
                "method": "GET",
                "full_url": "http://localhost:3000/api/users/123"
            }
        ],
        "by_method": {
            "GET": ["/api/users/:id"],
            "POST": ["/api/contact", "/api/auth/login"]
        },
        "patterns": {
            "authentication": ["/api/auth/login"],
            "user_management": ["/api/users/:id"]
        }
    }

    # Mock state machine
    state_machine = {
        "states": [
            {
                "url": "http://localhost:3000/",
                "outgoing_transitions": []
            },
            {
                "url": "http://localhost:3000/contact",
                "outgoing_transitions": []
            },
            {
                "url": "http://localhost:3000/login",
                "outgoing_transitions": []
            }
        ],
        "transitions": [],
        "initial_state": "http://localhost:3000/"
    }

    # Mock user flows
    user_flows = [
        {
            "steps": [
                {
                    "action": "click",
                    "element": "Contact",
                    "url": "http://localhost:3000/",
                    "url_after": "http://localhost:3000/contact"
                },
                {
                    "action": "form_submission",
                    "element": "contact form",
                    "url": "http://localhost:3000/contact",
                    "url_after": "http://localhost:3000/contact"
                }
            ],
            "start_url": "http://localhost:3000/",
            "end_url": "http://localhost:3000/contact"
        }
    ]

    # Mock interaction graph
    interaction_graph = {
        "nodes": [
            {"id": 0, "url": "http://localhost:3000/", "label": "home"},
            {"id": 1, "url": "http://localhost:3000/contact", "label": "contact"},
            {"id": 2, "url": "http://localhost:3000/login", "label": "login"}
        ],
        "edges": [
            {"from": 0, "to": 1, "label": "Contact", "type": "click"},
            {"from": 0, "to": 2, "label": "Login", "type": "click"}
        ]
    }

    # Save all files
    files = {
        "agent_data.json": agent_data,
        "action_library.json": action_library,
        "api_map.json": api_map,
        "state_machine.json": state_machine,
        "user_flows.json": user_flows,
        "interaction_graph.json": interaction_graph,
    }

    for filename, data in files.items():
        with open(output_path / filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    print(f"[OK] Created mock exploration data in {output_dir}/")


def test_context_builder():
    """Test the ContextBuilder"""
    print("\n=== Testing ContextBuilder ===")

    output_dir = "test_output"
    create_mock_exploration_data(output_dir)

    builder = ContextBuilder(output_dir)

    # Test loading data
    success = builder.load_exploration_data()
    assert success, "Failed to load exploration data"
    print("[OK] Loaded exploration data")

    # Test building context
    context = builder.build_context_for_prompt("submit contact form")
    assert context is not None, "Failed to build context"
    assert context["prompt"] == "submit contact form"
    assert len(context["relevant_actions"]) > 0, "No relevant actions found"
    print(f"[OK] Built context with {len(context['relevant_actions'])} relevant actions")

    # Test keyword extraction
    keywords = builder._extract_keywords("submit the contact form with data")
    assert "submit" in keywords
    assert "contact" in keywords
    assert "form" in keywords
    print(f"[OK] Extracted keywords: {keywords}")

    # Test context formatting
    formatted = builder.format_context_for_llm(context)
    assert "USER REQUEST" in formatted
    assert "APPLICATION OVERVIEW" in formatted
    assert "RELEVANT ACTIONS" in formatted
    print("[OK] Formatted context for LLM")

    print("[OK] All ContextBuilder tests passed!")


def test_llm_client_mock():
    """Test the LLMClient (without actual API calls)"""
    print("\n=== Testing LLMClient (Mock) ===")

    # Test initialization
    try:
        client = LLMClient(provider="openai")
        print("[OK] Initialized OpenAI client")
    except ImportError:
        print("[WARN] OpenAI library not installed, skipping")
        return

    # Test validation
    mock_plan = {
        "task_description": "Submit contact form",
        "steps": [
            {
                "step_number": 1,
                "action_type": "navigate",
                "description": "Go to contact page",
                "target": {"url": "http://localhost:3000/contact"},
                "expected_outcome": "Contact page loads",
                "verification": "Check URL"
            },
            {
                "step_number": 2,
                "action_type": "fill_form",
                "description": "Fill the form",
                "target": {
                    "selector": "#contact-form",
                    "form_data": {"name": "Test", "email": "test@example.com"}
                },
                "expected_outcome": "Form is filled",
                "verification": "Check field values"
            }
        ],
        "prerequisites": ["User is logged in"],
        "expected_result": "Form submitted successfully",
        "confidence": 0.85
    }

    mock_actions = [
        {"id": 0, "type": "click", "element": {"text": "Submit"}},
        {"id": 1, "type": "form_submission", "form": {"action": "/contact"}}
    ]

    validation = client.validate_plan(mock_plan, mock_actions)
    assert validation is not None
    print(f"[OK] Plan validation: valid={validation['valid']}, "
          f"errors={len(validation['errors'])}, warnings={len(validation['warnings'])}")

    # Test with invalid plan
    invalid_plan = {
        "steps": [
            {"step_number": 1}  # Missing required fields
        ]
    }

    validation = client.validate_plan(invalid_plan, mock_actions)
    assert not validation["valid"]
    assert len(validation["errors"]) > 0
    print("[OK] Detected invalid plan")

    print("[OK] All LLMClient mock tests passed!")


def test_task_planner():
    """Test the TaskPlanner (without LLM API calls)"""
    print("\n=== Testing TaskPlanner ===")

    output_dir = "test_output"

    # Initialize planner (will fail without API key, but we can test initialization)
    try:
        planner = TaskPlanner(
            output_dir=output_dir,
            llm_provider="openai"
        )
        print("[OK] Initialized TaskPlanner")
    except Exception as e:
        print(f"[WARN] Could not initialize TaskPlanner (expected without API key): {e}")
        return

    # Test loading
    success = planner.load_exploration_data()
    assert success, "Failed to load exploration data"
    print("[OK] Loaded exploration data through TaskPlanner")

    # Test app summary
    summary = planner.get_app_summary()
    assert summary is not None
    assert len(summary) > 0
    print("[OK] Generated app summary")

    # Test explain plan
    mock_plan = {
        "task_description": "Test task",
        "steps": [
            {
                "step_number": 1,
                "action_type": "navigate",
                "description": "Go to page",
                "target": {"url": "http://localhost:3000"},
                "expected_outcome": "Page loads",
                "verification": "Check URL"
            }
        ],
        "prerequisites": [],
        "expected_result": "Success",
        "confidence": 0.9
    }

    explanation = planner.explain_plan(mock_plan)
    assert "ACTION PLAN" in explanation
    assert "Test task" in explanation
    assert "90.0%" in explanation  # Confidence
    print("[OK] Generated plan explanation")

    print("[OK] All TaskPlanner tests passed!")


def cleanup():
    """Clean up test files"""
    import shutil
    test_dir = "test_output"
    if Path(test_dir).exists():
        shutil.rmtree(test_dir)
        print(f"\n[OK] Cleaned up {test_dir}/")


def main():
    """Run all tests"""
    print("=" * 60)
    print("COLT Task Planner Test Suite")
    print("=" * 60)

    try:
        test_context_builder()
        test_llm_client_mock()
        test_task_planner()

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


if __name__ == "__main__":
    main()
