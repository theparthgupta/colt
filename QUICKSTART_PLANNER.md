# COLT Task Planner - Quick Start Guide

## What is it?

The COLT Task Planner converts natural language like **"Submit the contact form"** into step-by-step action plans that can be executed by automation tools.

## Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Playwright browsers
playwright install chromium

# 3. Set your API key (choose one)

# Option A: OpenAI
export OPENAI_API_KEY="sk-..."

# Option B: Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Option C: Local (Ollama) - no API key needed
# Just install Ollama from https://ollama.ai
```

## Usage in 3 Steps

### Step 1: Explore Your App

```bash
# Update BASE_URL in config.py to point to your app
# Then run:
python explorer.py
```

This generates the knowledge base in `output/`.

### Step 2: Plan a Task

**Interactive mode (recommended):**
```bash
python planner_cli.py
```

Then type natural language prompts:
```
> Submit the contact form
> Login with username admin
> Create a new user account
```

**Single task mode:**
```bash
python planner_cli.py "Submit the contact form"
```

### Step 3: Review the Plan

The planner outputs a detailed plan:

```
ACTION PLAN
===========================================================

Task: Submit contact form with test data

Steps:

1. [NAVIGATE] Navigate to contact page
   URL: http://localhost:3000/contact
   Expected: Contact form is displayed

2. [FILL_FORM] Fill out the contact form
   Form data: {"name": "Test User", "email": "test@example.com"}
   Expected: All fields are filled

3. [CLICK] Submit the form
   Selector: button[type="submit"]
   Expected: Form is submitted

4. [VERIFY] Verify submission
   Expected: Confirmation message appears

Confidence: 85.0%
```

## Configuration

Edit `config.py`:

```python
# Which LLM to use
LLM_PROVIDER = "openai"  # or "anthropic" or "local"

# Temperature (0 = deterministic, 1 = creative)
LLM_TEMPERATURE = 0.7

# How many relevant actions to include
PLANNER_MAX_RELEVANT_ACTIONS = 10
```

## Example Prompts

Try these:

```
Submit the contact form
Login with test credentials
Search for "laptop" in the product catalog
Create a new user account
Add item to cart and checkout
Update my profile information
Delete the test user
Navigate to the settings page
```

## What's Next?

Currently, the planner **generates plans** but doesn't execute them.

**Coming soon:** The Task Executor will actually run these plans in the browser!

## Troubleshooting

**"Exploration data not loaded"**
- Run `python explorer.py` first

**"API key not found"**
- Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`

**"Low confidence plan"**
- Be more specific in your prompt
- Make sure your app was fully explored

## Need Help?

- Full guide: See `PLANNER_GUIDE.md`
- Main README: See `README.md`
- Run tests: `python test_planner.py`
