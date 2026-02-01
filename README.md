# COLT - Comprehensive Observational Learning Tool 🔍

**COLT** is an advanced web application exploration and analysis framework that automatically maps, interacts with, and learns from web applications using Playwright. It provides deep insights into web app structure, behavior, and functionality - perfect for AI agents, testing, documentation, and reverse engineering.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🎯 What is COLT?

COLT is a intelligent web exploration framework that:

- **Crawls** entire web applications with depth control
- **Interacts** with every button, link, and form automatically
- **Learns** application structure, APIs, and user flows
- **Extracts** comprehensive semantic information from pages
- **Analyzes** text, content patterns, and business logic
- **Prepares** data optimized for LLM agents and AI assistants
- **Maps** complete API endpoints and network activity
- **Tracks** state changes and user journey flows
- **Generates** actionable reports and interaction graphs

## 🚀 Key Features

### 🌐 Complete Web Exploration

- **Smart Crawling**: Multi-level depth control with intelligent URL queue management
- **Full DOM Extraction**: Captures every element, attribute, and relationship
- **Interaction Testing**: Automatically clicks every button and follows every link
- **Form Intelligence**: Smart form filling with pattern recognition
- **State Tracking**: Monitors application state changes and transitions

### 🧠 AI-Ready Data Preparation

- **Action Library**: Complete catalog of all possible user actions
- **API Mapping**: Automatic endpoint discovery and schema extraction
- **Business Logic**: Identifies validation rules, workflows, and CRUD operations
- **User Flows**: Maps complete user journeys through the application
- **Component Hierarchy**: Builds reusable component trees

### 📊 Advanced Analysis

- **Text Analysis**: Semantic keyword extraction, entity recognition, sentiment indicators
- **Content Structure**: Analyzes headings, readability, and information architecture
- **Pattern Detection**: Finds emails, phone numbers, dates, and data patterns
- **Network Monitoring**: Captures all API calls, headers, and payloads
- **Accessibility Tree**: Extracts ARIA labels and accessibility information

### 💾 Memory Layer

- **Product Context Storage**: Persistent memory for learned application knowledge
- **Terminology Management**: Stores domain-specific terms and definitions
- **Workflow Documentation**: Captures business processes and workflows
- **LLM Context Generation**: Formats all data for optimal AI consumption

### 📸 Comprehensive Monitoring

- **Network Monitor**: All HTTP requests/responses with timing
- **Console Monitor**: JavaScript console logs and errors
- **DOM Mutation Observer**: Real-time DOM changes tracking
- **Interaction Tracker**: User interaction simulation and recording
- **Screenshot Capture**: Before/after screenshots for every interaction

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Node.js (for Playwright)

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd colt

# Install Python dependencies
pip install playwright beautifulsoup4

# Install Playwright browsers
python -m playwright install chromium

# Test the setup
python test.py
```

### Dependencies

```
playwright>=1.40.0
beautifulsoup4>=4.12.0
```

## 🎮 Quick Start

### Basic Usage

1. **Configure your target application** in [config.py](config.py):

```python
class Config:
    BASE_URL = "http://localhost:3000"  # Your web app URL
    MAX_PAGES = 50
    MAX_DEPTH = 5
    HEADLESS = False  # Set True for production
```

2. **Run the explorer**:

```bash
# Using the shell script
./run.sh

# Or directly with Python
python explorer.py
```

3. **View results** in the `output/` directory:
   - `llm_report.md` - Human-readable markdown report
   - `agent_data.json` - AI-ready action library
   - `api_map.json` - Complete API endpoint map
   - `interaction_graph.json` - Visual interaction flow
   - `form_filling_summary.json` - Form analysis
   - Screenshots in `screenshots/` folder

### Using the Memory Layer

```bash
# Learn from exploration data
python -m src.memory.memory_layer my_product learn

# Export context for LLM
python -m src.memory.memory_layer my_product export

# View summary
python -m src.memory.memory_layer my_product summary
```

Or programmatically:

```python
from src.memory.memory_layer import MemoryLayer

# Create memory for your product
memory = MemoryLayer("my_app", exploration_dir="output")

# Add product context
memory.add_product_context(
    description="E-commerce platform for selling widgets",
    product_type="Web Application",
    domain="E-commerce"
)

# Add terminology
memory.add_terminology("SKU", "Stock Keeping Unit - unique product identifier")

# Learn from exploration
memory.learn_from_exploration()

