"""
Agent Preparation - Prepares data for LLM agent creation
"""
import json
from typing import Dict, Any, List, Set
from collections import defaultdict


class AgentPreparation:
    def __init__(self, config):
        self.config = config
        self.action_library = []
        self.api_map = {}
        self.component_hierarchy = {}
        self.business_rules = []
        self.validation_rules = []
        self.user_flows = []
        self.state_machine = {}
        
    def prepare_agent_data(self, all_pages: List[Dict[str, Any]], interactions: List[Dict[str, Any]], network_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare comprehensive agent data"""
        agent_data = {}
        
        if self.config.BUILD_ACTION_LIBRARY:
            agent_data['action_library'] = self._build_action_library(all_pages, interactions)
        
        if self.config.MAP_API_ENDPOINTS:
            agent_data['api_map'] = self._map_api_endpoints(network_data)
        
        if self.config.MAP_COMPONENT_HIERARCHY:
            agent_data['component_hierarchy'] = self._map_component_hierarchy(all_pages)
        
        if self.config.BUILD_INTERACTION_GRAPH:
            agent_data['interaction_graph'] = self._build_interaction_graph(interactions)
        
        if self.config.EXTRACT_BUSINESS_LOGIC:
            agent_data['business_logic'] = self._extract_business_logic(all_pages, interactions)
        
        if self.config.DETECT_AUTH_FLOWS:
            agent_data['auth_flows'] = self._detect_auth_flows(all_pages, network_data)
        
        if self.config.DETECT_CRUD_OPERATIONS:
            agent_data['crud_operations'] = self._detect_crud_operations(interactions, network_data)
        
        if self.config.DETECT_VALIDATION_RULES:
            agent_data['validation_rules'] = self._detect_validation_rules(all_pages)
        
        if self.config.DETECT_ERROR_PATTERNS:
            agent_data['error_patterns'] = self._detect_error_patterns(all_pages, interactions)
        
        if self.config.TRACK_USER_FLOWS:
            agent_data['user_flows'] = self._build_user_flows(interactions)
        
        if self.config.TRACK_STATE_TRANSITIONS:
            agent_data['state_machine'] = self._build_state_machine(interactions)
        
        return agent_data
    
    def _build_action_library(self, all_pages: List[Dict[str, Any]], interactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build library of all possible actions"""
        actions = []
        action_id = 0
        
        # Extract actions from interactions
        for interaction in interactions:
            element = interaction.get('element', {})
            
            action = {
                'id': action_id,
                'type': interaction.get('interaction_type', 'unknown'),
                'element': {
                    'tag': element.get('tag'),
                    'text': element.get('text', '')[:100],
                    'selector': element.get('selector'),
                    'class': element.get('class'),
                },
                'page_url': interaction.get('parent_url'),
                'result': {
                    'navigated': interaction.get('navigated', False),
                    'url_after': interaction.get('url_after'),
                    'changes': interaction.get('changes_detected', {}),
                },
                'preconditions': self._extract_preconditions(interaction),
                'postconditions': self._extract_postconditions(interaction),
            }
            
            actions.append(action)
            action_id += 1
        
        # Extract form actions
        for page in all_pages:
            forms = page.get('structure', {}).get('forms', [])
            for i, form in enumerate(forms):
                action = {
                    'id': action_id,
                    'type': 'form_submission',
                    'form': {
                        'action': form.get('action'),
                        'method': form.get('method'),
                        'fields': form.get('inputs', []),
                    },
                    'page_url': page.get('url'),
                    'requirements': self._extract_form_requirements(form),
                }
                
                actions.append(action)
                action_id += 1
        
        return actions
    
    def _map_api_endpoints(self, network_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Map all API endpoints"""
        api_map = {
            'endpoints': [],
            'by_method': defaultdict(list),
            'patterns': {},
        }
        
        seen_endpoints = set()
        
        for request in network_data:
            url = request.get('url', '')
            
            # Identify API calls
            if '/api/' in url or url.endswith('.json'):
                method = request.get('method', 'GET')
                
                # Extract endpoint pattern
                endpoint = self._extract_endpoint_pattern(url)
                
                if endpoint not in seen_endpoints:
                    seen_endpoints.add(endpoint)
                    
                    endpoint_info = {
                        'endpoint': endpoint,
                        'method': method,
                        'full_url': url,
                        'headers': request.get('headers', {}),
                        'body': request.get('post_data'),
                        'resource_type': request.get('resource_type'),
                    }
                    
                    api_map['endpoints'].append(endpoint_info)
                    api_map['by_method'][method].append(endpoint)
        
        # Identify patterns
        api_map['patterns'] = self._identify_api_patterns(api_map['endpoints'])
        
        return api_map
    
    def _map_component_hierarchy(self, all_pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Map component hierarchy"""
        hierarchy = {
            'pages': [],
            'reusable_components': [],
            'layout_patterns': [],
        }
        
        # Identify common components across pages
        common_elements = self._find_common_elements(all_pages)
        
        for page in all_pages:
            page_info = {
                'url': page.get('url'),
                'components': self._identify_page_components(page),
                'layout': self._identify_layout_pattern(page),
            }
            hierarchy['pages'].append(page_info)
        
        hierarchy['reusable_components'] = common_elements
        
        return hierarchy
    
    def _build_interaction_graph(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build visual interaction graph"""
        graph = {
            'nodes': [],
            'edges': [],
        }
        
        # Create nodes (unique URLs)
        urls = set()
        for interaction in interactions:
            urls.add(interaction.get('url_before'))
            urls.add(interaction.get('url_after'))
        
        for i, url in enumerate(urls):
            graph['nodes'].append({
                'id': i,
                'url': url,
                'label': url.split('/')[-1] or 'home',
            })
        
        # Create edges (interactions)
        url_to_id = {url: i for i, url in enumerate(urls)}
        
        for interaction in interactions:
            url_before = interaction.get('url_before')
            url_after = interaction.get('url_after')
            
            if url_before != url_after:  # Only if navigation occurred
                graph['edges'].append({
                    'from': url_to_id.get(url_before),
                    'to': url_to_id.get(url_after),
                    'label': interaction.get('element', {}).get('text', '')[:30],
                    'type': interaction.get('interaction_type'),
                })
        
        return graph
    
    def _extract_business_logic(self, all_pages: List[Dict[str, Any]], interactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract business logic rules"""
        rules = []
        
        # Extract from validation patterns
        for page in all_pages:
            forms = page.get('structure', {}).get('forms', [])
            for form in forms:
                for input_field in form.get('inputs', []):
                    field_name = input_field.get('name') or input_field.get('id') or 'unknown_field'
                    
                    if input_field.get('required'):
                        rules.append({
                            'type': 'required_field',
                            'field': field_name,
                            'form': form.get('action') or 'unknown_form',
                        })
                    
                    if input_field.get('pattern'):
                        rules.append({
                            'type': 'validation_pattern',
                            'field': field_name,
                            'pattern': input_field.get('pattern'),
                        })
                    
                    if input_field.get('min') or input_field.get('max'):
                        rules.append({
                            'type': 'range_constraint',
                            'field': field_name,
                            'min': input_field.get('min'),
                            'max': input_field.get('max'),
                        })
        
        return rules
    
    def _detect_auth_flows(self, all_pages: List[Dict[str, Any]], network_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect authentication flows"""
        auth_info = {
            'has_login': False,
            'login_url': None,
            'login_method': None,
            'auth_endpoints': [],
            'protected_routes': [],
        }
        
        # Look for login forms
        for page in all_pages:
            forms = page.get('structure', {}).get('forms', [])
            for form in forms:
                inputs = form.get('inputs', [])
                has_password = any(inp.get('type') == 'password' for inp in inputs)
                has_email_or_username = any(
                    'email' in (inp.get('name') or '').lower() or 
                    'username' in (inp.get('name') or '').lower() 
                    for inp in inputs
                )
                
                if has_password and has_email_or_username:
                    auth_info['has_login'] = True
                    auth_info['login_url'] = page.get('url')
                    auth_info['login_method'] = form.get('method')
                    auth_info['login_action'] = form.get('action')
        
        # Look for auth-related API calls
        for request in network_data:
            url = request.get('url', '').lower()
            if any(keyword in url for keyword in ['auth', 'login', 'token', 'session']):
                auth_info['auth_endpoints'].append({
                    'url': request.get('url'),
                    'method': request.get('method'),
                })
        
        return auth_info
    
    def _detect_crud_operations(self, interactions: List[Dict[str, Any]], network_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Detect CRUD operations"""
        crud = {
            'create': [],
            'read': [],
            'update': [],
            'delete': [],
        }
        
        for request in network_data:
            method = request.get('method', '')
            url = request.get('url', '')
            
            if method == 'POST':
                crud['create'].append({'url': url, 'type': 'api_create'})
            elif method == 'GET':
                crud['read'].append({'url': url, 'type': 'api_read'})
            elif method in ['PUT', 'PATCH']:
                crud['update'].append({'url': url, 'type': 'api_update'})
            elif method == 'DELETE':
                crud['delete'].append({'url': url, 'type': 'api_delete'})
        
        return crud
    
    def _detect_validation_rules(self, all_pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect validation rules"""
        rules = []
        
        for page in all_pages:
            forms = page.get('structure', {}).get('forms', [])
            for form in forms:
                for input_field in form.get('inputs', []):
                    validation = {}
                    
                    field_name = input_field.get('name') or input_field.get('id') or 'unknown_field'
                    
                    if input_field.get('required'):
                        validation['required'] = True
                    
                    if input_field.get('pattern'):
                        validation['pattern'] = input_field.get('pattern')
                    
                    if input_field.get('min'):
                        validation['min'] = input_field.get('min')
                    
                    if input_field.get('max'):
                        validation['max'] = input_field.get('max')
                    
                    if input_field.get('type') == 'email':
                        validation['email_format'] = True
                    
                    if validation:
                        validation['field'] = field_name
                        validation['type'] = input_field.get('type', 'text')
                        rules.append(validation)
        
        return rules
    
    def _detect_error_patterns(self, all_pages: List[Dict[str, Any]], interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect error patterns"""
        errors = {
            'console_errors': [],
            'error_pages': [],
            'validation_errors': [],
        }
        
        # Console errors
        for page in all_pages:
            console = page.get('console', {})
            if console.get('errors'):
                errors['console_errors'].extend(console['errors'])
        
        # Check for error indicators in interactions
        for interaction in interactions:
            changes = interaction.get('changes_detected', {})
            if changes.get('alert_appeared'):
                errors['validation_errors'].append({
                    'interaction': interaction.get('element', {}).get('text'),
                    'page': interaction.get('parent_url'),
                })
        
        return errors
    
    def _build_user_flows(self, interactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build common user flows"""
        flows = []
        
        # Group interactions by sequence
        current_flow = []
        last_url = None
        
        for interaction in interactions:
            url_before = interaction.get('url_before')
            
            if last_url and url_before != last_url:
                # New flow started
                if current_flow:
                    flows.append({
                        'steps': current_flow,
                        'start_url': current_flow[0]['url'],
                        'end_url': current_flow[-1]['url_after'],
                    })
                current_flow = []
            
            current_flow.append({
                'action': interaction.get('interaction_type'),
                'element': interaction.get('element', {}).get('text', '')[:50],
                'url': url_before,
                'url_after': interaction.get('url_after'),
            })
            
            last_url = interaction.get('url_after')
        
        if current_flow:
            flows.append({
                'steps': current_flow,
                'start_url': current_flow[0]['url'],
                'end_url': current_flow[-1]['url_after'],
            })
        
        return flows
    
    def _build_state_machine(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build state machine from interactions"""
        states = {}
        transitions = []
        
        for interaction in interactions:
            url_before = interaction.get('url_before')
            url_after = interaction.get('url_after')
            
            # Add states
            if url_before not in states:
                states[url_before] = {
                    'url': url_before,
                    'outgoing_transitions': [],
                }
            
            if url_after not in states:
                states[url_after] = {
                    'url': url_after,
                    'outgoing_transitions': [],
                }
            
            # Add transition
            transition = {
                'from': url_before,
                'to': url_after,
                'trigger': interaction.get('element', {}).get('text', '')[:50],
                'type': interaction.get('interaction_type'),
            }
            
            transitions.append(transition)
            states[url_before]['outgoing_transitions'].append(transition)
        
        return {
            'states': list(states.values()),
            'transitions': transitions,
            'initial_state': list(states.keys())[0] if states else None,
        }
    
    # Helper methods
    def _extract_preconditions(self, interaction: Dict[str, Any]) -> List[str]:
        """Extract preconditions for an action"""
        preconditions = []
        preconditions.append(f"User is on page: {interaction.get('url_before')}")
        
        element = interaction.get('element', {})
        if element.get('selector'):
            preconditions.append(f"Element {element['selector']} is visible")
        
        return preconditions
    
    def _extract_postconditions(self, interaction: Dict[str, Any]) -> List[str]:
        """Extract postconditions for an action"""
        postconditions = []
        
        if interaction.get('navigated'):
            postconditions.append(f"User navigated to: {interaction.get('url_after')}")
        
        changes = interaction.get('changes_detected', {})
        if changes.get('modal_appeared'):
            postconditions.append("Modal appeared")
        if changes.get('alert_appeared'):
            postconditions.append("Alert appeared")
        
        return postconditions
    
    def _extract_form_requirements(self, form: Dict[str, Any]) -> List[str]:
        """Extract form requirements"""
        requirements = []
        
        for input_field in form.get('inputs', []):
            if input_field.get('required'):
                field_name = input_field.get('name') or input_field.get('id') or 'unknown'
                requirements.append(f"Field '{field_name}' is required")
        
        return requirements
    
    def _extract_endpoint_pattern(self, url: str) -> str:
        """Extract endpoint pattern from URL"""
        # Remove query parameters
        url = url.split('?')[0]
        
        # Replace IDs with placeholders
        import re
        url = re.sub(r'/\d+', '/:id', url)
        url = re.sub(r'/[a-f0-9-]{36}', '/:uuid', url)  # UUIDs
        
        return url
    
    def _identify_api_patterns(self, endpoints: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Identify API patterns"""
        patterns = defaultdict(list)
        
        for endpoint in endpoints:
            url = endpoint['endpoint']
            
            if 'user' in url.lower():
                patterns['user_management'].append(url)
            if 'auth' in url.lower() or 'login' in url.lower():
                patterns['authentication'].append(url)
            if 'product' in url.lower() or 'item' in url.lower():
                patterns['products'].append(url)
            if 'order' in url.lower() or 'cart' in url.lower():
                patterns['orders'].append(url)
        
        return dict(patterns)
    
    def _find_common_elements(self, all_pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find common elements across pages"""
        # Simple implementation - find elements that appear on most pages
        common = []
        
        # Check for common navigation
        nav_items = defaultdict(int)
        for page in all_pages:
            nav = page.get('structure', {}).get('navigation', [])
            for item in nav:
                nav_items[item.get('text')] += 1
        
        # Elements that appear on >50% of pages are "common"
        threshold = len(all_pages) * 0.5
        for text, count in nav_items.items():
            if count >= threshold:
                common.append({
                    'type': 'navigation_item',
                    'text': text,
                    'appears_on': count,
                    'total_pages': len(all_pages),
                })
        
        return common
    
    def _identify_page_components(self, page: Dict[str, Any]) -> List[str]:
        """Identify components on a page"""
        components = []
        
        structure = page.get('structure', {})
        
        if structure.get('header'):
            components.append('header')
        if structure.get('navigation'):
            components.append('navigation')
        if structure.get('footer'):
            components.append('footer')
        if structure.get('sidebar'):
            components.append('sidebar')
        if structure.get('forms'):
            components.append('forms')
        
        return components
    
    def _identify_layout_pattern(self, page: Dict[str, Any]) -> str:
        """Identify layout pattern"""
        structure = page.get('structure', {})
        
        has_sidebar = bool(structure.get('sidebar'))
        has_header = bool(structure.get('header'))
        has_footer = bool(structure.get('footer'))
        
        if has_header and has_footer and has_sidebar:
            return 'header-sidebar-footer'
        elif has_header and has_footer:
            return 'header-footer'
        elif has_header:
            return 'header-only'
        else:
            return 'simple'