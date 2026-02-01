"""
Console Monitor - Captures browser console messages
"""
import json
from datetime import datetime
from typing import List, Dict, Any


class ConsoleMonitor:
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []
        
    def on_console(self, msg):
        """Capture console message"""
        try:
            message_data = {
                'timestamp': datetime.now().isoformat(),
                'type': msg.type,
                'text': msg.text,
                'location': msg.location if hasattr(msg, 'location') else None,
            }
            self.messages.append(message_data)
        except Exception as e:
            print(f"Error capturing console message: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of console activity"""
        return {
            'total_messages': len(self.messages),
            'messages': self.messages,
            'errors': [m for m in self.messages if m['type'] == 'error'],
            'warnings': [m for m in self.messages if m['type'] == 'warning'],
            'logs': [m for m in self.messages if m['type'] == 'log'],
        }
    
    def clear(self):
        """Clear all captured messages"""
        self.messages.clear()
    
    def export_to_json(self) -> str:
        """Export console data to JSON string"""
        return json.dumps(self.get_summary(), indent=2)