# Get LLM-ready context
context = memory.get_context_for_llm()
print(context)
```

## ⚙️ Configuration

COLT is highly configurable via [config.py](config.py). Key settings:

### Exploration Settings

```python
MAX_PAGES = 50              # Maximum pages to explore
MAX_DEPTH = 5               # Maximum crawl depth
TIMEOUT = 30000             # Page load timeout (ms)
HEADLESS = False            # Browser visibility
BROWSER_TYPE = "chromium"   # chromium, firefox, or webkit
```

### Interaction Exploration

```python
EXPLORE_ALL_BUTTONS = True           # Click every button
EXPLORE_ALL_LINKS = True             # Follow every link
EXPLORE_ALL_FORMS = True             # Fill and submit every form
MAX_INTERACTIONS_PER_PAGE = 20       # Interaction limit per page
INTERACTION_WAIT_TIME = 2000         # Wait between interactions (ms)
```

### Monitoring

```python
CAPTURE_SCREENSHOTS = True
CAPTURE_NETWORK = True
CAPTURE_CONSOLE = True
CAPTURE_DOM_MUTATIONS = True
CAPTURE_SCREENSHOTS_AFTER_INTERACTIONS = True
```

### Text Analysis

```python
ANALYZE_TEXT_SEMANTICS = True    # Keywords, entities, sentiment
ANALYZE_TEXT_STRUCTURE = True    # Headings, hierarchy, readability
EXTRACT_DATA_PATTERNS = True     # Phone numbers, emails, dates
```

### Form Filling

```python
FORM_FILL_DATA = {
    'name': ['John Doe', 'Jane Smith'],
    'email': ['test@example.com'],
    'password': ['TestPass123!'],
    # ... extensive pattern library
}

SUBMIT_FORMS = True
WAIT_AFTER_SUBMIT = 3000
```

### Agent Preparation

```python
BUILD_ACTION_LIBRARY = True       # Map UI actions to results
MAP_API_ENDPOINTS = True          # Create complete API map
BUILD_INTERACTION_GRAPH = True    # Visual interaction flow
DETECT_AUTH_FLOWS = True          # Identify login/auth
DETECT_CRUD_OPERATIONS = True     # Find Create/Read/Update/Delete
EXTRACT_BUSINESS_LOGIC = True     # Business rules extraction
```

## 📁 Project Structure

```
colt/
├── config.py                      # Main configuration
├── explorer.py                    # Main orchestrator
├── test.py                        # Component tests
├── run.sh                         # Quick start script
│
├── src/
│   ├── analyzers/
│   │   ├── agent_preparation.py   # AI agent data preparation
│   │   └── text_analyzer.py       # Semantic text analysis
│   │
│   ├── extractors/
│   │   └── dom_extractor.py       # Complete DOM extraction
│   │
│   ├── memory/
│   │   └── memory_layer.py        # Persistent product memory
│   │
│   ├── monitors/
│   │   ├── console_monitor.py     # JavaScript console capture
│   │   ├── dom_mutation_observer.py  # DOM changes tracking
│   │   ├── interaction_tracker.py    # Interaction recording
│   │   └── network_monitor.py        # Network traffic capture
│   │
│   └── utils/
│       ├── interaction_explorer.py   # Interactive element explorer
│       ├── llm_formatter.py          # LLM-optimized formatting
│       ├── page_crawler.py           # Smart page crawler
│       └── smart_form_filler.py      # Intelligent form filling
│
└── output/                        # Generated reports (created on run)
    ├── llm_report.md
    ├── agent_data.json
    ├── api_map.json
    ├── interaction_graph.json
    ├── form_filling_summary.json
    ├── action_library.json
    ├── state_machine.json
    ├── user_flows.json
    └── screenshots/
```

## 🎯 Use Cases

### 1. AI Agent Training

Prepare comprehensive data for training AI agents to interact with web applications:

```python
# Explore and prepare agent data
explorer = WebsiteExplorer()
await explorer.explore()

# Load agent data
with open('output/agent_data.json') as f:
    agent_data = json.load(f)

