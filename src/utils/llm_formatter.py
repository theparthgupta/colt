"""
LLM Data Formatter - Formats exploration data for LLM consumption
"""
from typing import Dict, Any, List
from datetime import datetime


class LLMDataFormatter:
    def __init__(self):
        pass
    
    def format_page_data(self, page_data: Dict[str, Any]) -> str:
        """Format single page data as markdown for LLM - COMPLETE VERSION"""
        
        md = f"""# Page: {page_data['url']}

## Metadata
- **Title**: {page_data.get('structure', {}).get('title', 'N/A')}
- **Visited**: {page_data.get('timestamp', 'N/A')}
- **Load Time**: {page_data.get('load_time_ms', 'N/A')}ms

"""
        
        # DOM Statistics
        dom_stats = page_data.get('structure', {}).get('dom_statistics', {})
        if dom_stats:
            md += "## DOM Statistics\n"
            md += f"- **Total Elements**: {dom_stats.get('total_elements', 0)}\n"
            md += f"- **Unique Tag Types**: {dom_stats.get('unique_tags', 0)}\n"
            md += f"- **Links**: {dom_stats.get('total_links', 0)}\n"
            md += f"- **Images**: {dom_stats.get('total_images', 0)}\n"
            md += f"- **Forms**: {dom_stats.get('total_forms', 0)}\n"
            md += f"- **Buttons**: {dom_stats.get('total_buttons', 0)}\n"
            md += f"- **Inputs**: {dom_stats.get('total_inputs', 0)}\n\n"
        
        # Text Content Stats
        text_content = page_data.get('structure', {}).get('all_text_content', {})
        if text_content:
            md += "## Content Statistics\n"
            md += f"- **Word Count**: {text_content.get('word_count', 0)}\n"
            md += f"- **Character Count**: {text_content.get('character_count', 0)}\n\n"
        
        # Navigation
        nav = page_data.get('structure', {}).get('navigation', [])
        if nav:
            md += "## Navigation\n"
            for item in nav[:10]:
                text = item.get('text', 'No text')
                href = item.get('href', '#')
                md += f"- {text} → `{href}`\n"
            if len(nav) > 10:
                md += f"- ... and {len(nav) - 10} more navigation items\n"
            md += "\n"
        
        # All Headings
        headings = page_data.get('structure', {}).get('all_headings', [])
        if headings:
            md += "## All Headings\n"
            for h in headings[:20]:
                indent = "  " * (h['level'] - 1)
                md += f"{indent}- H{h['level']}: {h['text']}\n"
            if len(headings) > 20:
                md += f"- ... and {len(headings) - 20} more headings\n"
            md += "\n"
        
        # Main Content
        main = page_data.get('structure', {}).get('main_content', {})
        if main:
            md += "## Main Content Summary\n"
            
            paragraphs = main.get('paragraphs', [])
            if paragraphs:
                md += "### Content Preview\n"
                for p in paragraphs[:3]:
                    if p:
                        md += f"{p}...\n\n"
        
        # All Images
        images = page_data.get('structure', {}).get('all_images', [])
        if images:
            md += f"## Images ({len(images)})\n"
            for img in images[:10]:
                alt = img.get('alt', 'No alt text')
                src = img.get('src', 'N/A')
                md += f"- **{alt}** - `{src}`\n"
            if len(images) > 10:
                md += f"- ... and {len(images) - 10} more images\n"
            md += "\n"
        
        # All Links
        all_links = page_data.get('structure', {}).get('all_links', [])
        if all_links:
            md += f"## All Links ({len(all_links)})\n"
            # Group by type
            internal = [l for l in all_links if l.get('href', '').startswith('/') or 'localhost' in l.get('href', '')]
            external = [l for l in all_links if l.get('href', '').startswith('http') and 'localhost' not in l.get('href', '')]
            
            if internal:
                md += f"### Internal Links ({len(internal)})\n"
                for link in internal[:10]:
                    text = link.get('text', 'No text')[:50]
                    href = link.get('href', '#')
                    md += f"- [{text}]({href})\n"
            
            if external:
                md += f"### External Links ({len(external)})\n"
                for link in external[:10]:
                    text = link.get('text', 'No text')[:50]
                    href = link.get('href', '#')
                    md += f"- [{text}]({href})\n"
            md += "\n"
        
        # Forms (Complete)
        forms = page_data.get('structure', {}).get('forms', [])
        if forms:
            md += f"## Forms ({len(forms)})\n"
            for i, form in enumerate(forms):
                md += f"\n### Form {i+1}\n"
                md += f"- **Action**: {form.get('action', 'N/A')}\n"
                md += f"- **Method**: {form.get('method', 'GET').upper()}\n"
                
                inputs = form.get('inputs', [])
                if inputs:
                    md += "- **Fields**:\n"
                    for inp in inputs:
                        field_type = inp.get('type', 'text')
                        field_name = inp.get('name', 'unnamed')
                        required = " (required)" if inp.get('required') else ""
                        placeholder = f" - {inp.get('placeholder')}" if inp.get('placeholder') else ""
                        md += f"  - {field_name}: {field_type}{required}{placeholder}\n"
                md += "\n"
        
        # All Buttons
        buttons = page_data.get('structure', {}).get('all_buttons', [])
        if buttons:
            md += f"## Buttons ({len(buttons)})\n"
            for btn in buttons[:15]:
                text = btn.get('text', 'No text')[:50]
                btn_type = btn.get('type', 'button')
                disabled = " (disabled)" if btn.get('disabled') else ""
                md += f"- **{text}** - type: {btn_type}{disabled}\n"
            if len(buttons) > 15:
                md += f"- ... and {len(buttons) - 15} more buttons\n"
            md += "\n"
        
        # All Tables
        tables = page_data.get('structure', {}).get('all_tables', [])
        if tables:
            md += f"## Tables ({len(tables)})\n"
            for i, table in enumerate(tables):
                md += f"\n### Table {i+1}\n"
                md += f"- **Rows**: {table.get('row_count', 0)}\n"
                md += f"- **Columns**: {table.get('column_count', 0)}\n"
                if table.get('caption'):
                    md += f"- **Caption**: {table['caption']}\n"
                if table.get('headers'):
                    md += f"- **Headers**: {', '.join(table['headers'][:10])}\n"
            md += "\n"
        
        # Media Elements
        media = page_data.get('structure', {}).get('all_media', {})
        if media:
            videos = media.get('videos', [])
            audios = media.get('audios', [])
            iframes = media.get('iframes', [])
            
            if videos:
                md += f"## Videos ({len(videos)})\n"
                for video in videos:
                    src = video.get('src', 'N/A')
                    md += f"- {src}\n"
                md += "\n"
            
            if audios:
                md += f"## Audio Elements ({len(audios)})\n"
                for audio in audios:
                    src = audio.get('src', 'N/A')
                    md += f"- {src}\n"
                md += "\n"
            
            if iframes:
                md += f"## Iframes ({len(iframes)})\n"
                for iframe in iframes:
                    src = iframe.get('src', 'N/A')
                    title = iframe.get('title', 'No title')
                    md += f"- **{title}**: {src}\n"
                md += "\n"
        
        # Scripts
        scripts = page_data.get('structure', {}).get('all_scripts', [])
        if scripts:
            external_scripts = [s for s in scripts if s.get('src')]
            inline_scripts = [s for s in scripts if s.get('inline')]
            
            md += f"## Scripts ({len(scripts)} total)\n"
            md += f"- External: {len(external_scripts)}\n"
            md += f"- Inline: {len(inline_scripts)}\n"
            
            if external_scripts:
                md += "\n### External Scripts\n"
                for script in external_scripts[:10]:
                    src = script.get('src', 'N/A')
                    async_attr = " (async)" if script.get('async') else ""
                    defer_attr = " (defer)" if script.get('defer') else ""
                    md += f"- `{src}`{async_attr}{defer_attr}\n"
            md += "\n"
        
        # Data Attributes
        data_attrs = page_data.get('structure', {}).get('data_attributes', [])
        if data_attrs:
            md += f"## Elements with Data Attributes ({len(data_attrs)})\n"
            for elem in data_attrs[:10]:
                tag = elem.get('tag', 'unknown')
                attrs = elem.get('data_attributes', {})
                md += f"- **{tag}**: {', '.join(attrs.keys())}\n"
            md += "\n"
        
        # ARIA & Accessibility
        aria = page_data.get('structure', {}).get('aria_labels', [])
        if aria:
            md += f"## ARIA Labels ({len(aria)})\n"
            for elem in aria[:10]:
                tag = elem.get('tag', 'unknown')
                text = elem.get('text', '')[:30]
                aria_attrs = elem.get('aria_attributes', {})
                md += f"- **{tag}** ({text}): {', '.join(aria_attrs.keys())}\n"
            md += "\n"
        
        # JavaScript Storage
        local_storage = page_data.get('structure', {}).get('local_storage', {})
        session_storage = page_data.get('structure', {}).get('session_storage', {})
        
        if local_storage or session_storage:
            md += "## Browser Storage\n"
            if local_storage:
                md += f"- **localStorage**: {len(local_storage)} items\n"
            if session_storage:
                md += f"- **sessionStorage**: {len(session_storage)} items\n"
            md += "\n"
        
        # Cookies
        cookies = page_data.get('structure', {}).get('cookies', [])
        if cookies:
            md += f"## Cookies ({len(cookies)})\n"
            for cookie in cookies[:10]:
                name = cookie.get('name', 'unknown')
                domain = cookie.get('domain', 'N/A')
                md += f"- **{name}** (domain: {domain})\n"
            md += "\n"
        
        # Network Activity
        network = page_data.get('network', {})
        if network:
            md += "## Network Activity\n"
            md += f"- **Total Requests**: {network.get('total_requests', 0)}\n"
            md += f"- **Total Responses**: {network.get('total_responses', 0)}\n"
            
            api_calls = network.get('api_calls', [])
            if api_calls:
                md += f"\n### API Calls ({len(api_calls)})\n"
                for api in api_calls[:10]:
                    method = api.get('method', 'GET')
                    url = api.get('url', 'N/A')
                    md += f"- `{method}` {url}\n"
            
            resource_breakdown = network.get('resource_breakdown', {})
            if resource_breakdown:
                md += "\n### Resources by Type\n"
                for res_type, count in resource_breakdown.items():
                    md += f"- {res_type}: {count}\n"
            
            md += "\n"
        
        # DOM Mutations
        mutations = page_data.get('dom_mutations', {})
        if mutations and mutations.get('total_mutations', 0) > 0:
            md += "## DOM Mutations\n"
            md += f"- **Total**: {mutations.get('total_mutations', 0)}\n"
            
            by_type = mutations.get('by_type', {})
            for mutation_type, count in by_type.items():
                md += f"- **{mutation_type}**: {count}\n"
            md += "\n"
        
        # Interactions
        interactions = page_data.get('interactions', {})
        if interactions and interactions.get('total_interactions', 0) > 0:
            md += "## User Interactions\n"
            md += f"- **Total**: {interactions.get('total_interactions', 0)}\n"
            
            by_type = interactions.get('by_type', {})
            for itype, count in by_type.items():
                md += f"- **{itype.capitalize()}**: {count}\n"
            
            md += "\n"
        
        # Console Messages
        console = page_data.get('console', {})
        if console:
            errors = console.get('errors', [])
            warnings = console.get('warnings', [])
            
            if errors:
                md += f"## Console Errors ({len(errors)})\n"
                for err in errors[:5]:
                    md += f"- {err.get('text', 'N/A')}\n"
                md += "\n"
            
            if warnings:
                md += f"## Console Warnings ({len(warnings)})\n"
                for warn in warnings[:5]:
                    md += f"- {warn.get('text', 'N/A')}\n"
                md += "\n"
        
        md += "---\n\n"
        return md
    
    def format_site_overview(self, all_pages: List[Dict[str, Any]]) -> str:
        """Format complete site overview for LLM"""
        
        md = f"""# Website Exploration Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Pages Explored**: {len(all_pages)}

## Site Map

"""
        
        # Create site map
        for page in all_pages:
            url = page.get('url', 'Unknown')
            title = page.get('structure', {}).get('title', 'No title')
            md += f"- [{title}]({url})\n"
        
        md += "\n## Page Details\n\n"
        
        # Add each page
        for page in all_pages:
            md += self.format_page_data(page)
        
        # Summary statistics
        md += "## Summary Statistics\n\n"
        
        total_forms = sum(len(p.get('structure', {}).get('forms', [])) for p in all_pages)
        total_links = sum(len(p.get('structure', {}).get('navigation', [])) for p in all_pages)
        total_api_calls = sum(p.get('network', {}).get('total_requests', 0) for p in all_pages)
        
        md += f"- **Total Forms**: {total_forms}\n"
        md += f"- **Total Navigation Links**: {total_links}\n"
        md += f"- **Total API Calls**: {total_api_calls}\n"
        
        return md
    
    def format_for_analysis(self, all_pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format data in structured JSON for analysis"""
        
        return {
            'metadata': {
                'total_pages': len(all_pages),
                'generated_at': datetime.now().isoformat(),
            },
            'pages': all_pages,
            'site_structure': self._analyze_site_structure(all_pages),
            'common_patterns': self._find_common_patterns(all_pages),
        }
    
    def _analyze_site_structure(self, all_pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall site structure"""
        
        all_urls = [p.get('url', '') for p in all_pages]
        
        # Extract common paths
        paths = {}
        for url in all_urls:
            parts = url.split('/')
            for i, part in enumerate(parts):
                if part:
                    depth = i
                    if depth not in paths:
                        paths[depth] = set()
                    paths[depth].add(part)
        
        return {
            'total_pages': len(all_pages),
            'url_patterns': {k: list(v) for k, v in paths.items()},
        }
    
    def _find_common_patterns(self, all_pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find common patterns across pages"""
        
        # Common navigation
        nav_items = {}
        for page in all_pages:
            nav = page.get('structure', {}).get('navigation', [])
            for item in nav:
                text = item.get('text', '')
                if text:
                    nav_items[text] = nav_items.get(text, 0) + 1
        
        # Sort by frequency
        common_nav = sorted(nav_items.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'common_navigation': [{'text': text, 'frequency': freq} for text, freq in common_nav],
        }