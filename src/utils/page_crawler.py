"""
Page Crawler - Main crawler that explores the website
"""
import asyncio
import hashlib
import re
from typing import Set, Dict, Any, List
from urllib.parse import urljoin, urlparse
from datetime import datetime


class PageCrawler:
    def __init__(self, base_url: str, config):
        self.base_url = base_url
        self.config = config
        self.visited_urls: Set[str] = set()
        self.visited_states: Set[str] = set()  # Hash of page states
        self.page_data: List[Dict[str, Any]] = []
        self.url_queue: List[tuple] = []  # (url, depth)
        
    def should_visit(self, url: str) -> bool:
        """Check if URL should be visited"""
        # Already visited
        if url in self.visited_urls:
            return False
        
        # Check if same domain
        parsed_base = urlparse(self.base_url)
        parsed_url = urlparse(url)
        
        if parsed_url.netloc and parsed_url.netloc != parsed_base.netloc:
            return False
        
        # Check ignore patterns
        for pattern in self.config.IGNORE_PATTERNS:
            if re.match(pattern, url):
                return False
        
        return True
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL for comparison"""
        # Remove fragments
        url = url.split('#')[0]
        
        # Convert relative to absolute
        if not url.startswith(('http://', 'https://')):
            url = urljoin(self.base_url, url)
        
        return url
    
    async def extract_links(self, page) -> List[str]:
        """Extract all links from current page"""
        try:
            links = await page.evaluate("""
                () => {
                    const links = [];
                    document.querySelectorAll('a[href]').forEach(a => {
                        links.push(a.href);
                    });
                    return links;
                }
            """)
            
            # Normalize and filter
            normalized_links = []
            for link in links:
                normalized = self.normalize_url(link)
                if self.should_visit(normalized):
                    normalized_links.append(normalized)
            
            return normalized_links
            
        except Exception as e:
            print(f"Error extracting links: {e}")
            return []
    
    async def get_page_state_hash(self, page) -> str:
        """Get hash of page state to detect duplicates"""
        try:
            # Get DOM structure without dynamic content
            state = await page.evaluate("""
                () => {
                    // Get simplified DOM structure
                    const getStructure = (elem, depth = 0) => {
                        if (depth > 3) return '';
                        let structure = elem.tagName;
                        for (let child of elem.children) {
                            structure += getStructure(child, depth + 1);
                        }
                        return structure;
                    };
                    
                    return {
                        url: window.location.pathname,
                        structure: getStructure(document.body),
                        title: document.title
                    };
                }
            """)
            
            # Create hash
            state_str = f"{state['url']}|{state['structure']}|{state['title']}"
            return hashlib.md5(state_str.encode()).hexdigest()
            
        except Exception as e:
            print(f"Error getting page state hash: {e}")
            return hashlib.md5(str(datetime.now()).encode()).hexdigest()
    
    async def find_interactive_elements(self, page) -> List[Dict[str, Any]]:
        """Find all interactive elements on the page"""
        try:
            elements = await page.evaluate(f"""
                () => {{
                    const selectors = {self.config.INTERACTIVE_SELECTORS};
                    const elements = [];
                    
                    selectors.forEach(selector => {{
                        try {{
                            document.querySelectorAll(selector).forEach((elem, index) => {{
                                const rect = elem.getBoundingClientRect();
                                
                                // Only visible elements
                                if (rect.width > 0 && rect.height > 0) {{
                                    elements.push({{
                                        selector: selector,
                                        index: index,
                                        tag: elem.tagName,
                                        text: elem.innerText?.substring(0, 50) || elem.value || '',
                                        id: elem.id || null,
                                        className: elem.className || null,
                                        href: elem.href || null,
                                        type: elem.type || null,
                                        visible: true,
                                        x: rect.x,
                                        y: rect.y
                                    }});
                                }}
                            }});
                        }} catch (e) {{
                            console.log('Error with selector:', selector, e);
                        }}
                    }});
                    
                    return elements;
                }}
            """)
            
            return elements
            
        except Exception as e:
            print(f"Error finding interactive elements: {e}")
            return []
    
    def add_to_queue(self, url: str, depth: int):
        """Add URL to crawl queue"""
        if depth >= self.config.MAX_DEPTH:
            return
        
        if url not in self.visited_urls:
            self.url_queue.append((url, depth))
    
    def get_summary(self) -> Dict[str, Any]:
        """Get crawl summary"""
        return {
            'total_pages_visited': len(self.visited_urls),
            'total_unique_states': len(self.visited_states),
            'urls_visited': list(self.visited_urls),
            'pages_remaining': len(self.url_queue),
            'page_data': self.page_data,
        }
    
    def is_complete(self) -> bool:
        """Check if crawling is complete"""
        return (
            len(self.visited_urls) >= self.config.MAX_PAGES or
            len(self.url_queue) == 0
        )