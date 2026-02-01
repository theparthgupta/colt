"""
Interaction Explorer - Explores ALL interactive elements (buttons, links, etc.)
"""
import asyncio
import hashlib
from typing import Dict, Any, List, Set, Optional
from datetime import datetime


class InteractionExplorer:
    def __init__(self, config):
        self.config = config
        self.explored_interactions = []
        self.interaction_states = set()  # Track unique states
        self.interaction_graph = []  # Graph of all interactions
        self.current_depth = 0
        
    async def explore_all_interactions(self, page, page_url: str, depth: int = 0) -> List[Dict[str, Any]]:
        """Explore ALL interactive elements on the current page"""
        if depth >= self.config.MAX_DEPTH:
            return []
        
        results = []
        
        # Get ALL interactive elements
        interactive_elements = await self._find_all_interactive_elements(page)
        
        print(f"   Found {len(interactive_elements)} interactive elements to explore")
        
        # Limit interactions per page
        elements_to_explore = interactive_elements[:self.config.MAX_INTERACTIONS_PER_PAGE]
        
        for i, element in enumerate(elements_to_explore):
            try:
                print(f"    [{i+1}/{len(elements_to_explore)}] Exploring: {element['type']} - {element['text'][:50]}")
                
                # Explore this interaction
                result = await self._explore_interaction(page, element, page_url, depth)
                if result:
                    results.append(result)
                    self.explored_interactions.append(result)
                
                # Wait between interactions
                await asyncio.sleep(self.config.INTERACTION_WAIT_TIME / 1000)
                
            except Exception as e:
                print(f"      Error exploring element: {e}")
        
        return results
    
    async def _find_all_interactive_elements(self, page) -> List[Dict[str, Any]]:
        """Find ALL interactive elements on the page"""
        try:
            elements = await page.evaluate("""
                () => {
                    const elements = [];
                    let elementId = 0;
                    
                    // Buttons
                    document.querySelectorAll('button:not([disabled])').forEach(btn => {
                        const rect = btn.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            elements.push({
                                id: elementId++,
                                type: 'button',
                                tag: 'BUTTON',
                                text: btn.innerText?.substring(0, 100) || btn.value || '',
                                selector: btn.id ? `#${btn.id}` : null,
                                class: btn.className || null,
                                x: rect.x,
                                y: rect.y,
                                ariaLabel: btn.getAttribute('aria-label'),
                                dataAttributes: Object.keys(btn.dataset).length > 0 ? btn.dataset : null,
                            });
                        }
                    });
                    
                    // Links (not for navigation, for interaction)
                    document.querySelectorAll('a[href]:not([href^="http"]):not([href^="//"]):not([href^="mailto"]):not([href^="tel"])').forEach(link => {
                        const rect = link.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            elements.push({
                                id: elementId++,
                                type: 'link',
                                tag: 'A',
                                text: link.innerText?.substring(0, 100) || '',
                                href: link.href,
                                selector: link.id ? `#${link.id}` : null,
                                class: link.className || null,
                                x: rect.x,
                                y: rect.y,
                            });
                        }
                    });
                    
                    // Input buttons
                    document.querySelectorAll('input[type="button"], input[type="submit"]:not([disabled])').forEach(inp => {
                        const rect = inp.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            elements.push({
                                id: elementId++,
                                type: 'input_button',
                                tag: 'INPUT',
                                text: inp.value || '',
                                selector: inp.id ? `#${inp.id}` : null,
                                class: inp.className || null,
                                x: rect.x,
                                y: rect.y,
                            });
                        }
                    });
                    
                    // Elements with onclick
                    document.querySelectorAll('[onclick]').forEach(elem => {
                        const rect = elem.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            elements.push({
                                id: elementId++,
                                type: 'onclick',
                                tag: elem.tagName,
                                text: elem.innerText?.substring(0, 100) || '',
                                selector: elem.id ? `#${elem.id}` : null,
                                class: elem.className || null,
                                x: rect.x,
                                y: rect.y,
                            });
                        }
                    });
                    
                    // Role=button elements
                    document.querySelectorAll('[role="button"]').forEach(elem => {
                        const rect = elem.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            elements.push({
                                id: elementId++,
                                type: 'role_button',
                                tag: elem.tagName,
                                text: elem.innerText?.substring(0, 100) || '',
                                selector: elem.id ? `#${elem.id}` : null,
                                class: elem.className || null,
                                x: rect.x,
                                y: rect.y,
                            });
                        }
                    });
                    
                    return elements;
                }
            """)
            
            return elements
        except Exception as e:
            print(f"Error finding interactive elements: {e}")
            return []
    
    async def _explore_interaction(self, page, element: Dict[str, Any], parent_url: str, depth: int) -> Optional[Dict[str, Any]]:
        """Explore a single interaction"""
        try:
            # Record state before interaction
            state_before = await self._capture_state(page)
            url_before = page.url
            
            print(f"       Capturing state before...")
            
            # Take screenshot before
            screenshot_before = None
            if self.config.CAPTURE_SCREENSHOTS_AFTER_INTERACTIONS:
                screenshot_before = f"{self.config.OUTPUT_DIR}/screenshots/interaction_{element['id']}_before.png"
                await page.screenshot(path=screenshot_before, full_page=True)
            
            # Perform the interaction
            print(f"        Clicking element...")
            interaction_result = await self._perform_interaction(page, element)
            
            # Wait for any changes
            await page.wait_for_timeout(1500)  # Increased wait time
            
            # Record state after interaction
            print(f"       Capturing state after...")
            state_after = await self._capture_state(page)
            url_after = page.url
            
            # Take screenshot after
            screenshot_after = None
            if self.config.CAPTURE_SCREENSHOTS_AFTER_INTERACTIONS:
                screenshot_after = f"{self.config.OUTPUT_DIR}/screenshots/interaction_{element['id']}_after.png"
                await page.screenshot(path=screenshot_after, full_page=True)
            
            # Analyze what changed
            changes = self._detect_changes(state_before, state_after)
            
            # Log changes
            if changes.get('has_changes'):
                print(f"       Changes detected:")
                if changes.get('url_changed'):
                    print(f"         • Navigated: {changes.get('url_to')}")
                if changes.get('modal_appeared'):
                    print(f"         • Modal appeared")
                if changes.get('alert_appeared'):
                    print(f"         • Alert appeared")
                if changes.get('content_changed'):
                    print(f"         • Content changed: {changes.get('content_delta_percent', 0)}%")
                if changes.get('dom_changed'):
                    print(f"         • DOM changed: {changes.get('element_delta', 0)} elements")
            else:
                print(f"        No visible changes detected")
            
            # Build result
            result = {
                'timestamp': datetime.now().isoformat(),
                'parent_url': parent_url,
                'element': element,
                'interaction_type': element['type'],
                'state_before': state_before,
                'state_after': state_after,
                'url_before': url_before,
                'url_after': url_after,
                'navigated': url_before != url_after,
                'changes_detected': changes,
                'screenshot_before': screenshot_before,
                'screenshot_after': screenshot_after,
                'interaction_result': interaction_result,
                'depth': depth,
            }
            
            # Add to interaction graph
            self._add_to_graph(result)
            
            # If we navigated, go back
            if url_before != url_after:
                print(f"        Navigating back to {parent_url}")
                try:
                    await page.go_back(wait_until='networkidle', timeout=5000)
                    await page.wait_for_timeout(1000)
                except:
                    # If can't go back, navigate to parent
                    await page.goto(parent_url, wait_until='networkidle')
                    await page.wait_for_timeout(1000)
            
            return result
            
        except Exception as e:
            print(f"       Error exploring interaction: {e}")
            return None
    
    async def _perform_interaction(self, page, element: Dict[str, Any]) -> Dict[str, Any]:
        """Perform the actual interaction (click, etc.)"""
        try:
            # Try to click by selector first
            if element.get('selector'):
                await page.click(element['selector'])
                return {'method': 'selector', 'selector': element['selector']}
            
            # Try by coordinates
            if element.get('x') and element.get('y'):
                await page.mouse.click(element['x'], element['y'])
                return {'method': 'coordinates', 'x': element['x'], 'y': element['y']}
            
            # Try by text (for buttons)
            if element['type'] == 'button' and element.get('text'):
                button = page.get_by_role('button', name=element['text'][:30])
                await button.click()
                return {'method': 'role_text', 'text': element['text'][:30]}
            
            return {'method': 'none', 'error': 'Could not perform interaction'}
            
        except Exception as e:
            return {'method': 'error', 'error': str(e)}
    
    async def _capture_state(self, page) -> Dict[str, Any]:
        """Capture current page state"""
        try:
            state = await page.evaluate("""
                () => {
                    return {
                        url: window.location.href,
                        title: document.title,
                        body_html_length: document.body.innerHTML.length,
                        visible_text_length: document.body.innerText.length,
                        element_count: document.querySelectorAll('*').length,
                        // Get some key elements
                        has_modal: document.querySelector('[role="dialog"], .modal') !== null,
                        has_alert: document.querySelector('[role="alert"], .alert') !== null,
                        active_element: document.activeElement?.tagName || null,
                    };
                }
            """)
            return state
        except:
            return {}
    
    def _detect_changes(self, before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
        """Detect what changed between states"""
        changes = {}
        
        # URL change
        if before.get('url') != after.get('url'):
            changes['url_changed'] = True
            changes['url_from'] = before.get('url')
            changes['url_to'] = after.get('url')
        
        # Title change
        if before.get('title') != after.get('title'):
            changes['title_changed'] = True
            changes['title_from'] = before.get('title')
            changes['title_to'] = after.get('title')
        
        # Content change (significant threshold)
        before_length = before.get('body_html_length', 0)
        after_length = after.get('body_html_length', 0)
        delta = after_length - before_length
        
        if abs(delta) > 100:  # Only if significant change
            changes['content_changed'] = True
            changes['content_delta'] = delta
            changes['content_delta_percent'] = round((delta / before_length * 100), 2) if before_length > 0 else 0
        
        # Visible text change
        before_text = before.get('visible_text_length', 0)
        after_text = after.get('visible_text_length', 0)
        text_delta = after_text - before_text
        
        if abs(text_delta) > 50:
            changes['text_changed'] = True
            changes['text_delta'] = text_delta
        
        # Modal appeared
        if not before.get('has_modal') and after.get('has_modal'):
            changes['modal_appeared'] = True
        
        # Modal closed
        if before.get('has_modal') and not after.get('has_modal'):
            changes['modal_closed'] = True
        
        # Alert appeared
        if not before.get('has_alert') and after.get('has_alert'):
            changes['alert_appeared'] = True
        
        # Alert closed
        if before.get('has_alert') and not after.get('has_alert'):
            changes['alert_closed'] = True
        
        # Element count change
        before_count = before.get('element_count', 0)
        after_count = after.get('element_count', 0)
        element_delta = after_count - before_count
        
        if abs(element_delta) > 5:  # Threshold for DOM changes
            changes['dom_changed'] = True
            changes['element_delta'] = element_delta
        
        # Active element change (focus)
        if before.get('active_element') != after.get('active_element'):
            changes['focus_changed'] = True
            changes['focus_from'] = before.get('active_element')
            changes['focus_to'] = after.get('active_element')
        
        # Summary
        changes['has_changes'] = len(changes) > 0
        changes['change_count'] = len([k for k in changes.keys() if k not in ['has_changes', 'change_count']])
        
        return changes
    
    def _add_to_graph(self, interaction: Dict[str, Any]):
        """Add interaction to the interaction graph"""
        graph_node = {
            'from_url': interaction['url_before'],
            'to_url': interaction['url_after'],
            'element_type': interaction['element']['type'],
            'element_text': interaction['element']['text'][:50],
            'changes': list(interaction['changes_detected'].keys()),
            'timestamp': interaction['timestamp'],
        }
        self.interaction_graph.append(graph_node)
    
    def get_interaction_graph(self) -> List[Dict[str, Any]]:
        """Get the complete interaction graph"""
        return self.interaction_graph
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all interactions"""
        return {
            'total_interactions': len(self.explored_interactions),
            'interactions': self.explored_interactions,
            'interaction_graph': self.interaction_graph,
            'unique_states': len(self.interaction_states),
            'by_type': self._count_by_type(),
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count interactions by type"""
        counts = {}
        for interaction in self.explored_interactions:
            itype = interaction['interaction_type']
            counts[itype] = counts.get(itype, 0) + 1
        return counts