"""
Network Monitor - Captures all network requests and responses
"""
import json
from datetime import datetime
from typing import List, Dict, Any


class NetworkMonitor:
    def __init__(self):
        self.requests: List[Dict[str, Any]] = []
        self.responses: List[Dict[str, Any]] = []
        
    def on_request(self, request):
        """Capture outgoing request"""
        try:
            request_data = {
                'timestamp': datetime.now().isoformat(),
                'url': request.url,
                'method': request.method,
                'headers': dict(request.headers),
                'resource_type': request.resource_type,
                'post_data': request.post_data if request.method == 'POST' else None,
            }
            self.requests.append(request_data)
        except Exception as e:
            print(f"Error capturing request: {e}")
    
    def on_response(self, response):
        """Capture incoming response"""
        try:
            response_data = {
                'timestamp': datetime.now().isoformat(),
                'url': response.url,
                'status': response.status,
                'status_text': response.status_text,
                'headers': dict(response.headers),
                'resource_type': response.request.resource_type,
            }
            self.responses.append(response_data)
        except Exception as e:
            print(f"Error capturing response: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of network activity"""
        return {
            'total_requests': len(self.requests),
            'total_responses': len(self.responses),
            'requests': self.requests,
            'responses': self.responses,
            'api_calls': [r for r in self.requests if '/api/' in r['url']],
            'resource_breakdown': self._get_resource_breakdown(),
        }
    
    def _get_resource_breakdown(self) -> Dict[str, int]:
        """Get breakdown of resources by type"""
        breakdown = {}
        for req in self.requests:
            res_type = req.get('resource_type', 'unknown')
            breakdown[res_type] = breakdown.get(res_type, 0) + 1
        return breakdown
    
    def clear(self):
        """Clear all captured data"""
        self.requests.clear()
        self.responses.clear()
    
    def export_to_json(self) -> str:
        """Export network data to JSON string"""
        return json.dumps(self.get_summary(), indent=2)