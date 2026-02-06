# COLT - Complete Observation and Learning Tool

<img width="1024" height="768" alt="Blue and White Modern Clean Sign-up Process Flowchart" src="https://github.com/user-attachments/assets/257e2374-5676-4095-bd4d-34387ff2bcf7" />

**COLT** is a sophisticated web application explorer and AI-powered task automation platform. It deeply analyzes web applications and enables LLM agents to understand and interact with them through natural language.

## Features

### 🔍 **Deep Web Exploration**
- Comprehensive crawling of web applications
- Complete DOM structure extraction
- Network monitoring (API calls, requests/responses)
- Form detection and intelligent filling
- Interactive element discovery (buttons, links, forms)
- Browser storage extraction (localStorage, sessionStorage, cookies)
- Console logging and error tracking
- DOM mutation observation

### 🤖 **LLM-Powered Task Planning**
- Convert natural language prompts to executable action plans
- Supports OpenAI GPT-4, Anthropic Claude, and local models
- Context-aware planning using exploration data
- Automatic validation and confidence scoring
- Interactive CLI for task planning

### ⚡ **Task Execution** ⭐ NEW
- Execute LLM-generated plans in real browsers
- Automated form filling, clicking, navigation
- Screenshot capture at each step
- Outcome verification and error handling
- Detailed execution reports

### 📊 **Agent-Ready Output**
- Action library (all possible UI actions)
- API endpoint mapping with CRUD detection
- State machine and user flow graphs
- Validation rules and business logic extraction
- Authentication flow detection
- Component hierarchy mapping
- Multiple output formats (JSON, Markdown)

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/colt.git
cd colt

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Explore Your Application

```bash
# Update config.py with your app's URL
# BASE_URL = "http://localhost:3000"

# Run the explorer
python explorer.py
```

This generates comprehensive exploration data in `output/`.

### 3. Plan Tasks with Natural Language

```bash
# Set up your LLM API key
export OPENAI_API_KEY="sk-..."
# or
export ANTHROPIC_API_KEY="sk-ant-..."

# Start the interactive planner
python planner_cli.py
```

Then describe tasks in plain English:
```
> Submit the contact form
> Login with test credentials
> Create a new user account
> Add product to cart and checkout
```

### 4. Execute the Plan

```bash
# Execute the generated plan
python execute_plan.py output/generated_plans/plan_submit_the_contact_form.json

# Or with options
python execute_plan.py plan.json --show-plan --headless
```

The executor will:
- ✅ Open the browser
- ✅ Execute each step (navigate, fill forms, click buttons)
- ✅ Verify expected outcomes
- ✅ Capture screenshots
- ✅ Generate execution report

## Documentation

- **[Quick Start Guide](QUICKSTART_PLANNER.md)** - Get started in 5 minutes
- **[Planner Guide](PLANNER_GUIDE.md)** - Complete guide for the LLM task planner
- **[Executor Guide](EXECUTOR_GUIDE.md)** - Complete guide for task execution ⭐ NEW
- **[Configuration](config.py)** - All configuration options

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              Natural Language Prompt                 │
│           "Submit the contact form"                  │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│            LLM Task Planner                          │
│  • Context building from exploration data            │
│  • LLM-powered plan generation                       │
│  • Plan validation and optimization                  │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│           Structured Action Plan                     │
│  • Step-by-step instructions                        │
│  • Selectors, URLs, form data                       │
│  • Expected outcomes & verification                  │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│          Task Executor (NEW)                         │
│  • Executes plans in real browser                   │
│  • Handles navigation, clicks, forms                │
│  • Verifies outcomes automatically                  │
│  • Captures screenshots & reports                   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│         Exploration Engine                           │
│  • Playwright browser automation                     │
│  • Comprehensive data extraction                     │
│  • Multi-format output generation                    │
└─────────────────────────────────────────────────────┘
```

## Project Structure

```
colt/
├── explorer.py              # Main exploration orchestrator
├── planner_cli.py          # Task planner CLI
├── execute_plan.py         # Plan executor CLI ⭐ NEW
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── run.sh                  # Quick start script
├── test.py                 # Test suite for explorer
├── test_planner.py        # Test suite for planner
├── test_executor.py       # Test suite for executor ⭐ NEW
│
├── src/
│   ├── analyzers/          # Text analysis, agent preparation
│   ├── extractors/         # DOM extraction
│   ├── memory/            # Memory management (future)
│   ├── monitors/          # Network, console, interactions, DOM
│   ├── planner/           # LLM task planner
│   │   ├── context_builder.py
│   │   ├── llm_client.py
│   │   └── task_planner.py
│   ├── executor/          # Task executor ⭐ NEW
│   │   ├── task_executor.py
│   │   ├── action_handlers.py
│   │   └── verification.py
│   └── utils/             # Crawling, forms, interactions, formatting
│
└── output/                # Generated data
    ├── agent_data.json
    ├── action_library.json
    ├── api_map.json
    ├── state_machine.json
    ├── user_flows.json
    ├── generated_plans/    # LLM-generated plans
    ├── execution_screenshots/  # Step-by-step screenshots ⭐ NEW
    └── execution_reports/     # Execution results ⭐ NEW
```
