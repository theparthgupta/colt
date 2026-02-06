"""
Configuration settings for the website explorer
"""

class Config:
    # Target website settings
    BASE_URL = "http://localhost:3000"  # Configure this to your application URL
    
    # Crawler settings
    MAX_PAGES = 50  # Maximum number of pages to explore
    MAX_DEPTH = 5   # Maximum depth of exploration
    TIMEOUT = 30000  # Page load timeout in milliseconds
    
    # INTERACTION EXPLORATION SETTINGS
    EXPLORE_ALL_BUTTONS = True  # Click and explore EVERY button
    EXPLORE_ALL_LINKS = True    # Follow ALL links (not just for crawling)
    EXPLORE_ALL_FORMS = True    # Fill and submit EVERY form
    MAX_INTERACTIONS_PER_PAGE = 20  # Max interactions to try per page
    INTERACTION_WAIT_TIME = 2000  # Wait after each interaction (ms)
    
    # Exploration settings
    CLICK_DELAY = 1000  # Delay between clicks in milliseconds
    SCROLL_DELAY = 500  # Delay for scrolling in milliseconds
    
    # Monitoring settings
    CAPTURE_SCREENSHOTS = True
    CAPTURE_NETWORK = True
    CAPTURE_CONSOLE = True
    CAPTURE_DOM_MUTATIONS = True
    CAPTURE_SCREENSHOTS_AFTER_INTERACTIONS = True  # Screenshot after each interaction
    
    # TEXT ANALYSIS SETTINGS
    ANALYZE_TEXT_SEMANTICS = True  # Extract keywords, entities, sentiment
    ANALYZE_TEXT_STRUCTURE = True  # Analyze headings, hierarchy, readability
    EXTRACT_DATA_PATTERNS = True   # Find phone numbers, emails, dates, etc.
    
    # Output settings
    OUTPUT_DIR = "output"
    SAVE_RAW_DATA = True
    SAVE_SCREENSHOTS = True
    SAVE_INTERACTION_GRAPH = True  # Save visual interaction flow
    SAVE_STATE_TRANSITIONS = True  # Track state changes
    
    # Browser settings
    HEADLESS = True  # Set to True for production
    BROWSER_TYPE = "chromium"  # chromium, firefox, or webkit
    SLOW_MO = 500  # Slow down browser by N ms (helps see what's happening)
    
    # Element interaction settings
    INTERACTIVE_SELECTORS = [
        'a[href]',
        'button:not([disabled])',
        'input[type="submit"]',
        'input[type="button"]',
        '[role="button"]',
        '[onclick]',
        'select',
        'input[type="checkbox"]',
        'input[type="radio"]',
    ]
    
    # Ignore patterns (URLs to skip)
    IGNORE_PATTERNS = [
        r'.*\.pdf$',
        r'.*\.zip$',
        r'.*\.exe$',
        r'.*logout.*',
        r'.*signout.*',
        r'.*delete.*',  # Avoid destructive actions
        r'.*remove.*',
    ]
    
    # ========================================
    # SMART FORM FILLING CONFIGURATION
    # ========================================
    
    # Default test data for different input types
    FORM_FILL_DATA = {
        # Text inputs by name/id patterns
        'name': ['John Doe', 'Jane Smith', 'Test User'],
        'username': ['testuser123', 'john_doe', 'jane_smith'],
        'email': ['test@example.com', 'user@test.com', 'john.doe@example.org'],
        'password': ['TestPass123!', 'SecureP@ssw0rd', 'MyPassword123'],
        'phone': ['555-123-4567', '(555) 987-6543', '+1-555-123-4567'],
        'address': ['123 Main St', '456 Oak Avenue', '789 Pine Road'],
        'city': ['New York', 'Los Angeles', 'Chicago'],
        'zip': ['12345', '90210', '60601'],
        'state': ['NY', 'CA', 'IL'],
        'country': ['USA', 'United States', 'US'],
        'company': ['Acme Corp', 'Test Company', 'Example Inc'],
        'title': ['Software Engineer', 'Product Manager', 'Designer'],
        'message': ['This is a test message', 'Hello, testing the form', 'Sample feedback'],
        'comment': ['Great product!', 'This is a test comment', 'Testing feedback'],
        'description': ['This is a test description', 'Sample description text', 'Testing'],
        'url': ['https://example.com', 'https://test.com', 'https://website.org'],
        'search': ['test query', 'search term', 'example search'],
        'first_name': ['John', 'Jane', 'Test'],
        'last_name': ['Doe', 'Smith', 'User'],
        'age': ['25', '30', '35'],
        'date': ['2024-01-15', '2024-06-30', '2024-12-25'],
        'time': ['10:30', '14:45', '09:00'],
        'number': ['42', '100', '999'],
        'amount': ['100.00', '250.50', '1000.00'],
        'quantity': ['1', '5', '10'],
        'card': ['4111111111111111', '5500000000000004'],  # Test card numbers
        'cvv': ['123', '456', '789'],
        'code': ['ABC123', 'XYZ789', 'TEST001'],
    }
    
    # Fallback data by input type
    FORM_FILL_BY_TYPE = {
        'text': 'Test input text',
        'email': 'test@example.com',
        'password': 'TestPassword123!',
        'tel': '555-123-4567',
        'number': '42',
        'url': 'https://example.com',
        'date': '2024-01-15',
        'time': '10:30',
        'datetime-local': '2024-01-15T10:30',
        'month': '2024-01',
        'week': '2024-W03',
        'color': '#FF5733',
        'range': '50',
        'search': 'test search',
    }
    
    # Select/dropdown options strategy
    SELECT_STRATEGY = 'first'  # Options: 'first', 'random', 'all'
    
    # Checkbox/radio strategy
    CHECKBOX_STRATEGY = 'check_all'  # Options: 'check_all', 'random', 'first'
    RADIO_STRATEGY = 'first'  # Options: 'first', 'random', 'last'
    
    # Textarea default
    TEXTAREA_DEFAULT = 'This is a test message.\nTesting the textarea field.\nMultiple lines of text.'
    
    # Form submission settings
    SUBMIT_FORMS = True  # Actually submit forms
    WAIT_AFTER_SUBMIT = 3000  # Wait time after form submission (ms)
    CAPTURE_FORM_RESPONSES = True  # Capture what happens after submission
    
    # Smart field detection patterns (regex)
    FIELD_PATTERNS = {
        'email': r'.*(email|e-mail|mail).*',
        'password': r'.*(pass|password|pwd).*',
        'phone': r'.*(phone|tel|mobile|cell).*',
        'name': r'.*(name|full.?name|first.?name|last.?name).*',
        'address': r'.*(address|street|addr).*',
        'city': r'.*(city|town).*',
        'zip': r'.*(zip|postal|post.?code).*',
        'state': r'.*(state|province|region).*',
        'country': r'.*(country|nation).*',
        'date': r'.*(date|dob|birth).*',
        'url': r'.*(url|website|link).*',
        'search': r'.*(search|query|find).*',
        'card': r'.*(card|credit|payment).*',
        'cvv': r'.*(cvv|cvc|security.?code).*',
        'amount': r'.*(amount|price|cost|total).*',
    }
    
    # ARIA role-based filling
    ARIA_BASED_FILL = True
    
    # Validation handling
    RESPECT_PATTERN_VALIDATION = True  # Try to match pattern attribute
    RESPECT_MIN_MAX = True  # Respect min/max for numbers/dates
    RESPECT_REQUIRED = True  # Always fill required fields
    
    # Multi-step form handling
    HANDLE_MULTI_STEP_FORMS = True  # Continue through multi-step forms
    MAX_FORM_STEPS = 5  # Maximum steps to go through
    
    # ========================================
    # STATE TRACKING & AGENT PREPARATION
    # ========================================
    
    # Track application state
    TRACK_APP_STATE = True  # Track state variables, routes, etc.
    TRACK_USER_FLOWS = True  # Build user flow graphs
    TRACK_STATE_TRANSITIONS = True  # Record all state changes
    
    # Component/element tracking
    IDENTIFY_COMPONENTS = True  # Identify reusable components
    MAP_COMPONENT_HIERARCHY = True  # Build component tree
    
    # API mapping for agents
    MAP_API_ENDPOINTS = True  # Create complete API map
    EXTRACT_API_SCHEMAS = True  # Extract request/response schemas
    BUILD_ACTION_LIBRARY = True  # Map UI actions to API calls
    
    # Context for LLM agents
    BUILD_INTERACTION_GRAPH = True  # Visual graph of all interactions
    CREATE_ACTION_LIBRARY = True  # Library of all possible actions
    EXTRACT_BUSINESS_LOGIC = True  # Identify business rules/logic
    
    # Advanced analysis
    DETECT_AUTH_FLOWS = True  # Identify login/auth patterns
    DETECT_CRUD_OPERATIONS = True  # Identify Create/Read/Update/Delete
    DETECT_VALIDATION_RULES = True  # Extract validation patterns
    DETECT_ERROR_PATTERNS = True  # Common error scenarios

    # ========================================
    # LLM TASK PLANNER CONFIGURATION
    # ========================================

    # LLM Provider settings
    LLM_PROVIDER = "openai"  # Options: "openai", "anthropic", "local"
    LLM_MODEL = None  # None = use provider default, or specify: "gpt-4-turbo-preview", "claude-3-5-sonnet-20241022", etc.
    LLM_API_KEY = None  # None = use environment variables (OPENAI_API_KEY or ANTHROPIC_API_KEY)
    LLM_BASE_URL = None  # For local models (e.g., "http://localhost:11434" for Ollama)

    # Generation parameters
    LLM_TEMPERATURE = 0.7  # 0.0 = deterministic, 1.0 = creative
    LLM_MAX_TOKENS = 2000  # Maximum tokens for LLM response
    LLM_CONTEXT_WINDOW = 8000  # Maximum context tokens to send to LLM

    # Planning settings
    PLANNER_MAX_RELEVANT_ACTIONS = 10  # Max actions to include in context
    PLANNER_MAX_RELEVANT_PAGES = 5  # Max pages to include in context
    PLANNER_MAX_RELEVANT_FLOWS = 3  # Max user flows to include in context
    PLANNER_MAX_API_ENDPOINTS = 5  # Max API endpoints to include in context

    # Output settings
    SAVE_GENERATED_PLANS = True  # Save plans to output/generated_plans/
    AUTO_VALIDATE_PLANS = True  # Automatically validate plans against action library