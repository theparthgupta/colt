"""
Test script to verify all components are working
"""
import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print(" Testing imports...")
    
    try:
        from config import Config
        print("  ✓ Config imported")
        
        from src.monitors.network_monitor import NetworkMonitor
        print("  ✓ NetworkMonitor imported")
        
        from src.monitors.console_monitor import ConsoleMonitor
        print("  ✓ ConsoleMonitor imported")
        
        from src.monitors.interaction_tracker import InteractionTracker
        print("  ✓ InteractionTracker imported")
        
        from src.extractors.dom_extractor import DOMExtractor
        print("  ✓ DOMExtractor imported")
        
        from src.utils.page_crawler import PageCrawler
        print("  ✓ PageCrawler imported")
        
        from src.utils.llm_formatter import LLMDataFormatter
        print("  ✓ LLMDataFormatter imported")
        
        print("\n All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n Import failed: {e}")
        return False

def test_dependencies():
    """Test that required dependencies are available"""
    print("\n Testing dependencies...")
    
    try:
        import playwright
        print("  ✓ Playwright available")
        
        from bs4 import BeautifulSoup
        print("  ✓ BeautifulSoup available")
        
        print("\n All dependencies available!")
        return True
        
    except Exception as e:
        print(f"\n Dependency missing: {e}")
        return False

def test_config():
    """Test configuration"""
    print("\n Testing configuration...")
    
    try:
        from config import Config
        
        config = Config()
        
        assert config.BASE_URL == "http://localhost:3000"
        print("  ✓ BASE_URL configured")
        
        assert config.MAX_PAGES > 0
        print("  ✓ MAX_PAGES configured")
        
        assert config.MAX_DEPTH > 0
        print("  ✓ MAX_DEPTH configured")
        
        assert config.OUTPUT_DIR == "output"
        print("  ✓ OUTPUT_DIR configured")
        
        print("\n Configuration valid!")
        return True
        
    except Exception as e:
        print(f"\n Configuration test failed: {e}")
        return False

def test_components():
    """Test individual components"""
    print("\n Testing components...")
    
    try:
        from src.monitors.network_monitor import NetworkMonitor
        from src.monitors.console_monitor import ConsoleMonitor
        from src.utils.llm_formatter import LLMDataFormatter
        
        # Test NetworkMonitor
        nm = NetworkMonitor()
        summary = nm.get_summary()
        assert 'total_requests' in summary
        print("  ✓ NetworkMonitor works")
        
        # Test ConsoleMonitor
        cm = ConsoleMonitor()
        summary = cm.get_summary()
        assert 'total_messages' in summary
        print("  ✓ ConsoleMonitor works")
        
        # Test LLMDataFormatter
        formatter = LLMDataFormatter()
        test_data = {
            'url': 'test',
            'structure': {'title': 'Test Page'},
            'timestamp': '2024-01-01'
        }
        result = formatter.format_page_data(test_data)
        assert '# Page:' in result
        print("  ✓ LLMDataFormatter works")
        
        print("\n All components working!")
        return True
        
    except Exception as e:
        print(f"\n Component test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_directory_structure():
    """Test that all directories exist"""
    print("\n Testing directory structure...")
    
    base = Path(".")
    
    required_dirs = [
        base / "src" / "monitors",
        base / "src" / "extractors",
        base / "src" / "utils",
    ]
    
    required_files = [
        base / "config.py",
        base / "explorer.py",
        base / "demo.py",
        base / "analyze.py",
        base / "README.md",
    ]
    
    all_good = True
    
    for dir_path in required_dirs:
        if dir_path.exists():
            print(f"  ✓ {dir_path.name}/ exists")
        else:
            print(f"   {dir_path.name}/ missing")
            all_good = False
    
    for file_path in required_files:
        if file_path.exists():
            print(f"  ✓ {file_path.name} exists")
        else:
            print(f"   {file_path.name} missing")
            all_good = False
    
    if all_good:
        print("\n Directory structure complete!")
    else:
        print("\n Some files/directories missing!")
    
    return all_good

def main():
    """Run all tests"""
    print("=" * 60)
    print("Website Explorer - Component Tests")
    print("=" * 60)
    
    results = []
    
    results.append(("Directory Structure", test_directory_structure()))
    results.append(("Dependencies", test_dependencies()))
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Components", test_components()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for name, result in results:
        status = " PASS" if result else " FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n All tests passed! Ready to explore.")
        print("\nNext steps:")
        print("  1. Make sure localhost:3000 is running")
        print("  2. Run: python demo.py (quick test)")
        print("  3. Run: python explorer.py (full exploration)")
    else:
        print("\n  Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())