"""
Context Builder - Loads and prepares exploration data for LLM consumption
"""
import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path


class ContextBuilder:
    """Builds optimized context from exploration data for LLM planning"""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.agent_data = None
        self.action_library = None
        self.api_map = None
        self.state_machine = None
        self.user_flows = None
        self.interaction_graph = None

    def load_exploration_data(self) -> bool:
        """Load all exploration data from output directory"""
        try:
            # Load agent data (main knowledge base)
            agent_data_path = self.output_dir / "agent_data.json"
            if agent_data_path.exists():
                with open(agent_data_path, 'r', encoding='utf-8') as f:
                    self.agent_data = json.load(f)

            # Load action library
            action_lib_path = self.output_dir / "action_library.json"
            if action_lib_path.exists():
                with open(action_lib_path, 'r', encoding='utf-8') as f:
                    self.action_library = json.load(f)

            # Load API map
            api_map_path = self.output_dir / "api_map.json"
            if api_map_path.exists():
                with open(api_map_path, 'r', encoding='utf-8') as f:
                    self.api_map = json.load(f)

            # Load state machine
            state_machine_path = self.output_dir / "state_machine.json"
            if state_machine_path.exists():
                with open(state_machine_path, 'r', encoding='utf-8') as f:
                    self.state_machine = json.load(f)

            # Load user flows
            user_flows_path = self.output_dir / "user_flows.json"
            if user_flows_path.exists():
                with open(user_flows_path, 'r', encoding='utf-8') as f:
                    self.user_flows = json.load(f)

            # Load interaction graph
            interaction_graph_path = self.output_dir / "interaction_graph.json"
            if interaction_graph_path.exists():
                with open(interaction_graph_path, 'r', encoding='utf-8') as f:
                    self.interaction_graph = json.load(f)

            return True
        except Exception as e:
            print(f"Error loading exploration data: {e}")
            return False

    def build_context_for_prompt(self, user_prompt: str, max_tokens: int = 8000) -> Dict[str, Any]:
        """
        Build optimized context for a specific user prompt
        Uses relevance scoring to include most pertinent information
        """
        if not self.agent_data:
            raise ValueError("Exploration data not loaded. Call load_exploration_data() first.")

        context = {
            "prompt": user_prompt,
            "app_overview": self._build_app_overview(),
            "relevant_actions": self._find_relevant_actions(user_prompt),
            "relevant_pages": self._find_relevant_pages(user_prompt),
            "relevant_flows": self._find_relevant_flows(user_prompt),
            "api_endpoints": self._get_relevant_api_endpoints(user_prompt),
            "validation_rules": self._get_validation_rules(),
            "auth_info": self._get_auth_info(),
        }

        return context

    def _build_app_overview(self) -> Dict[str, Any]:
        """Build high-level app overview"""
        overview = {
            "description": "Web application explored by COLT",
            "total_pages": len(self.state_machine.get('states', [])) if self.state_machine else 0,
            "total_actions": len(self.action_library) if self.action_library else 0,
            "has_auth": False,
            "key_features": [],
        }

        # Check for authentication
        if self.agent_data and self.agent_data.get('auth_flows', {}).get('has_login'):
            overview['has_auth'] = True
            overview['login_url'] = self.agent_data['auth_flows'].get('login_url')

        # Identify key features from API patterns
        if self.api_map and self.api_map.get('patterns'):
            overview['key_features'] = list(self.api_map['patterns'].keys())

        return overview

    def _find_relevant_actions(self, prompt: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Find actions relevant to the user prompt"""
        if not self.action_library:
            return []

        # Simple keyword-based relevance (can be enhanced with embeddings)
        prompt_lower = prompt.lower()
        keywords = self._extract_keywords(prompt_lower)

        scored_actions = []
        for action in self.action_library:
            score = 0

            # Score based on element text
            element_text = action.get('element', {}).get('text', '').lower()
            for keyword in keywords:
                if keyword in element_text:
                    score += 2

            # Score based on page URL
            page_url = action.get('page_url', '').lower()
            for keyword in keywords:
                if keyword in page_url:
                    score += 1

            # Score based on action type
            action_type = action.get('type', '').lower()
            if 'form' in prompt_lower and 'form' in action_type:
                score += 3
            if 'click' in prompt_lower and action_type == 'click':
                score += 2

            if score > 0:
                scored_actions.append((score, action))

        # Sort by score and return top K
        scored_actions.sort(key=lambda x: x[0], reverse=True)
        return [action for _, action in scored_actions[:top_k]]

    def _find_relevant_pages(self, prompt: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find pages relevant to the user prompt"""
        if not self.state_machine:
            return []

        prompt_lower = prompt.lower()
        keywords = self._extract_keywords(prompt_lower)

        scored_pages = []
        for state in self.state_machine.get('states', []):
            score = 0
            url = state.get('url', '').lower()

            for keyword in keywords:
                if keyword in url:
                    score += 2

            if score > 0:
                scored_pages.append((score, state))

        scored_pages.sort(key=lambda x: x[0], reverse=True)
        return [page for _, page in scored_pages[:top_k]]

    def _find_relevant_flows(self, prompt: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Find user flows relevant to the prompt"""
        if not self.user_flows:
            return []

        prompt_lower = prompt.lower()
        keywords = self._extract_keywords(prompt_lower)

        scored_flows = []
        for flow in self.user_flows:
            score = 0

            # Score based on flow steps
            for step in flow.get('steps', []):
                element = step.get('element', '').lower()
                for keyword in keywords:
                    if keyword in element:
                        score += 1

            if score > 0:
                scored_flows.append((score, flow))

        scored_flows.sort(key=lambda x: x[0], reverse=True)
        return [flow for _, flow in scored_flows[:top_k]]

    def _get_relevant_api_endpoints(self, prompt: str) -> List[Dict[str, Any]]:
        """Get API endpoints relevant to the prompt"""
        if not self.api_map:
            return []

        prompt_lower = prompt.lower()
        keywords = self._extract_keywords(prompt_lower)

        relevant_endpoints = []
        for endpoint in self.api_map.get('endpoints', []):
            endpoint_url = endpoint.get('endpoint', '').lower()

            for keyword in keywords:
                if keyword in endpoint_url:
                    relevant_endpoints.append(endpoint)
                    break

        return relevant_endpoints[:5]

    def _get_validation_rules(self) -> List[Dict[str, Any]]:
        """Get all validation rules"""
        if not self.agent_data:
            return []

        return self.agent_data.get('validation_rules', [])

    def _get_auth_info(self) -> Dict[str, Any]:
        """Get authentication information"""
        if not self.agent_data:
            return {}

        return self.agent_data.get('auth_flows', {})

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'i', 'me', 'my', 'we', 'us', 'you', 'your', 'he', 'she', 'it', 'they',
            'what', 'which', 'who', 'when', 'where', 'why', 'how', 'can', 'should',
            'would', 'could', 'will', 'shall', 'may', 'might', 'must', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'please', 'help', 'want', 'need'
        }

        words = text.lower().split()
        keywords = [w.strip('.,!?;:') for w in words if w not in stop_words and len(w) > 2]

        return keywords

    def get_full_context_summary(self) -> str:
        """Get a text summary of the entire application context"""
        summary_parts = []

        summary_parts.append("=== APPLICATION OVERVIEW ===")
        if self.agent_data:
            summary_parts.append(f"Total pages explored: {len(self.state_machine.get('states', [])) if self.state_machine else 0}")
            summary_parts.append(f"Total actions available: {len(self.action_library) if self.action_library else 0}")

            if self.agent_data.get('auth_flows', {}).get('has_login'):
                summary_parts.append(f"Login URL: {self.agent_data['auth_flows'].get('login_url')}")

        summary_parts.append("\n=== AVAILABLE ACTIONS ===")
        if self.action_library:
            for i, action in enumerate(self.action_library[:10]):  # Show first 10
                element_text = action.get('element', {}).get('text', 'N/A')
                action_type = action.get('type', 'unknown')
                page_url = action.get('page_url', 'N/A')
                summary_parts.append(f"{i+1}. {action_type}: '{element_text}' on {page_url}")

        summary_parts.append("\n=== API ENDPOINTS ===")
        if self.api_map:
            for endpoint in self.api_map.get('endpoints', [])[:10]:  # Show first 10
                method = endpoint.get('method', 'GET')
                url = endpoint.get('endpoint', 'N/A')
                summary_parts.append(f"{method} {url}")

        return "\n".join(summary_parts)

    def format_context_for_llm(self, context: Dict[str, Any]) -> str:
        """Format context as a string prompt for the LLM"""
        parts = []

        parts.append("You are an AI agent that helps automate tasks in a web application.")
        parts.append("Below is the context about the application and the user's request.")
        parts.append("")

        parts.append("=== USER REQUEST ===")
        parts.append(context['prompt'])
        parts.append("")

        parts.append("=== APPLICATION OVERVIEW ===")
        overview = context['app_overview']
        parts.append(f"Total pages: {overview.get('total_pages', 0)}")
        parts.append(f"Total actions: {overview.get('total_actions', 0)}")
        parts.append(f"Has authentication: {overview.get('has_auth', False)}")
        if overview.get('has_auth'):
            parts.append(f"Login URL: {overview.get('login_url', 'N/A')}")
        parts.append(f"Key features: {', '.join(overview.get('key_features', []))}")
        parts.append("")

        parts.append("=== RELEVANT ACTIONS ===")
        for i, action in enumerate(context['relevant_actions']):
            element_text = action.get('element', {}).get('text', 'N/A')
            action_type = action.get('type', 'unknown')
            page_url = action.get('page_url', 'N/A')
            selector = action.get('element', {}).get('selector', 'N/A')
            parts.append(f"{i+1}. Type: {action_type}")
            parts.append(f"   Element: '{element_text}'")
            parts.append(f"   Selector: {selector}")
            parts.append(f"   Page: {page_url}")
            parts.append("")

        parts.append("=== RELEVANT USER FLOWS ===")
        for i, flow in enumerate(context['relevant_flows']):
            parts.append(f"Flow {i+1}:")
            parts.append(f"  Start: {flow.get('start_url', 'N/A')}")
            parts.append(f"  End: {flow.get('end_url', 'N/A')}")
            parts.append(f"  Steps:")
            for j, step in enumerate(flow.get('steps', [])):
                parts.append(f"    {j+1}. {step.get('action', 'N/A')}: {step.get('element', 'N/A')}")
            parts.append("")

        parts.append("=== RELEVANT API ENDPOINTS ===")
        for endpoint in context['api_endpoints']:
            method = endpoint.get('method', 'GET')
            url = endpoint.get('endpoint', 'N/A')
            parts.append(f"{method} {url}")
        parts.append("")

        if context.get('validation_rules'):
            parts.append("=== VALIDATION RULES ===")
            for rule in context['validation_rules'][:5]:  # Show first 5
                field = rule.get('field', 'N/A')
                parts.append(f"Field '{field}':")
                if rule.get('required'):
                    parts.append("  - Required")
                if rule.get('pattern'):
                    parts.append(f"  - Pattern: {rule['pattern']}")
                if rule.get('min'):
                    parts.append(f"  - Min: {rule['min']}")
                if rule.get('max'):
                    parts.append(f"  - Max: {rule['max']}")
            parts.append("")

        return "\n".join(parts)
