"""
DOM Extractor - Extracts semantic structure from DOM
"""
import json
from typing import Dict, Any, List
from bs4 import BeautifulSoup


class DOMExtractor:
    def __init__(self):
        pass
    
    async def extract_page_structure(self, page) -> Dict[str, Any]:
        """Extract COMPLETE structure from the current page - leaves nothing untouched"""
        
        # Get page metadata
        title = await page.title()
        url = page.url
        
        # Get HTML content
        html_content = await page.content()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract EVERYTHING
        structure = {
            'url': url,
            'title': title,
            
            # Basic metadata
            'metadata': self._extract_metadata(soup),
            
            # Structural elements
            'navigation': self._extract_navigation(soup),
            'header': self._extract_header(soup),
            'main_content': self._extract_main_content(soup),
            'footer': self._extract_footer(soup),
            'sidebar': self._extract_sidebar(soup),
            
            # All content types
            'forms': self._extract_forms(soup),
            'interactive_elements': await self._extract_interactive_elements(page),
            'semantic_sections': self._extract_semantic_sections(soup),
            'all_links': self._extract_all_links(soup),
            'all_images': self._extract_all_images(soup),
            'all_media': self._extract_all_media(soup),
            'all_scripts': self._extract_all_scripts(soup),
            'all_styles': self._extract_all_styles(soup),
            
            # Detailed content analysis
            'all_text_content': self._extract_all_text(soup),
            'all_headings': self._extract_all_headings(soup),
            'all_lists': self._extract_all_lists(soup),
            'all_tables': self._extract_all_tables(soup),
            'all_buttons': self._extract_all_buttons(soup),
            'all_inputs': self._extract_all_inputs(soup),
            
            # Data attributes and custom elements
            'data_attributes': self._extract_data_attributes(soup),
            'aria_labels': self._extract_aria_labels(soup),
            'custom_elements': self._extract_custom_elements(soup),
            
            # DOM structure analysis
            'dom_depth': await self._analyze_dom_depth(page),
            'dom_statistics': self._get_dom_statistics(soup),
            'accessibility_tree': await self._get_accessibility_tree(page),
            
            # JavaScript state
            'js_variables': await self._extract_js_variables(page),
            'local_storage': await self._extract_local_storage(page),
            'session_storage': await self._extract_session_storage(page),
            'cookies': await self._extract_cookies(page),
            
            # Complete HTML
            'full_html': html_content,
            'body_html': str(soup.body) if soup.body else '',
        }
        
        return structure
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract page metadata"""
        metadata = {}
        
        # Meta tags
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            name = tag.get('name') or tag.get('property')
            content = tag.get('content')
            if name and content:
                metadata[name] = content
        
        return metadata
    
    def _extract_navigation(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract navigation links"""
        nav_items = []
        
        # Find nav elements
        nav_elements = soup.find_all('nav')
        for nav in nav_elements:
            links = nav.find_all('a')
            for link in links:
                nav_items.append({
                    'text': link.get_text(strip=True),
                    'href': link.get('href'),
                    'aria_label': link.get('aria-label'),
                })
        
        return nav_items
    
    def _extract_header(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract header content"""
        header = soup.find('header')
        if not header:
            return {}
        
        return {
            'text': header.get_text(strip=True)[:500],
            'has_logo': bool(header.find('img')),
            'links': len(header.find_all('a')),
        }
    
    def _extract_main_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract main content"""
        main = soup.find('main') or soup.find('div', {'role': 'main'})
        
        if not main:
            # Fallback to body
            main = soup.find('body')
        
        if not main:
            return {}
        
        # Extract headings
        headings = []
        for i in range(1, 7):
            for heading in main.find_all(f'h{i}'):
                headings.append({
                    'level': i,
                    'text': heading.get_text(strip=True)
                })
        
        # Extract paragraphs (first 5)
        paragraphs = [p.get_text(strip=True)[:200] for p in main.find_all('p')[:5]]
        
        # Extract lists
        lists = []
        for ul in main.find_all(['ul', 'ol'])[:3]:
            items = [li.get_text(strip=True) for li in ul.find_all('li')[:5]]
            lists.append({
                'type': ul.name,
                'items': items
            })
        
        return {
            'headings': headings,
            'paragraphs': paragraphs,
            'lists': lists,
            'images': len(main.find_all('img')),
            'tables': len(main.find_all('table')),
        }
    
    def _extract_footer(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract footer content"""
        footer = soup.find('footer')
        if not footer:
            return {}
        
        return {
            'text': footer.get_text(strip=True)[:200],
            'links': len(footer.find_all('a')),
        }
    
    def _extract_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract form information"""
        forms = []
        
        for form in soup.find_all('form'):
            inputs = []
            for input_elem in form.find_all(['input', 'select', 'textarea']):
                inputs.append({
                    'type': input_elem.get('type', input_elem.name),
                    'name': input_elem.get('name'),
                    'id': input_elem.get('id'),
                    'placeholder': input_elem.get('placeholder'),
                    'required': input_elem.has_attr('required'),
                })
            
            forms.append({
                'action': form.get('action'),
                'method': form.get('method', 'get'),
                'id': form.get('id'),
                'inputs': inputs,
            })
        
        return forms
    
    async def _extract_interactive_elements(self, page) -> List[Dict[str, Any]]:
        """Extract interactive elements using JavaScript"""
        try:
            elements = await page.evaluate("""
                () => {
                    const selectors = [
                        'button:not([disabled])',
                        'a[href]',
                        'input[type="submit"]',
                        'input[type="button"]',
                        '[role="button"]',
                        '[onclick]'
                    ];
                    
                    const elements = [];
                    selectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(elem => {
                            elements.push({
                                tag: elem.tagName,
                                text: elem.innerText?.substring(0, 50) || elem.value || '',
                                id: elem.id || null,
                                className: elem.className || null,
                                href: elem.href || null,
                                type: elem.type || null,
                                ariaLabel: elem.getAttribute('aria-label'),
                            });
                        });
                    });
                    
                    return elements;
                }
            """)
            return elements
        except Exception as e:
            print(f"Error extracting interactive elements: {e}")
            return []
    
    def _extract_semantic_sections(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract semantic HTML5 sections"""
        sections = []
        
        semantic_tags = ['article', 'section', 'aside', 'nav', 'header', 'footer']
        
        for tag_name in semantic_tags:
            for elem in soup.find_all(tag_name):
                sections.append({
                    'tag': tag_name,
                    'id': elem.get('id'),
                    'class': ' '.join(elem.get('class', [])),
                    'preview': elem.get_text(strip=True)[:100],
                })
        
        return sections
    
    def _extract_sidebar(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract sidebar content"""
        sidebar = soup.find('aside') or soup.find('div', {'class': lambda x: x and 'sidebar' in x.lower()})
        
        if not sidebar:
            return {}
        
        return {
            'text': sidebar.get_text(strip=True)[:500],
            'links': len(sidebar.find_all('a')),
            'widgets': len(sidebar.find_all(['div', 'section'])),
        }
    
    def _extract_all_links(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract ALL links from the page"""
        links = []
        for a in soup.find_all('a'):
            links.append({
                'href': a.get('href'),
                'text': a.get_text(strip=True)[:100],
                'title': a.get('title'),
                'target': a.get('target'),
                'rel': a.get('rel'),
                'aria_label': a.get('aria-label'),
                'id': a.get('id'),
                'classes': a.get('class', []),
            })
        return links
    
    def _extract_all_images(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract ALL images"""
        images = []
        for img in soup.find_all('img'):
            images.append({
                'src': img.get('src'),
                'alt': img.get('alt'),
                'title': img.get('title'),
                'width': img.get('width'),
                'height': img.get('height'),
                'loading': img.get('loading'),
                'srcset': img.get('srcset'),
                'id': img.get('id'),
                'classes': img.get('class', []),
            })
        return images
    
    def _extract_all_media(self, soup: BeautifulSoup) -> Dict[str, List[Dict[str, Any]]]:
        """Extract all media elements (video, audio, iframe, embed)"""
        media = {
            'videos': [],
            'audios': [],
            'iframes': [],
            'embeds': [],
        }
        
        # Videos
        for video in soup.find_all('video'):
            media['videos'].append({
                'src': video.get('src'),
                'sources': [s.get('src') for s in video.find_all('source')],
                'poster': video.get('poster'),
                'controls': video.has_attr('controls'),
                'autoplay': video.has_attr('autoplay'),
            })
        
        # Audio
        for audio in soup.find_all('audio'):
            media['audios'].append({
                'src': audio.get('src'),
                'sources': [s.get('src') for s in audio.find_all('source')],
                'controls': audio.has_attr('controls'),
            })
        
        # Iframes
        for iframe in soup.find_all('iframe'):
            media['iframes'].append({
                'src': iframe.get('src'),
                'title': iframe.get('title'),
                'width': iframe.get('width'),
                'height': iframe.get('height'),
            })
        
        # Embeds
        for embed in soup.find_all('embed'):
            media['embeds'].append({
                'src': embed.get('src'),
                'type': embed.get('type'),
            })
        
        return media
    
    def _extract_all_scripts(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract all script tags"""
        scripts = []
        for script in soup.find_all('script'):
            scripts.append({
                'src': script.get('src'),
                'type': script.get('type'),
                'async': script.has_attr('async'),
                'defer': script.has_attr('defer'),
                'inline': bool(script.string),
                'content_preview': script.string[:200] if script.string else None,
            })
        return scripts
    
    def _extract_all_styles(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract all style tags and links"""
        styles = []
        
        # External stylesheets
        for link in soup.find_all('link', {'rel': 'stylesheet'}):
            styles.append({
                'type': 'external',
                'href': link.get('href'),
                'media': link.get('media'),
            })
        
        # Inline styles
        for style in soup.find_all('style'):
            styles.append({
                'type': 'inline',
                'content_preview': style.string[:200] if style.string else None,
            })
        
        return styles
    
    def _extract_all_text(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract all text content comprehensively"""
        body = soup.body if soup.body else soup
        
        return {
            'full_text': body.get_text(separator=' ', strip=True),
            'visible_text': body.get_text(separator=' ', strip=True),  # Could be enhanced with visibility checks
            'word_count': len(body.get_text(separator=' ', strip=True).split()),
            'character_count': len(body.get_text(strip=True)),
        }
    
    def _extract_all_headings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract ALL headings (h1-h6)"""
        headings = []
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                headings.append({
                    'level': i,
                    'text': heading.get_text(strip=True),
                    'id': heading.get('id'),
                    'classes': heading.get('class', []),
                })
        return headings
    
    def _extract_all_lists(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract ALL lists (ul, ol, dl)"""
        lists = []
        
        for ul in soup.find_all(['ul', 'ol']):
            items = [li.get_text(strip=True) for li in ul.find_all('li', recursive=False)]
            lists.append({
                'type': ul.name,
                'items': items,
                'item_count': len(items),
                'id': ul.get('id'),
                'classes': ul.get('class', []),
            })
        
        # Definition lists
        for dl in soup.find_all('dl'):
            lists.append({
                'type': 'definition',
                'terms': [dt.get_text(strip=True) for dt in dl.find_all('dt')],
                'definitions': [dd.get_text(strip=True) for dd in dl.find_all('dd')],
            })
        
        return lists
    
    def _extract_all_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract ALL tables with complete structure"""
        tables = []
        
        for table in soup.find_all('table'):
            headers = []
            rows = []
            
            # Extract headers
            for th in table.find_all('th'):
                headers.append(th.get_text(strip=True))
            
            # Extract rows
            for tr in table.find_all('tr'):
                cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                if cells:
                    rows.append(cells)
            
            tables.append({
                'headers': headers,
                'rows': rows,
                'row_count': len(rows),
                'column_count': len(headers) if headers else (len(rows[0]) if rows else 0),
                'id': table.get('id'),
                'classes': table.get('class', []),
                'caption': table.find('caption').get_text(strip=True) if table.find('caption') else None,
            })
        
        return tables
    
    def _extract_all_buttons(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract ALL buttons"""
        buttons = []
        
        for button in soup.find_all('button'):
            buttons.append({
                'text': button.get_text(strip=True),
                'type': button.get('type', 'button'),
                'id': button.get('id'),
                'classes': button.get('class', []),
                'disabled': button.has_attr('disabled'),
                'aria_label': button.get('aria-label'),
                'data_attributes': {k: v for k, v in button.attrs.items() if k.startswith('data-')},
            })
        
        return buttons
    
    def _extract_all_inputs(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract ALL input fields, textareas, selects"""
        inputs = []
        
        # Input fields
        for inp in soup.find_all('input'):
            inputs.append({
                'element': 'input',
                'type': inp.get('type', 'text'),
                'name': inp.get('name'),
                'id': inp.get('id'),
                'placeholder': inp.get('placeholder'),
                'value': inp.get('value'),
                'required': inp.has_attr('required'),
                'disabled': inp.has_attr('disabled'),
                'pattern': inp.get('pattern'),
                'min': inp.get('min'),
                'max': inp.get('max'),
                'classes': inp.get('class', []),
            })
        
        # Textareas
        for textarea in soup.find_all('textarea'):
            inputs.append({
                'element': 'textarea',
                'name': textarea.get('name'),
                'id': textarea.get('id'),
                'placeholder': textarea.get('placeholder'),
                'required': textarea.has_attr('required'),
                'rows': textarea.get('rows'),
                'cols': textarea.get('cols'),
            })
        
        # Select dropdowns
        for select in soup.find_all('select'):
            options = [opt.get_text(strip=True) for opt in select.find_all('option')]
            inputs.append({
                'element': 'select',
                'name': select.get('name'),
                'id': select.get('id'),
                'required': select.has_attr('required'),
                'multiple': select.has_attr('multiple'),
                'options': options,
                'option_count': len(options),
            })
        
        return inputs
    
    def _extract_data_attributes(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract all elements with data-* attributes"""
        data_attrs = []
        
        for elem in soup.find_all(True):  # Find all elements
            data = {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
            if data:
                data_attrs.append({
                    'tag': elem.name,
                    'id': elem.get('id'),
                    'classes': elem.get('class', []),
                    'data_attributes': data,
                })
        
        return data_attrs
    
    def _extract_aria_labels(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract all ARIA labels and accessibility attributes"""
        aria_elements = []
        
        aria_attrs = ['aria-label', 'aria-labelledby', 'aria-describedby', 'aria-hidden', 'role']
        
        for elem in soup.find_all(True):
            aria = {k: v for k, v in elem.attrs.items() if k.startswith('aria-') or k == 'role'}
            if aria:
                aria_elements.append({
                    'tag': elem.name,
                    'id': elem.get('id'),
                    'text': elem.get_text(strip=True)[:50],
                    'aria_attributes': aria,
                })
        
        return aria_elements
    
    def _extract_custom_elements(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract custom/web components (tags with hyphens)"""
        custom = []
        
        for elem in soup.find_all(True):
            if '-' in elem.name:  # Custom elements have hyphens
                custom.append({
                    'tag': elem.name,
                    'id': elem.get('id'),
                    'classes': elem.get('class', []),
                    'attributes': dict(elem.attrs),
                })
        
        return custom
    
    def _get_dom_statistics(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Get comprehensive DOM statistics"""
        all_elements = soup.find_all(True)
        
        tag_counts = {}
        for elem in all_elements:
            tag_counts[elem.name] = tag_counts.get(elem.name, 0) + 1
        
        return {
            'total_elements': len(all_elements),
            'unique_tags': len(tag_counts),
            'tag_distribution': tag_counts,
            'total_links': len(soup.find_all('a')),
            'total_images': len(soup.find_all('img')),
            'total_forms': len(soup.find_all('form')),
            'total_buttons': len(soup.find_all('button')),
            'total_inputs': len(soup.find_all(['input', 'textarea', 'select'])),
            'total_scripts': len(soup.find_all('script')),
            'total_styles': len(soup.find_all(['style', 'link'])),
        }
    
    async def _analyze_dom_depth(self, page) -> Dict[str, Any]:
        """Analyze DOM tree depth and structure"""
        try:
            result = await page.evaluate("""
                () => {
                    const getDepth = (element) => {
                        let maxDepth = 0;
                        for (let child of element.children) {
                            maxDepth = Math.max(maxDepth, getDepth(child));
                        }
                        return maxDepth + 1;
                    };
                    
                    const countNodes = (element) => {
                        let count = 1;
                        for (let child of element.children) {
                            count += countNodes(child);
                        }
                        return count;
                    };
                    
                    return {
                        maxDepth: getDepth(document.body),
                        totalNodes: countNodes(document.body),
                        bodyChildren: document.body.children.length,
                    };
                }
            """)
            return result
        except Exception as e:
            print(f"Error analyzing DOM depth: {e}")
            return {}
    
    async def _get_accessibility_tree(self, page) -> Dict[str, Any]:
        """Get accessibility tree snapshot"""
        try:
            snapshot = await page.accessibility.snapshot()
            return snapshot if snapshot else {}
        except Exception as e:
            print(f"Error getting accessibility tree: {e}")
            return {}
    
    async def _extract_js_variables(self, page) -> Dict[str, Any]:
        """Extract JavaScript global variables"""
        try:
            variables = await page.evaluate("""
                () => {
                    const globals = {};
                    const excludeKeys = ['top', 'window', 'document', 'location', 'navigator', 'screen', 'history'];
                    
                    for (let key in window) {
                        if (!excludeKeys.includes(key) && typeof window[key] !== 'function') {
                            try {
                                const value = window[key];
                                if (value && typeof value === 'object') {
                                    globals[key] = '[Object]';
                                } else if (Array.isArray(value)) {
                                    globals[key] = '[Array]';
                                } else {
                                    globals[key] = String(value).substring(0, 100);
                                }
                            } catch (e) {
                                // Skip inaccessible properties
                            }
                        }
                    }
                    
                    return globals;
                }
            """)
            return variables
        except Exception as e:
            print(f"Error extracting JS variables: {e}")
            return {}
    
    async def _extract_local_storage(self, page) -> Dict[str, str]:
        """Extract localStorage data"""
        try:
            storage = await page.evaluate("""
                () => {
                    const data = {};
                    for (let i = 0; i < localStorage.length; i++) {
                        const key = localStorage.key(i);
                        data[key] = localStorage.getItem(key);
                    }
                    return data;
                }
            """)
            return storage
        except Exception as e:
            print(f"Error extracting localStorage: {e}")
            return {}
    
    async def _extract_session_storage(self, page) -> Dict[str, str]:
        """Extract sessionStorage data"""
        try:
            storage = await page.evaluate("""
                () => {
                    const data = {};
                    for (let i = 0; i < sessionStorage.length; i++) {
                        const key = sessionStorage.key(i);
                        data[key] = sessionStorage.getItem(key);
                    }
                    return data;
                }
            """)
            return storage
        except Exception as e:
            print(f"Error extracting sessionStorage: {e}")
            return {}
    
    async def _extract_cookies(self, page) -> List[Dict[str, Any]]:
        """Extract cookies"""
        try:
            cookies = await page.context.cookies()
            return [
                {
                    'name': c['name'],
                    'value': c['value'][:100],  # Truncate for safety
                    'domain': c['domain'],
                    'path': c['path'],
                    'secure': c.get('secure', False),
                    'httpOnly': c.get('httpOnly', False),
                }
                for c in cookies
            ]
        except Exception as e:
            print(f"Error extracting cookies: {e}")
            return []
    
    def export_to_json(self, structure: Dict[str, Any]) -> str:
        """Export structure to JSON string"""
        return json.dumps(structure, indent=2)