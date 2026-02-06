"""
Action Handlers - Executes different types of actions in the browser
"""
import asyncio
from typing import Dict, Any, Optional
from playwright.async_api import Page, TimeoutError as PlaywrightTimeout


class ActionHandlers:
    """Handles execution of different action types"""

    def __init__(self, page: Page, timeout: int = 30000):
        self.page = page
        self.timeout = timeout

    async def navigate(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Navigate to a URL"""
        target = step.get('target', {})
        url = target.get('url')

        if not url:
            raise ValueError("Navigate action requires 'url' in target")

        print(f"  -> Navigating to: {url}")

        try:
            response = await self.page.goto(url, timeout=self.timeout, wait_until='domcontentloaded')

            result = {
                'success': True,
                'url': self.page.url,
                'status': response.status if response else None,
                'action': 'navigate'
            }

            # Wait a bit for dynamic content
            await asyncio.sleep(1)

            return result

        except PlaywrightTimeout:
            raise TimeoutError(f"Navigation to {url} timed out")
        except Exception as e:
            raise RuntimeError(f"Navigation failed: {str(e)}")

    async def click(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Click an element"""
        target = step.get('target', {})
        selector = target.get('selector')
        text = target.get('text')

        if not selector and not text:
            raise ValueError("Click action requires 'selector' or 'text' in target")

        # Try selector first, then text
        element_locator = None
        if selector:
            print(f"  -> Clicking element: {selector}")
            element_locator = self.page.locator(selector).first
        elif text:
            print(f"  -> Clicking element with text: '{text}'")
            element_locator = self.page.get_by_text(text, exact=False).first

        try:
            # Wait for element to be visible and enabled
            await element_locator.wait_for(state='visible', timeout=self.timeout)

            # Scroll into view if needed
            await element_locator.scroll_into_view_if_needed()

            # Click
            await element_locator.click(timeout=self.timeout)

            result = {
                'success': True,
                'selector': selector or f"text='{text}'",
                'url_after': self.page.url,
                'action': 'click'
            }

            # Wait for any navigation or dynamic changes
            await asyncio.sleep(1)

            return result

        except PlaywrightTimeout:
            raise TimeoutError(f"Element not found or not clickable: {selector or text}")
        except Exception as e:
            raise RuntimeError(f"Click failed: {str(e)}")

    async def fill_form(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Fill out a form"""
        target = step.get('target', {})
        form_data = target.get('form_data', {})
        selector = target.get('selector')  # Optional form selector

        if not form_data:
            raise ValueError("Fill form action requires 'form_data' in target")

        print(f"  -> Filling form with {len(form_data)} fields")

        filled_fields = []
        errors = []

        for field_name, field_value in form_data.items():
            try:
                # Try multiple selector strategies
                field_selector = None

                # Strategy 1: By name attribute
                if await self.page.locator(f'[name="{field_name}"]').count() > 0:
                    field_selector = f'[name="{field_name}"]'
                # Strategy 2: By id attribute
                elif await self.page.locator(f'#{field_name}').count() > 0:
                    field_selector = f'#{field_name}'
                # Strategy 3: By label text
                elif await self.page.get_by_label(field_name, exact=False).count() > 0:
                    field_selector = f'label:has-text("{field_name}")'
                # Strategy 4: By placeholder
                elif await self.page.get_by_placeholder(field_name, exact=False).count() > 0:
                    field_selector = f'[placeholder*="{field_name}"]'

                if not field_selector:
                    errors.append(f"Field '{field_name}' not found")
                    continue

                # Get the field element
                field = self.page.locator(field_selector).first

                # Wait for field to be visible
                await field.wait_for(state='visible', timeout=5000)
                await field.scroll_into_view_if_needed()

                # Determine field type and fill accordingly
                tag_name = await field.evaluate('el => el.tagName.toLowerCase()')
                input_type = await field.evaluate('el => el.type || "text"')

                if tag_name == 'select':
                    # Dropdown/select
                    await field.select_option(str(field_value))
                elif input_type in ['checkbox', 'radio']:
                    # Checkbox or radio
                    if field_value:
                        await field.check()
                    else:
                        await field.uncheck()
                elif tag_name == 'textarea' or input_type == 'text' or input_type == 'email' or input_type == 'password':
                    # Text input
                    await field.clear()
                    await field.fill(str(field_value))
                else:
                    # Default: try to fill
                    await field.fill(str(field_value))

                filled_fields.append(field_name)
                print(f"    [OK] Filled '{field_name}': {field_value}")

            except Exception as e:
                error_msg = f"Failed to fill '{field_name}': {str(e)}"
                errors.append(error_msg)
                print(f"    X {error_msg}")

        result = {
            'success': len(filled_fields) > 0,
            'filled_fields': filled_fields,
            'errors': errors,
            'total_fields': len(form_data),
            'action': 'fill_form'
        }

        # Brief wait after filling
        await asyncio.sleep(0.5)

        return result

    async def submit(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a form"""
        target = step.get('target', {})
        selector = target.get('selector', 'button[type="submit"]')

        print(f"  -> Submitting form: {selector}")

        try:
            submit_button = self.page.locator(selector).first

            await submit_button.wait_for(state='visible', timeout=self.timeout)
            await submit_button.scroll_into_view_if_needed()

            # Click submit and wait for navigation or response
            async with self.page.expect_navigation(timeout=self.timeout, wait_until='domcontentloaded'):
                await submit_button.click()

            result = {
                'success': True,
                'url_after': self.page.url,
                'action': 'submit'
            }

            # Wait for post-submit processing
            await asyncio.sleep(2)

            return result

        except PlaywrightTimeout:
            # Form might submit without navigation (AJAX)
            print("    Note: Form submitted without navigation (AJAX form)")
            await asyncio.sleep(2)

            return {
                'success': True,
                'url_after': self.page.url,
                'ajax_submit': True,
                'action': 'submit'
            }
        except Exception as e:
            raise RuntimeError(f"Form submission failed: {str(e)}")

    async def wait(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Wait for a condition or duration"""
        target = step.get('target', {})
        duration = target.get('duration', 2000)  # Default 2 seconds
        selector = target.get('selector')
        condition = target.get('condition', 'visible')  # visible, hidden, attached

        if selector:
            print(f"  -> Waiting for element '{selector}' to be {condition}")
            try:
                element = self.page.locator(selector).first
                await element.wait_for(state=condition, timeout=self.timeout)
            except PlaywrightTimeout:
                raise TimeoutError(f"Element '{selector}' did not become {condition}")
        else:
            print(f"  -> Waiting for {duration}ms")
            await asyncio.sleep(duration / 1000)

        return {
            'success': True,
            'waited': duration if not selector else None,
            'action': 'wait'
        }

    async def verify(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a condition"""
        target = step.get('target', {})
        selector = target.get('selector')
        text = target.get('text')
        url_contains = target.get('url_contains')

        print(f"  -> Verifying condition...")

        verifications = []

        # Verify URL
        if url_contains:
            current_url = self.page.url
            if url_contains in current_url:
                print(f"    [OK] URL contains '{url_contains}'")
                verifications.append({'type': 'url', 'success': True})
            else:
                print(f"    X URL does not contain '{url_contains}' (current: {current_url})")
                verifications.append({'type': 'url', 'success': False})

        # Verify element exists
        if selector:
            try:
                element = self.page.locator(selector).first
                await element.wait_for(state='visible', timeout=5000)
                print(f"    [OK] Element '{selector}' is visible")
                verifications.append({'type': 'element', 'success': True})
            except:
                print(f"    X Element '{selector}' not found")
                verifications.append({'type': 'element', 'success': False})

        # Verify text exists on page
        if text:
            try:
                text_element = self.page.get_by_text(text, exact=False).first
                await text_element.wait_for(state='visible', timeout=5000)
                print(f"    [OK] Text '{text}' found on page")
                verifications.append({'type': 'text', 'success': True})
            except:
                print(f"    X Text '{text}' not found on page")
                verifications.append({'type': 'text', 'success': False})

        all_passed = all(v['success'] for v in verifications)

        return {
            'success': all_passed,
            'verifications': verifications,
            'action': 'verify'
        }

    async def type_text(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Type text into an element"""
        target = step.get('target', {})
        selector = target.get('selector')
        text = target.get('text', '')
        delay = target.get('delay', 50)  # Delay between keystrokes (ms)

        if not selector:
            raise ValueError("Type text action requires 'selector' in target")

        print(f"  -> Typing into '{selector}': {text}")

        try:
            element = self.page.locator(selector).first
            await element.wait_for(state='visible', timeout=self.timeout)
            await element.scroll_into_view_if_needed()

            # Clear first
            await element.clear()

            # Type with delay
            await element.type(text, delay=delay)

            return {
                'success': True,
                'selector': selector,
                'text_length': len(text),
                'action': 'type_text'
            }

        except Exception as e:
            raise RuntimeError(f"Type text failed: {str(e)}")

    async def screenshot(self, step: Dict[str, Any], path: str) -> Dict[str, Any]:
        """Take a screenshot"""
        target = step.get('target', {})
        full_page = target.get('full_page', True)

        print(f"  -> Taking screenshot: {path}")

        try:
            await self.page.screenshot(path=path, full_page=full_page)

            return {
                'success': True,
                'path': path,
                'action': 'screenshot'
            }

        except Exception as e:
            raise RuntimeError(f"Screenshot failed: {str(e)}")
