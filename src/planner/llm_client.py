"""
LLM Client - Handles communication with LLM APIs (OpenAI, Anthropic, local models)
"""
import json
import os
from typing import Dict, Any, Optional, List
from enum import Enum


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class LLMClient:
    """Client for interacting with various LLM providers"""

    def __init__(
        self,
        provider: str = "openai",
        model: str = None,
        api_key: str = None,
        base_url: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        self.provider = LLMProvider(provider)
        self.model = model or self._get_default_model()
        self.api_key = api_key or self._get_api_key()
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize provider-specific client
        self.client = None
        self._initialize_client()

    def _get_default_model(self) -> str:
        """Get default model for the provider"""
        defaults = {
            LLMProvider.OPENAI: "gpt-4-turbo-preview",
            LLMProvider.ANTHROPIC: "claude-3-5-sonnet-20241022",
            LLMProvider.LOCAL: "llama2",
        }
        return defaults.get(self.provider, "gpt-4-turbo-preview")

    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment variables"""
        if self.provider == LLMProvider.OPENAI:
            return os.environ.get("OPENAI_API_KEY")
        elif self.provider == LLMProvider.ANTHROPIC:
            return os.environ.get("ANTHROPIC_API_KEY")
        return None

    def _initialize_client(self):
        """Initialize the provider-specific client"""
        try:
            if self.provider == LLMProvider.OPENAI:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            elif self.provider == LLMProvider.ANTHROPIC:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            elif self.provider == LLMProvider.LOCAL:
                # For local models (e.g., Ollama)
                import requests
                self.client = requests.Session()
                self.base_url = self.base_url or "http://localhost:11434"
        except ImportError as e:
            raise ImportError(
                f"Required library for {self.provider.value} not installed. "
                f"Install with: pip install {self._get_install_package()}"
            )

    def _get_install_package(self) -> str:
        """Get the pip package name for the provider"""
        packages = {
            LLMProvider.OPENAI: "openai",
            LLMProvider.ANTHROPIC: "anthropic",
            LLMProvider.LOCAL: "requests",
        }
        return packages.get(self.provider, "")

    def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate a completion from the LLM

        Args:
            system_prompt: System instructions for the LLM
            user_prompt: User's request/prompt
            response_format: Optional JSON schema for structured output

        Returns:
            LLM's response as a string
        """
        try:
            if self.provider == LLMProvider.OPENAI:
                return self._openai_completion(system_prompt, user_prompt, response_format)
            elif self.provider == LLMProvider.ANTHROPIC:
                return self._anthropic_completion(system_prompt, user_prompt, response_format)
            elif self.provider == LLMProvider.LOCAL:
                return self._local_completion(system_prompt, user_prompt)
        except Exception as e:
            raise RuntimeError(f"Error generating completion: {e}")

    def _openai_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate completion using OpenAI API"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        # Add JSON mode if response format specified
        if response_format:
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    def _anthropic_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate completion using Anthropic API"""
        # Add JSON formatting instruction if response format specified
        if response_format:
            user_prompt += "\n\nPlease respond with valid JSON only."

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        return response.content[0].text

    def _local_completion(self, system_prompt: str, user_prompt: str) -> str:
        """Generate completion using local model (Ollama)"""
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "temperature": self.temperature,
            "stream": False,
        }

        response = self.client.post(url, json=payload)
        response.raise_for_status()

        return response.json()["response"]

    def generate_structured_plan(
        self,
        context: str,
        user_request: str,
    ) -> Dict[str, Any]:
        """
        Generate a structured action plan from the LLM

        Args:
            context: Application context (from ContextBuilder)
            user_request: User's natural language request

        Returns:
            Structured action plan as a dictionary
        """
        system_prompt = """You are an AI task planner for web automation. Your job is to create detailed, step-by-step action plans for automating tasks in web applications.

Given information about a web application (available pages, actions, forms, APIs, etc.) and a user's request, generate a precise action plan.

The action plan should be a JSON object with this structure:
{
    "task_description": "Brief description of the task",
    "steps": [
        {
            "step_number": 1,
            "action_type": "navigate|click|fill_form|wait|verify",
            "description": "What this step does",
            "target": {
                "selector": "CSS selector or element identifier",
                "url": "URL if navigating",
                "text": "Element text if clicking",
                "form_data": {"field": "value"} // if filling form
            },
            "expected_outcome": "What should happen after this step",
            "verification": "How to verify this step succeeded"
        }
    ],
    "prerequisites": ["List of things that must be true before starting"],
    "expected_result": "What the final outcome should be",
    "potential_errors": ["List of things that might go wrong"],
    "confidence": 0.0-1.0 // How confident you are this plan will work
}

Be specific with selectors, URLs, and form field names. Use information from the provided context."""

        user_prompt = f"{context}\n\n=== TASK TO PLAN ===\n{user_request}\n\nGenerate a detailed action plan in JSON format."

        response = self.generate_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format={"type": "json_object"}
        )

        # Parse JSON response
        try:
            plan = json.loads(response)
            return plan
        except json.JSONDecodeError:
            # Try to extract JSON from response if wrapped in markdown
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
                return json.loads(json_str)
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
                return json.loads(json_str)
            else:
                raise ValueError(f"Could not parse JSON from LLM response: {response}")

    def validate_plan(self, plan: Dict[str, Any], available_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a generated plan against available actions

        Args:
            plan: Generated action plan
            available_actions: List of available actions from exploration

        Returns:
            Validation result with errors/warnings
        """
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
        }

        if not plan.get("steps"):
            validation["valid"] = False
            validation["errors"].append("Plan has no steps")
            return validation

        # Check each step
        for i, step in enumerate(plan["steps"]):
            step_num = step.get("step_number", i + 1)

            # Check required fields
            if not step.get("action_type"):
                validation["errors"].append(f"Step {step_num}: Missing action_type")
                validation["valid"] = False

            if not step.get("description"):
                validation["warnings"].append(f"Step {step_num}: Missing description")

            if not step.get("expected_outcome"):
                validation["warnings"].append(f"Step {step_num}: Missing expected_outcome")

            # Validate action type
            valid_actions = ["navigate", "click", "fill_form", "wait", "verify", "submit"]
            action_type = step.get("action_type", "").lower()
            if action_type not in valid_actions:
                validation["warnings"].append(
                    f"Step {step_num}: Unknown action_type '{action_type}'. "
                    f"Expected one of: {', '.join(valid_actions)}"
                )

        # Check confidence
        confidence = plan.get("confidence", 0)
        if confidence < 0.5:
            validation["warnings"].append(
                f"Low confidence ({confidence:.1%}). Plan may not work as expected."
            )

        return validation