# Now feed to your LLM/agent
```

### 2. Automated Testing

Generate test scenarios and interaction maps:

- Test all buttons and links
- Validate all forms
- Verify state transitions
- Check API responses

### 3. Documentation Generation

Auto-document your web application:

- Complete sitemap
- Form specifications
- API endpoint catalog
- User flow diagrams

### 4. Security Analysis

Identify potential security issues:

- Exposed API endpoints
- Form validation gaps
- Authentication flows
- Network traffic analysis

### 5. Reverse Engineering

Understand legacy applications:

- Component hierarchy
- Business logic extraction
- API schema discovery
- User journey mapping

## 📊 Output Files

### For Humans 👤

- **`llm_report.md`** - Comprehensive markdown report with all findings
- **`pages_markdown/*.md`** - Individual page reports
- **`screenshots/*.png`** - Visual captures of every interaction

### For AI Agents 🤖

- **`agent_data.json`** - Complete action library with preconditions/postconditions
- **`action_library.json`** - All possible UI actions
- **`api_map.json`** - API endpoints with methods and patterns
- **`state_machine.json`** - State transitions graph
- **`user_flows.json`** - Complete user journey flows
- **`interaction_graph.json`** - Visual interaction map

### For Analysis 📈

- **`analysis_data.json`** - Structured data for further processing
- **`crawl_summary.json`** - High-level statistics
- **`form_filling_summary.json`** - Form interaction results
- **`pages/*.json`** - Raw per-page data

## 🔧 Advanced Usage

### Custom Exploration Patterns

```python
from explorer import WebsiteExplorer
from config import Config

# Custom configuration
config = Config()
config.BASE_URL = "https://your-app.com"
config.MAX_PAGES = 100
config.HEADLESS = True

# Custom ignore patterns
config.IGNORE_PATTERNS.append(r'.*admin.*')
config.IGNORE_PATTERNS.append(r'.*analytics.*')

# Run exploration
explorer = WebsiteExplorer(config)
await explorer.explore()
```

### Programmatic Memory Management

```python
from src.memory.memory_layer import MemoryLayer

memory = MemoryLayer("my_product")

# Add business context
memory.add_product_context(
    description="CRM for managing customer relationships",
    product_type="SaaS Platform",
    domain="Business Software"
)

# Add workflows
memory.add_workflow("Lead Creation", [
    "Navigate to Leads page",
    "Click 'New Lead' button",
    "Fill contact information",
    "Assign to sales rep",
    "Save lead"
])

# Add business rules
memory.add_business_rule(
    "Lead Assignment",
    "Leads are automatically assigned to reps based on territory"
)

# Learn from exploration
memory.learn_from_exploration()

# Export for AI
memory.export_context("context_for_ai.txt")
```

### Selective Monitoring

```python
from config import Config

config = Config()

# Enable only specific monitors
config.CAPTURE_NETWORK = True
config.CAPTURE_SCREENSHOTS = False
config.CAPTURE_DOM_MUTATIONS = False

# Enable only API endpoint mapping
config.MAP_API_ENDPOINTS = True
config.BUILD_ACTION_LIBRARY = False
config.BUILD_INTERACTION_GRAPH = False
```

## 🐛 Troubleshooting

### Playwright Installation Issues

```bash
# Reinstall Playwright
pip uninstall playwright
pip install playwright
python -m playwright install chromium
```

### Permission Errors

```bash
# Make run.sh executable
chmod +x run.sh
```

### Browser Not Found

```bash
# Install specific browser
python -m playwright install chromium
```

### Memory Issues with Large Sites

```python
# Reduce exploration scope
config.MAX_PAGES = 20
config.MAX_DEPTH = 3
config.MAX_INTERACTIONS_PER_PAGE = 10
```

### Timeout Issues

```python
# Increase timeouts
config.TIMEOUT = 60000
config.INTERACTION_WAIT_TIME = 3000
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Multi-browser support (Firefox, WebKit)
- [ ] Distributed crawling for large sites
- [ ] Machine learning for smarter form filling
- [ ] Visual regression testing
- [ ] Performance monitoring
- [ ] Accessibility scoring
- [ ] Docker containerization
- [ ] API for programmatic control
- [ ] Real-time dashboard
- [ ] Plugin system for custom extractors

## 📜 License

MIT License - Copyright (c) 2026 Vipul Sharma

See [LICENSE.txt](LICENSE.txt) for full details.

## 🙏 Acknowledgments

Built with:

- [Playwright](https://playwright.dev/) - Browser automation
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
- Python 3.8+ - Core language

## 📞 Support

For issues, questions, or contributions:

- Open an issue on GitHub
- Check the troubleshooting section
- Review the configuration options

## 🗺️ Roadmap

### v1.1 (Planned)

- [ ] WebSocket monitoring
- [ ] GraphQL query extraction
- [ ] Enhanced component detection
- [ ] Video recording of interactions

### v1.2 (Future)

- [ ] Cloud deployment options
- [ ] Collaborative exploration sessions
- [ ] Integration with testing frameworks
- [ ] Advanced AI agent integration

---

**Made with ❤️ for web exploration and AI agent training**

_COLT - Because every web application has stories to tell._
