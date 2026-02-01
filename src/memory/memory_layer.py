"""
Memory Layer - Learns from Playwright exploration and stores product context
"""
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class MemoryLayer:
    """
    Learns product context from Playwright exploration data
    Stores it persistently for LLM consumption
    """
    
    def __init__(self, product_name: str, exploration_dir: str = "output"):
        self.product_name = product_name
        self.exploration_dir = Path(exploration_dir)
        self.memory_dir = Path("memory")
        self.memory_dir.mkdir(exist_ok=True)
        
        self.memory_file = self.memory_dir / f"{product_name}.json"
        self.memory = self._load_or_create()
    
    def _load_or_create(self) -> Dict[str, Any]:
        """Load existing memory or create new"""
        if self.memory_file.exists():
            with open(self.memory_file) as f:
                return json.load(f)
        
        return {
            "product_name": self.product_name,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            
            # Product context (user-provided)
            "product_context": {
                "description": "",
                "type": "",
                "domain": "",
                "terminology": {},
                "workflows": {},
                "business_rules": {},
            },
            
            # Learned from Playwright exploration
            "learned_from_exploration": {
                "pages": {},
                "forms": {},
                "buttons": {},
                "navigation_flows": [],
                "api_endpoints": {},
                "user_journeys": [],
                "common_patterns": {},
            },
            
            # Combined context for LLM
            "llm_context": ""
        }
    
    def save(self):
        """Save memory to disk"""
        self.memory["last_updated"] = datetime.now().isoformat()
        self._rebuild_llm_context()
        
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
        
        print(f"💾 Memory saved: {self.memory_file}")
    
    def learn_from_exploration(self):
        """
        Automatically learn from Playwright exploration data
        Uses: agent_data.json, action_library.json, forms, etc.
        """
        print(f"🧠 Learning from exploration data in {self.exploration_dir}...")
        
        # 1. Learn from pages
        self._learn_pages()
        
        # 2. Learn from forms
        self._learn_forms()
        
        # 3. Learn from interactions (buttons, links)
        self._learn_interactions()
        
        # 4. Learn from API endpoints
        self._learn_apis()
        
        # 5. Learn from user flows
        self._learn_user_flows()
        
        # 6. Learn common patterns
        self._learn_patterns()
        
        self.save()
        print("✅ Learning complete!")
    
    def _learn_pages(self):
        """Learn about pages from exploration"""
        pages_dir = self.exploration_dir / "pages"
        if not pages_dir.exists():
            return
        
        print("   📄 Learning pages...")
        
        pages = {}
        for page_file in pages_dir.glob("*.json"):
            with open(page_file) as f:
                page_data = json.load(f)
            
            url = page_data.get('url', '')
            pages[url] = {
                "title": page_data.get('structure', {}).get('metadata', {}).get('title', ''),
                "has_forms": len(page_data.get('structure', {}).get('forms', [])) > 0,
                "has_navigation": len(page_data.get('structure', {}).get('navigation', [])) > 0,
                "interactive_elements": page_data.get('interactive_elements_count', 0),
            }
        
        self.memory["learned_from_exploration"]["pages"] = pages
        print(f"      ✓ Learned {len(pages)} pages")
    
    def _learn_forms(self):
        """Learn about forms from exploration"""
        forms_file = self.exploration_dir / "form_filling_summary.json"
        if not forms_file.exists():
            return
        
        print("   📝 Learning forms...")
        
        with open(forms_file) as f:
            form_data = json.load(f)
        
        forms = {}
        for form in form_data.get('forms', []):
            action = form.get('form_action', 'unknown')
            forms[action] = {
                "method": form.get('form_method', 'GET'),
                "fields": [
                    {
                        "name": field.get('name'),
                        "type": field.get('field_type'),
                        "example_value": field.get('value', '')[:50] if field.get('value') else ''
                    }
                    for field in form.get('filled_fields', [])
                ],
                "submission_result": form.get('submission_result', {})
            }
        
        self.memory["learned_from_exploration"]["forms"] = forms
        print(f"      ✓ Learned {len(forms)} forms")
    
    def _learn_interactions(self):
        """Learn about buttons and interactive elements"""
        action_file = self.exploration_dir / "action_library.json"
        if not action_file.exists():
            return
        
        print("   🖱️  Learning interactions...")
        
        with open(action_file) as f:
            actions = json.load(f)
        
        buttons = {}
        for action in actions:
            if action.get('type') in ['button_click', 'button']:
                element = action.get('element', {})
                text = element.get('text', '')[:50]
                
                if text:
                    buttons[text] = {
                        "page": action.get('page_url'),
                        "result": action.get('result', {}),
                    }
        
        self.memory["learned_from_exploration"]["buttons"] = buttons
        print(f"      ✓ Learned {len(buttons)} buttons")
    
    def _learn_apis(self):
        """Learn about API endpoints"""
        api_file = self.exploration_dir / "api_map.json"
        if not api_file.exists():
            return
        
        print("   🌐 Learning API endpoints...")
        
        with open(api_file) as f:
            api_data = json.load(f)
        
        apis = {}
        for endpoint_data in api_data.get('endpoints', []):
            endpoint = endpoint_data.get('endpoint', '')
            method = endpoint_data.get('method', 'GET')
            
            key = f"{method} {endpoint}"
            apis[key] = {
                "method": method,
                "endpoint": endpoint,
                "resource_type": endpoint_data.get('resource_type'),
            }
        
        self.memory["learned_from_exploration"]["api_endpoints"] = apis
        print(f"      ✓ Learned {len(apis)} API endpoints")
    
    def _learn_user_flows(self):
        """Learn user flows/journeys"""
        flows_file = self.exploration_dir / "user_flows.json"
        if not flows_file.exists():
            return
        
        print("   🚶 Learning user flows...")
        
        with open(flows_file) as f:
            flows_data = json.load(f)
        
        flows = []
        for flow in flows_data:
            flows.append({
                "from": flow.get('start_url'),
                "to": flow.get('end_url'),
                "steps": [
                    {
                        "action": step.get('action'),
                        "element": step.get('element', '')[:50]
                    }
                    for step in flow.get('steps', [])
                ]
            })
        
        self.memory["learned_from_exploration"]["navigation_flows"] = flows
        print(f"      ✓ Learned {len(flows)} user flows")
    
    def _learn_patterns(self):
        """Learn common patterns"""
        graph_file = self.exploration_dir / "interaction_graph.json"
        if not graph_file.exists():
            return
        
        print("   🔄 Learning patterns...")
        
        with open(graph_file) as f:
            interactions = json.load(f)
        
        # Count interaction types
        patterns = {}
        for interaction in interactions:
            itype = interaction.get('element_type', 'unknown')
            patterns[itype] = patterns.get(itype, 0) + 1
        
        self.memory["learned_from_exploration"]["common_patterns"] = patterns
        print(f"      ✓ Learned {len(patterns)} interaction patterns")
    
    def add_product_context(self, 
                           description: str = None,
                           product_type: str = None,
                           domain: str = None):
        """Add basic product context"""
        if description:
            self.memory["product_context"]["description"] = description
        if product_type:
            self.memory["product_context"]["type"] = product_type
        if domain:
            self.memory["product_context"]["domain"] = domain
        
        self.save()
    
    def add_terminology(self, term: str, definition: str):
        """Add product-specific terminology"""
        self.memory["product_context"]["terminology"][term] = definition
        self.save()
    
    def add_workflow(self, name: str, steps: List[str]):
        """Add product workflow"""
        self.memory["product_context"]["workflows"][name] = steps
        self.save()
    
    def add_business_rule(self, name: str, description: str):
        """Add business rule"""
        self.memory["product_context"]["business_rules"][name] = description
        self.save()
    
    def _rebuild_llm_context(self):
        """Build complete context string for LLM"""
        parts = []
        
        parts.append(f"# PRODUCT MEMORY: {self.product_name.upper()}\n\n")
        
        # Product context (user-provided)
        ctx = self.memory["product_context"]
        if ctx.get("description"):
            parts.append(f"## Description\n{ctx['description']}\n\n")
        
        if ctx.get("type"):
            parts.append(f"**Type:** {ctx['type']}\n")
        if ctx.get("domain"):
            parts.append(f"**Domain:** {ctx['domain']}\n\n")
        
        if ctx.get("terminology"):
            parts.append("## Terminology\n")
            for term, definition in ctx["terminology"].items():
                parts.append(f"- **{term}**: {definition}\n")
            parts.append("\n")
        
        if ctx.get("workflows"):
            parts.append("## Workflows\n")
            for name, steps in ctx["workflows"].items():
                parts.append(f"\n### {name}\n")
                for i, step in enumerate(steps, 1):
                    parts.append(f"{i}. {step}\n")
            parts.append("\n")
        
        if ctx.get("business_rules"):
            parts.append("## Business Rules\n")
            for name, desc in ctx["business_rules"].items():
                parts.append(f"- **{name}**: {desc}\n")
            parts.append("\n")
        
        # Learned from exploration
        learned = self.memory["learned_from_exploration"]
        
        if learned.get("pages"):
            parts.append(f"## Pages ({len(learned['pages'])} discovered)\n")
            for url, info in list(learned["pages"].items())[:10]:
                parts.append(f"- {url}: {info.get('title', 'No title')}\n")
            parts.append("\n")
        
        if learned.get("forms"):
            parts.append(f"## Forms ({len(learned['forms'])} discovered)\n")
            for action, form in learned["forms"].items():
                parts.append(f"\n### {action}\n")
                parts.append(f"Method: {form['method']}\n")
                parts.append("Fields:\n")
                for field in form.get('fields', [])[:5]:
                    parts.append(f"  - {field['name']} ({field['type']})\n")
            parts.append("\n")
        
        if learned.get("buttons"):
            parts.append(f"## Interactive Elements ({len(learned['buttons'])} buttons)\n")
            for text, info in list(learned["buttons"].items())[:10]:
                parts.append(f"- '{text}' on {info.get('page', 'unknown')}\n")
            parts.append("\n")
        
        if learned.get("api_endpoints"):
            parts.append(f"## API Endpoints ({len(learned['api_endpoints'])} discovered)\n")
            for endpoint in list(learned["api_endpoints"].values())[:10]:
                parts.append(f"- {endpoint['method']} {endpoint['endpoint']}\n")
            parts.append("\n")
        
        if learned.get("navigation_flows"):
            parts.append(f"## User Flows ({len(learned['navigation_flows'])} discovered)\n")
            for flow in learned["navigation_flows"][:5]:
                parts.append(f"\n{flow['from']} → {flow['to']}\n")
                for step in flow.get('steps', [])[:3]:
                    parts.append(f"  - {step['action']}: {step['element']}\n")
            parts.append("\n")
        
        self.memory["llm_context"] = ''.join(parts)
    
    def get_context_for_llm(self) -> str:
        """Get complete context formatted for LLM"""
        return self.memory.get("llm_context", "")
    
    def export_context(self, output_file: str = None):
        """Export LLM context to file"""
        if not output_file:
            output_file = self.memory_dir / f"{self.product_name}_context.txt"
        
        with open(output_file, 'w') as f:
            f.write(self.get_context_for_llm())
        
        print(f"📄 Context exported to: {output_file}")
        return output_file
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of what's in memory"""
        learned = self.memory["learned_from_exploration"]
        ctx = self.memory["product_context"]
        
        return {
            "product_name": self.product_name,
            "last_updated": self.memory.get("last_updated"),
            "user_provided": {
                "description": bool(ctx.get("description")),
                "terminology": len(ctx.get("terminology", {})),
                "workflows": len(ctx.get("workflows", {})),
                "business_rules": len(ctx.get("business_rules", {})),
            },
            "learned_from_exploration": {
                "pages": len(learned.get("pages", {})),
                "forms": len(learned.get("forms", {})),
                "buttons": len(learned.get("buttons", {})),
                "api_endpoints": len(learned.get("api_endpoints", {})),
                "navigation_flows": len(learned.get("navigation_flows", [])),
                "patterns": len(learned.get("common_patterns", {})),
            }
        }


# Simple CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python memory_layer.py <product_name> [command]")
        print("\nCommands:")
        print("  learn     - Learn from exploration data")
        print("  export    - Export context for LLM")
        print("  summary   - Show summary")
        sys.exit(1)
    
    product_name = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else "learn"
    
    memory = MemoryLayer(product_name)
    
    if command == "learn":
        memory.learn_from_exploration()
    elif command == "export":
        memory.export_context()
    elif command == "summary":
        summary = memory.get_summary()
        print(json.dumps(summary, indent=2))