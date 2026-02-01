"""
Interaction Tracker - Tracks all user interactions with the page
"""
import json
from datetime import datetime
from typing import List, Dict, Any


class InteractionTracker:
    def __init__(self):
        self.interactions: List[Dict[str, Any]] = []
        
    async def setup_page_listeners(self, page):
        """Setup JavaScript listeners on the page to track interactions"""
        await page.evaluate("""
            () => {
                // Store interactions in window object
                if (!window.__interactions) {
                    window.__interactions = [];
                }
                
                // Track clicks
                document.addEventListener('click', (e) => {
                    const element = e.target;
                    window.__interactions.push({
                        type: 'click',
                        timestamp: new Date().toISOString(),
                        tagName: element.tagName,
                        id: element.id || null,
                        className: element.className || null,
                        text: element.innerText?.substring(0, 50) || null,
                        href: element.href || null,
                        coordinates: { x: e.clientX, y: e.clientY }
                    });
                }, true);
                
                // Track form submissions
                document.addEventListener('submit', (e) => {
                    const form = e.target;
                    window.__interactions.push({
                        type: 'submit',
                        timestamp: new Date().toISOString(),
                        formId: form.id || null,
                        formAction: form.action || null,
                        formMethod: form.method || null
                    });
                }, true);
                
                // Track input changes
                document.addEventListener('change', (e) => {
                    const element = e.target;
                    if (element.tagName === 'INPUT' || element.tagName === 'SELECT' || element.tagName === 'TEXTAREA') {
                        window.__interactions.push({
                            type: 'change',
                            timestamp: new Date().toISOString(),
                            tagName: element.tagName,
                            inputType: element.type || null,
                            id: element.id || null,
                            name: element.name || null
                        });
                    }
                }, true);
                
                // Track scroll events (throttled)
                let scrollTimeout;
                window.addEventListener('scroll', () => {
                    clearTimeout(scrollTimeout);
                    scrollTimeout = setTimeout(() => {
                        window.__interactions.push({
                            type: 'scroll',
                            timestamp: new Date().toISOString(),
                            scrollY: window.scrollY,
                            scrollX: window.scrollX
                        });
                    }, 200);
                }, true);
            }
        """)
    
    async def collect_interactions(self, page):
        """Collect interactions from the page"""
        try:
            interactions = await page.evaluate("() => window.__interactions || []")
            
            # Add to our list
            for interaction in interactions:
                self.interactions.append(interaction)
            
            # Clear the page's interaction list
            await page.evaluate("() => { window.__interactions = []; }")
            
        except Exception as e:
            print(f"Error collecting interactions: {e}")
    
    def add_interaction(self, interaction_type: str, details: Dict[str, Any]):
        """Manually add an interaction"""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'type': interaction_type,
            **details
        }
        self.interactions.append(interaction)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of interactions"""
        interaction_types = {}
        for interaction in self.interactions:
            itype = interaction.get('type', 'unknown')
            interaction_types[itype] = interaction_types.get(itype, 0) + 1
        
        return {
            'total_interactions': len(self.interactions),
            'interactions': self.interactions,
            'by_type': interaction_types,
            'clicks': [i for i in self.interactions if i['type'] == 'click'],
            'forms': [i for i in self.interactions if i['type'] == 'submit'],
        }
    
    def clear(self):
        """Clear all tracked interactions"""
        self.interactions.clear()
    
    def export_to_json(self) -> str:
        """Export interaction data to JSON string"""
        return json.dumps(self.get_summary(), indent=2)