"""
Smart Form Filler - Intelligently fills forms based on field patterns
"""
import re
import random
from typing import Dict, Any, List, Optional


class SmartFormFiller:
    def __init__(self, config):
        self.config = config
        self.filled_forms = []
        
    def _match_field_pattern(self, field_name: str, field_id: str, placeholder: str, aria_label: str) -> Optional[str]:
        """Match field to a pattern and return appropriate test data"""
        # Combine all identifiers
        combined = f"{field_name} {field_id} {placeholder} {aria_label}".lower()
        
        # Check against patterns
        for pattern_type, pattern_regex in self.config.FIELD_PATTERNS.items():
            if re.search(pattern_regex, combined, re.IGNORECASE):
                if pattern_type in self.config.FORM_FILL_DATA:
                    return random.choice(self.config.FORM_FILL_DATA[pattern_type])
        
        # Check direct name matches
        name_lower = field_name.lower() if field_name else ''
        for key, values in self.config.FORM_FILL_DATA.items():
            if key in name_lower:
                return random.choice(values)
        
        return None
    
    def _get_value_for_input(self, input_info: Dict[str, Any]) -> str:
        """Get appropriate value for an input field"""
        field_type = input_info.get('type', 'text')
        field_name = input_info.get('name', '')
        field_id = input_info.get('id', '')
        placeholder = input_info.get('placeholder', '')
        aria_label = input_info.get('aria-label', '')
        pattern = input_info.get('pattern', '')
        min_val = input_info.get('min', '')
        max_val = input_info.get('max', '')
        
        # Try pattern matching first
        matched_value = self._match_field_pattern(field_name, field_id, placeholder, aria_label)
        if matched_value:
            # Validate against pattern if required
            if self.config.RESPECT_PATTERN_VALIDATION and pattern:
                if re.match(pattern, matched_value):
                    return matched_value
            else:
                return matched_value
        
        # Fall back to type-based filling
        if field_type in self.config.FORM_FILL_BY_TYPE:
            value = self.config.FORM_FILL_BY_TYPE[field_type]
            
            # Handle min/max for numbers
            if self.config.RESPECT_MIN_MAX and field_type == 'number':
                if min_val and max_val:
                    try:
                        return str(random.randint(int(min_val), int(max_val)))
                    except:
                        pass
            
            return value
        
        # Ultimate fallback
        return 'test_value'
    
    async def fill_and_submit_form(self, page, form_info: Dict[str, Any], form_index: int) -> Dict[str, Any]:
        """Fill and submit a single form"""
        result = {
            'form_index': form_index,
            'form_action': form_info.get('action', ''),
            'form_method': form_info.get('method', 'GET'),
            'filled_fields': [],
            'submission_result': None,
            'errors': [],
        }
        
        try:
            # Get form element
            forms = await page.query_selector_all('form')
            if form_index >= len(forms):
                result['errors'].append('Form index out of range')
                return result
            
            form = forms[form_index]
            
            # Take screenshot BEFORE filling
            if self.config.CAPTURE_SCREENSHOTS_AFTER_INTERACTIONS:
                await page.screenshot(
                    path=f"{self.config.OUTPUT_DIR}/screenshots/form_{form_index}_before_fill.png",
                    full_page=True
                )
            
            # Fill each input
            print(f"    Filling form {form_index} with {len(form_info.get('inputs', []))} fields...")
            for input_info in form_info.get('inputs', []):
                try:
                    field_filled = await self._fill_input(page, input_info)
                    if field_filled:
                        result['filled_fields'].append(field_filled)
                        print(f"      ✓ Filled: {field_filled.get('name', 'unknown')} = {str(field_filled.get('value', ''))[:30]}")
                except Exception as e:
                    result['errors'].append(f"Error filling {input_info.get('name')}: {str(e)}")
                    print(f"      ✗ Error: {input_info.get('name')}: {e}")
            
            # Wait for a moment to let the form update
            await page.wait_for_timeout(1000)
            
            # Take screenshot AFTER filling (showing filled fields)
            if self.config.CAPTURE_SCREENSHOTS_AFTER_INTERACTIONS:
                await page.screenshot(
                    path=f"{self.config.OUTPUT_DIR}/screenshots/form_{form_index}_after_fill.png",
                    full_page=True
                )
            
            # Submit form if configured
            if self.config.SUBMIT_FORMS:
                # Get current URL
                url_before = page.url
                
                print(f"    Submitting form {form_index}...")
                
                # Try to submit
                try:
                    # Look for submit button
                    submit_button = await form.query_selector('button[type="submit"], input[type="submit"]')
                    if submit_button:
                        await submit_button.click()
                    else:
                        # Try form.submit() via JS
                        await page.evaluate(f'document.forms[{form_index}].submit()')
                    
                    # Wait for response
                    await page.wait_for_load_state('networkidle', timeout=self.config.WAIT_AFTER_SUBMIT)
                    
                    # Capture result
                    url_after = page.url
                    result['submission_result'] = {
                        'url_before': url_before,
                        'url_after': url_after,
                        'navigated': url_before != url_after,
                        'page_title': await page.title(),
                    }
                    
                    # Take screenshot after submission
                    if self.config.CAPTURE_SCREENSHOTS_AFTER_INTERACTIONS:
                        await page.screenshot(
                            path=f"{self.config.OUTPUT_DIR}/screenshots/form_{form_index}_after_submit.png",
                            full_page=True
                        )
                    
                    print(f"    ✓ Form submitted successfully! {url_before} → {url_after}")
                    
                except Exception as e:
                    result['errors'].append(f"Submit error: {str(e)}")
                    print(f"    ✗ Submit error: {e}")
            
            self.filled_forms.append(result)
            return result
            
        except Exception as e:
            result['errors'].append(f"Form filling error: {str(e)}")
            return result
    
    async def _fill_input(self, page, input_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fill a single input field"""
        element_type = input_info.get('element', 'input')
        field_type = input_info.get('type', 'text')
        field_name = input_info.get('name', '')
        field_id = input_info.get('id', '')
        
        try:
            # Build selector
            selector = None
            if field_id:
                selector = f'[id="{field_id}"]'
            elif field_name:
                selector = f'[name="{field_name}"]'
            
            if not selector:
                print(f" No selector found for field: {input_info}")
                return None
            
            # Wait for element
            element = await page.wait_for_selector(selector, state='visible', timeout=5000)
            if not element:
                print(f" Element not found: {selector}")
                return None
            
            filled_data = {
                'element_type': element_type,
                'field_type': field_type,
                'name': field_name,
                'id': field_id,
            }
            
            # Handle different input types
            if element_type == 'input':
                if field_type in ['text', 'email', 'password', 'tel', 'url', 'search', 'number', 'date', 'time']:
                    value = self._get_value_for_input(input_info)
                    
                    #  NEW: Better approach for React controlled inputs
                    await element.click()  # Focus the input
                    await page.keyboard.press('Control+A')  # Select all
                    await page.keyboard.press('Backspace')  # Clear
                    await page.keyboard.type(value, delay=50)  # Type with delay
                    await page.wait_for_timeout(200)  # Let React update
                    
                    filled_data['value'] = value
                    
                elif field_type == 'checkbox':
                    if self.config.CHECKBOX_STRATEGY == 'check_all':
                        await element.check()
                        filled_data['checked'] = True
                    elif self.config.CHECKBOX_STRATEGY == 'random':
                        if random.choice([True, False]):
                            await element.check()
                            filled_data['checked'] = True
                    
                elif field_type == 'radio':
                    if self.config.RADIO_STRATEGY == 'first':
                        await element.check()
                        filled_data['checked'] = True
            
            elif element_type == 'textarea':
                await element.click()
                await page.keyboard.press('Control+A')
                await page.keyboard.press('Backspace')
                await page.keyboard.type(self.config.TEXTAREA_DEFAULT, delay=50)
                filled_data['value'] = self.config.TEXTAREA_DEFAULT
            
            elif element_type == 'select':
                options = input_info.get('options', [])
                if options:
                    if self.config.SELECT_STRATEGY == 'first':
                        await element.select_option(index=0)
                        filled_data['selected'] = options[0]
                    elif self.config.SELECT_STRATEGY == 'random':
                        selected = random.choice(options)
                        await element.select_option(label=selected)
                        filled_data['selected'] = selected
            
            print(f" Successfully filled: {selector} = {filled_data.get('value', 'N/A')}")
            return filled_data
            
        except Exception as e:
            print(f" Error filling field {field_name}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all filled forms"""
        return {
            'total_forms_filled': len(self.filled_forms),
            'forms': self.filled_forms,
            'success_count': len([f for f in self.filled_forms if not f['errors']]),
            'error_count': len([f for f in self.filled_forms if f['errors']]),
        }