"""
DOM Mutation Observer - Tracks ALL DOM changes in real-time
"""
import json
from datetime import datetime
from typing import List, Dict, Any


class DOMMutationObserver:
    def __init__(self):
        self.mutations: List[Dict[str, Any]] = []
        self.mutation_summary: Dict[str, int] = {}
        
    async def setup_mutation_observer(self, page):
        """Setup comprehensive MutationObserver on the page"""
        await page.evaluate("""
            () => {
                // Store mutations in window object
                if (!window.__domMutations) {
                    window.__domMutations = [];
                }
                
                // Create mutation observer
                const observer = new MutationObserver((mutations) => {
                    mutations.forEach((mutation) => {
                        const record = {
                            type: mutation.type,
                            timestamp: new Date().toISOString(),
                            target: {
                                tagName: mutation.target.tagName,
                                id: mutation.target.id || null,
                                className: mutation.target.className || null,
                            }
                        };
                        
                        if (mutation.type === 'attributes') {
                            record.attributeName = mutation.attributeName;
                            record.oldValue = mutation.oldValue;
                            record.newValue = mutation.target.getAttribute(mutation.attributeName);
                        } else if (mutation.type === 'childList') {
                            record.addedNodes = mutation.addedNodes.length;
                            record.removedNodes = mutation.removedNodes.length;
                            record.addedNodeTypes = Array.from(mutation.addedNodes)
                                .map(n => n.nodeType === 1 ? n.tagName : 'text')
                                .filter(Boolean);
                            record.removedNodeTypes = Array.from(mutation.removedNodes)
                                .map(n => n.nodeType === 1 ? n.tagName : 'text')
                                .filter(Boolean);
                        } else if (mutation.type === 'characterData') {
                            record.oldValue = mutation.oldValue;
                            record.newValue = mutation.target.textContent?.substring(0, 100);
                        }
                        
                        window.__domMutations.push(record);
                    });
                });
                
                // Observe everything
                observer.observe(document.body, {
                    childList: true,           // Watch for added/removed nodes
                    attributes: true,          // Watch for attribute changes
                    characterData: true,       // Watch for text changes
                    subtree: true,             // Watch entire tree
                    attributeOldValue: true,   // Record old attribute values
                    characterDataOldValue: true // Record old text values
                });
                
                // Store observer reference
                window.__mutationObserver = observer;
            }
        """)
    
    async def collect_mutations(self, page):
        """Collect all mutations from the page"""
        try:
            mutations = await page.evaluate("() => window.__domMutations || []")
            
            # Add to our list
            for mutation in mutations:
                self.mutations.append(mutation)
                
                # Update summary
                mutation_type = mutation.get('type', 'unknown')
                self.mutation_summary[mutation_type] = self.mutation_summary.get(mutation_type, 0) + 1
            
            # Clear the page's mutation list
            await page.evaluate("() => { window.__domMutations = []; }")
            
        except Exception as e:
            print(f"Error collecting mutations: {e}")
    
    async def stop_observer(self, page):
        """Stop the mutation observer"""
        try:
            await page.evaluate("""
                () => {
                    if (window.__mutationObserver) {
                        window.__mutationObserver.disconnect();
                    }
                }
            """)
        except Exception as e:
            print(f"Error stopping observer: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of mutations"""
        return {
            'total_mutations': len(self.mutations),
            'mutations': self.mutations,
            'by_type': self.mutation_summary,
            'attribute_changes': [m for m in self.mutations if m['type'] == 'attributes'],
            'child_list_changes': [m for m in self.mutations if m['type'] == 'childList'],
            'text_changes': [m for m in self.mutations if m['type'] == 'characterData'],
        }
    
    def clear(self):
        """Clear all mutations"""
        self.mutations.clear()
        self.mutation_summary.clear()
    
    def export_to_json(self) -> str:
        """Export mutation data to JSON string"""
        return json.dumps(self.get_summary(), indent=2)