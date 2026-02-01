"""
Website Explorer - Main orchestrator
"""
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

from config import Config
from src.monitors.network_monitor import NetworkMonitor
from src.monitors.console_monitor import ConsoleMonitor
from src.monitors.interaction_tracker import InteractionTracker
from src.monitors.dom_mutation_observer import DOMMutationObserver
from src.extractors.dom_extractor import DOMExtractor
from src.utils.page_crawler import PageCrawler
from src.utils.llm_formatter import LLMDataFormatter
from src.utils.smart_form_filler import SmartFormFiller
from src.utils.interaction_explorer import InteractionExplorer
from src.analyzers.text_analyzer import TextAnalyzer
from src.analyzers.agent_preparation import AgentPreparation


class WebsiteExplorer:
    def __init__(self, config=None):
        self.config = config or Config()
        
        # Monitors
        self.network_monitor = NetworkMonitor()
        self.console_monitor = ConsoleMonitor()
        self.interaction_tracker = InteractionTracker()
        self.dom_mutation_observer = DOMMutationObserver()
        
        # Extractors & Analyzers
        self.dom_extractor = DOMExtractor()
        self.text_analyzer = TextAnalyzer(self.config)
        
        # Utilities
        self.page_crawler = PageCrawler(self.config.BASE_URL, self.config)
        self.llm_formatter = LLMDataFormatter()
        self.form_filler = SmartFormFiller(self.config)
        self.interaction_explorer = InteractionExplorer(self.config)
        
        # Agent preparation
        self.agent_preparation = AgentPreparation(self.config)
        
        # Storage for agent data
        self.all_network_data = []
        self.all_interactions = []
        
        # Create output directory
        Path(self.config.OUTPUT_DIR).mkdir(exist_ok=True)
        Path(f"{self.config.OUTPUT_DIR}/screenshots").mkdir(exist_ok=True)
        
    async def explore(self):
        """Main exploration method"""
        print(f" Starting exploration of {self.config.BASE_URL}")
        print(f" Max pages: {self.config.MAX_PAGES}, Max depth: {self.config.MAX_DEPTH}")
        
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(
                headless=self.config.HEADLESS,
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            page = await context.new_page()
            
            # Setup monitors
            self._setup_page_monitors(page)
            
            # Start crawling from base URL
            self.page_crawler.add_to_queue(self.config.BASE_URL, 0)
            
            page_count = 0
            
            while not self.page_crawler.is_complete():
                if not self.page_crawler.url_queue:
                    break
                
                # Get next URL
                url, depth = self.page_crawler.url_queue.pop(0)
                
                if url in self.page_crawler.visited_urls:
                    continue
                
                page_count += 1
                print(f"\n [{page_count}/{self.config.MAX_PAGES}] Exploring: {url} (depth: {depth})")
                
                # Visit page
                page_data = await self._explore_page(page, url, depth)
                
                if page_data:
                    self.page_crawler.page_data.append(page_data)
                    self.page_crawler.visited_urls.add(url)
                    
                    # Save individual page data
                    if self.config.SAVE_RAW_DATA:
                        self._save_page_data(page_data, page_count)
                
                # Small delay between pages
                await asyncio.sleep(1)
            
            # Close browser
            await browser.close()
        
        # Generate final reports
        self._generate_reports()
        
        print(f"\n Exploration complete!")
        print(f" Total pages explored: {len(self.page_crawler.visited_urls)}")
        print(f" Results saved to: {self.config.OUTPUT_DIR}/")
    
    def _setup_page_monitors(self, page):
        """Setup all page monitors"""
        # Network monitoring
        page.on('request', self.network_monitor.on_request)
        page.on('response', self.network_monitor.on_response)
        
        # Console monitoring
        page.on('console', self.console_monitor.on_console)
    
    async def _explore_page(self, page, url: str, depth: int) -> dict:
        """Explore a single page with COMPLETE interaction exploration"""
        try:
            start_time = datetime.now()
            
            # Clear monitors
            self.network_monitor.clear()
            self.console_monitor.clear()
            self.interaction_tracker.clear()
            self.dom_mutation_observer.clear()
            
            # Navigate to page
            print(f"   Loading page...")
            await page.goto(url, wait_until='networkidle', timeout=self.config.TIMEOUT)
            
            # Wait a bit for dynamic content
            await asyncio.sleep(2)
            
            # Setup all monitors
            await self.interaction_tracker.setup_page_listeners(page)
            if self.config.CAPTURE_DOM_MUTATIONS:
                await self.dom_mutation_observer.setup_mutation_observer(page)
            
            # Extract page structure (COMPLETE extraction)
            print(f"   Extracting COMPLETE page structure...")
            structure = await self.dom_extractor.extract_page_structure(page)
            
            # Analyze text content
            text_analysis = {}
            if self.config.ANALYZE_TEXT_SEMANTICS or self.config.ANALYZE_TEXT_STRUCTURE:
                print(f"   Analyzing text semantically...")
                page_text = structure.get('all_text_content', {}).get('full_text', '')
                html_content = structure.get('full_html', '')
                text_analysis = self.text_analyzer.analyze_text(page_text, html_content)
            
            # Get page state hash
            state_hash = await self.page_crawler.get_page_state_hash(page)
            self.page_crawler.visited_states.add(state_hash)
            
            # Find interactive elements
            print(f"   Finding interactive elements...")
            interactive_elements = await self.page_crawler.find_interactive_elements(page)
            
            # EXPLORE ALL INTERACTIONS (NEW!)
            interaction_results = []
            if self.config.EXPLORE_ALL_BUTTONS or self.config.EXPLORE_ALL_LINKS:
                print(f"   Exploring ALL interactions...")
                interaction_results = await self.interaction_explorer.explore_all_interactions(
                    page, url, depth
                )
                # Store for agent preparation
                self.all_interactions.extend(interaction_results)
            
            # FILL AND SUBMIT ALL FORMS (NEW!)
            form_results = []
            if self.config.EXPLORE_ALL_FORMS:
                forms = structure.get('forms', [])
                if forms:
                    print(f"   Filling and submitting {len(forms)} forms...")
                    for i, form in enumerate(forms):
                        try:
                            result = await self.form_filler.fill_and_submit_form(page, form, i)
                            form_results.append(result)
                            
                            # Navigate back to the page
                            await page.goto(url, wait_until='networkidle')
                            await asyncio.sleep(1)
                        except Exception as e:
                            print(f"      Error with form {i}: {e}")
            
            # Extract links for further crawling
            print(f"   Extracting links...")
            links = await self.page_crawler.extract_links(page)
            
            # Add links to queue
            for link in links:
                self.page_crawler.add_to_queue(link, depth + 1)
            
            print(f"  ✓ Found {len(links)} new links")
            
            # Take screenshot
            screenshot_path = None
            if self.config.SAVE_SCREENSHOTS:
                screenshot_path = f"{self.config.OUTPUT_DIR}/screenshots/page_{len(self.page_crawler.visited_urls)}.png"
                Path(screenshot_path).parent.mkdir(exist_ok=True)
                await page.screenshot(path=screenshot_path, full_page=True)
            
            # Wait to capture mutations
            await asyncio.sleep(1)
            
            # Collect all monitoring data
            await self.interaction_tracker.collect_interactions(page)
            if self.config.CAPTURE_DOM_MUTATIONS:
                await self.dom_mutation_observer.collect_mutations(page)
            
            # Store network data for agent preparation
            network_summary = self.network_monitor.get_summary()
            self.all_network_data.extend(network_summary.get('requests', []))
            
            # Calculate load time
            load_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Compile COMPLETE page data
            page_data = {
                'url': url,
                'depth': depth,
                'timestamp': datetime.now().isoformat(),
                'load_time_ms': load_time,
                'state_hash': state_hash,
                'structure': structure,
                'text_analysis': text_analysis,  # NEW!
                'interactive_elements_count': len(interactive_elements),
                'interaction_results': interaction_results,  # NEW!
                'form_results': form_results,  # NEW!
                'links_found': len(links),
                'network': network_summary,
                'console': self.console_monitor.get_summary(),
                'interactions': self.interaction_tracker.get_summary(),
                'dom_mutations': self.dom_mutation_observer.get_summary() if self.config.CAPTURE_DOM_MUTATIONS else {},
                'screenshot': screenshot_path,
            }
            
            # Stop mutation observer
            if self.config.CAPTURE_DOM_MUTATIONS:
                await self.dom_mutation_observer.stop_observer(page)
            
            return page_data
            
        except Exception as e:
            print(f"   Error exploring page: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _simulate_interactions(self, page, elements):
        """Simulate some interactions with the page"""
        if not elements:
            return
        
        print(f"    Simulating interactions with {len(elements)} elements...")
        
        for elem in elements:
            try:
                # Find element by selector
                tag = elem.get('tag', '').lower()
                
                if tag == 'button':
                    # Find by text
                    text = elem.get('text', '')[:30]
                    if text:
                        button = page.get_by_role('button', name=text).first
                        if await button.is_visible():
                            self.interaction_tracker.add_interaction('simulated_click', {
                                'element': 'button',
                                'text': text
                            })
                            # Note: Not actually clicking to avoid navigation
                            # await button.click()
                            # await asyncio.sleep(self.config.CLICK_DELAY / 1000)
                
            except Exception as e:
                # Silent fail for interactions
                pass
    
    def _save_page_data(self, page_data: dict, page_num: int):
        """Save individual page data"""
        filename = f"{self.config.OUTPUT_DIR}/pages/page_{page_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        Path(filename).parent.mkdir(exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(page_data, f, indent=2)
    
    def _generate_reports(self):
        """Generate final reports including agent preparation data"""
        print("\n Generating reports...")
        
        all_pages = self.page_crawler.page_data
        
        # 1. Prepare agent data (NEW!)
        print("   Preparing agent data...")
        agent_data = self.agent_preparation.prepare_agent_data(
            all_pages,
            self.all_interactions,
            self.all_network_data
        )
        
        # Save agent data
        agent_data_path = f"{self.config.OUTPUT_DIR}/agent_data.json"
        with open(agent_data_path, 'w') as f:
            json.dump(agent_data, f, indent=2)
        print(f"  ✓ Agent data: {agent_data_path}")
        
        # 2. Save interaction graph (NEW!)
        if self.config.SAVE_INTERACTION_GRAPH:
            interaction_graph = self.interaction_explorer.get_interaction_graph()
            graph_path = f"{self.config.OUTPUT_DIR}/interaction_graph.json"
            with open(graph_path, 'w') as f:
                json.dump(interaction_graph, f, indent=2)
            print(f"  ✓ Interaction graph: {graph_path}")
        
        # 3. Save form filling summary (NEW!)
        form_summary = self.form_filler.get_summary()
        form_path = f"{self.config.OUTPUT_DIR}/form_filling_summary.json"
        with open(form_path, 'w') as f:
            json.dump(form_summary, f, indent=2)
        print(f"  ✓ Form filling summary: {form_path}")
        
        # 4. LLM-formatted markdown report
        markdown_report = self.llm_formatter.format_site_overview(all_pages)
        markdown_path = f"{self.config.OUTPUT_DIR}/llm_report.md"
        with open(markdown_path, 'w') as f:
            f.write(markdown_report)
        print(f"  ✓ LLM report (Markdown): {markdown_path}")
        
        # 5. Structured JSON for analysis
        analysis_data = self.llm_formatter.format_for_analysis(all_pages)
        
        # Add agent data to analysis
        analysis_data['agent_data'] = agent_data
        analysis_data['interaction_graph'] = interaction_graph if self.config.SAVE_INTERACTION_GRAPH else {}
        analysis_data['form_summary'] = form_summary
        
        json_path = f"{self.config.OUTPUT_DIR}/analysis_data.json"
        with open(json_path, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        print(f"  ✓ Analysis data (JSON): {json_path}")
        
        # 6. Crawl summary
        summary = self.page_crawler.get_summary()
        summary['total_interactions_explored'] = len(self.all_interactions)
        summary['total_forms_filled'] = len([f for f in form_summary.get('forms', []) if not f.get('errors')])
        
        summary_path = f"{self.config.OUTPUT_DIR}/crawl_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"  ✓ Crawl summary: {summary_path}")
        
        # 7. Individual page reports (markdown)
        pages_dir = f"{self.config.OUTPUT_DIR}/pages_markdown"
        Path(pages_dir).mkdir(exist_ok=True)
        for i, page in enumerate(all_pages, 1):
            page_md = self.llm_formatter.format_page_data(page)
            page_path = f"{pages_dir}/page_{i}.md"
            with open(page_path, 'w') as f:
                f.write(page_md)
        print(f"  ✓ Individual page reports: {pages_dir}/")
        
        # 8. Agent-specific reports (NEW!)
        if agent_data:
            # Action library
            if agent_data.get('action_library'):
                action_lib_path = f"{self.config.OUTPUT_DIR}/action_library.json"
                with open(action_lib_path, 'w') as f:
                    json.dump(agent_data['action_library'], f, indent=2)
                print(f"  ✓ Action library: {action_lib_path}")
            
            # API map
            if agent_data.get('api_map'):
                api_map_path = f"{self.config.OUTPUT_DIR}/api_map.json"
                with open(api_map_path, 'w') as f:
                    json.dump(agent_data['api_map'], f, indent=2)
                print(f"  ✓ API map: {api_map_path}")
            
            # State machine
            if agent_data.get('state_machine'):
                state_machine_path = f"{self.config.OUTPUT_DIR}/state_machine.json"
                with open(state_machine_path, 'w') as f:
                    json.dump(agent_data['state_machine'], f, indent=2)
                print(f"  ✓ State machine: {state_machine_path}")
            
            # User flows
            if agent_data.get('user_flows'):
                user_flows_path = f"{self.config.OUTPUT_DIR}/user_flows.json"
                with open(user_flows_path, 'w') as f:
                    json.dump(agent_data['user_flows'], f, indent=2)
                print(f"  ✓ User flows: {user_flows_path}")


async def main():
    """Main entry point"""
    explorer = WebsiteExplorer()
    await explorer.explore()


if __name__ == "__main__":
    asyncio.run(main())