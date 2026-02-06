"""
Verification - Verifies expected outcomes after each action
"""
from typing import Dict, Any
from playwright.async_api import Page


class Verifier:
    """Verifies expected outcomes and conditions"""

    def __init__(self, page: Page):
        self.page = page

    async def verify_step_outcome(self, step: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify the expected outcome of a step

        Args:
            step: The step that was executed
            result: The result from executing the step

        Returns:
            Verification result with success status and details
        """
        expected_outcome = step.get('expected_outcome', '')
        verification_spec = step.get('verification', '')

        verification_result = {
            'passed': True,
            'checks': [],
            'warnings': [],
            'errors': []
        }

        # Check if action itself succeeded
        if not result.get('success', False):
            verification_result['passed'] = False
            verification_result['errors'].append(f"Action failed: {result.get('error', 'Unknown error')}")
            return verification_result

        action_type = step.get('action_type', '').lower()

        # Action-specific verifications
        if action_type == 'navigate':
            await self._verify_navigation(step, result, verification_result)
        elif action_type == 'click':
            await self._verify_click(step, result, verification_result)
        elif action_type == 'fill_form':
            await self._verify_form_fill(step, result, verification_result)
        elif action_type == 'submit':
            await self._verify_submit(step, result, verification_result)
        elif action_type == 'verify':
            # Verify action has its own verification logic
            if not result.get('success'):
                verification_result['passed'] = False
                verification_result['errors'].append("Verification step failed")

        # Generic verification based on expected_outcome text
        if expected_outcome:
            await self._verify_generic_expectation(expected_outcome, verification_result)

        return verification_result

    async def _verify_navigation(self, step: Dict[str, Any], result: Dict[str, Any], verification_result: Dict[str, Any]):
        """Verify navigation succeeded"""
        target_url = step.get('target', {}).get('url', '')
        current_url = self.page.url

        if target_url:
            # Check if we're on the expected URL (or close to it)
            if target_url in current_url or current_url.rstrip('/') == target_url.rstrip('/'):
                verification_result['checks'].append({
                    'type': 'url_match',
                    'expected': target_url,
                    'actual': current_url,
                    'passed': True
                })
            else:
                verification_result['warnings'].append(
                    f"URL mismatch: expected '{target_url}', got '{current_url}'"
                )

        # Check page loaded successfully
        if result.get('status'):
            status = result['status']
            if status >= 200 and status < 400:
                verification_result['checks'].append({
                    'type': 'http_status',
                    'status': status,
                    'passed': True
                })
            else:
                verification_result['passed'] = False
                verification_result['errors'].append(f"HTTP error: {status}")

    async def _verify_click(self, step: Dict[str, Any], result: Dict[str, Any], verification_result: Dict[str, Any]):
        """Verify click action completed"""
        # Check if URL changed (navigation occurred)
        url_before = result.get('url_before', '')
        url_after = result.get('url_after', '')

        if url_before and url_after and url_before != url_after:
            verification_result['checks'].append({
                'type': 'navigation_occurred',
                'from': url_before,
                'to': url_after,
                'passed': True
            })

        # Check for common success indicators
        try:
            # Look for modals, alerts, or new content
            has_modal = await self.page.locator('[role="dialog"], .modal, [class*="modal"]').count() > 0
            if has_modal:
                verification_result['checks'].append({
                    'type': 'modal_appeared',
                    'passed': True
                })
        except:
            pass

    async def _verify_form_fill(self, step: Dict[str, Any], result: Dict[str, Any], verification_result: Dict[str, Any]):
        """Verify form filling succeeded"""
        filled_fields = result.get('filled_fields', [])
        total_fields = result.get('total_fields', 0)
        errors = result.get('errors', [])

        if len(filled_fields) == total_fields:
            verification_result['checks'].append({
                'type': 'all_fields_filled',
                'filled': len(filled_fields),
                'total': total_fields,
                'passed': True
            })
        elif len(filled_fields) > 0:
            verification_result['warnings'].append(
                f"Only {len(filled_fields)}/{total_fields} fields filled"
            )
            verification_result['checks'].append({
                'type': 'partial_fill',
                'filled': len(filled_fields),
                'total': total_fields,
                'passed': True
            })
        else:
            verification_result['passed'] = False
            verification_result['errors'].append("No fields were filled")

        if errors:
            for error in errors:
                verification_result['warnings'].append(error)

    async def _verify_submit(self, step: Dict[str, Any], result: Dict[str, Any], verification_result: Dict[str, Any]):
        """Verify form submission succeeded"""
        url_after = result.get('url_after', '')
        ajax_submit = result.get('ajax_submit', False)

        if ajax_submit:
            verification_result['checks'].append({
                'type': 'ajax_submit',
                'passed': True
            })

        # Look for success messages
        try:
            success_indicators = [
                'success', 'submitted', 'thank you', 'confirmation',
                'received', 'completed', 'done'
            ]

            page_text = await self.page.content()
            page_text_lower = page_text.lower()

            found_indicators = [ind for ind in success_indicators if ind in page_text_lower]

            if found_indicators:
                verification_result['checks'].append({
                    'type': 'success_message',
                    'indicators': found_indicators,
                    'passed': True
                })

        except:
            pass

        # Look for error messages
        try:
            error_indicators = ['error', 'invalid', 'failed', 'wrong']
            page_text_lower = (await self.page.content()).lower()

            found_errors = [ind for ind in error_indicators if ind in page_text_lower]

            if found_errors:
                verification_result['warnings'].append(
                    f"Possible error messages detected: {', '.join(found_errors)}"
                )

        except:
            pass

    async def _verify_generic_expectation(self, expected_outcome: str, verification_result: Dict[str, Any]):
        """Verify generic expected outcome by searching for keywords"""
        try:
            page_content = await self.page.content()
            page_content_lower = page_content.lower()
            expected_lower = expected_outcome.lower()

            # Extract keywords from expected outcome
            keywords = [word for word in expected_lower.split() if len(word) > 3]

            # Check if any keywords appear in the page
            found_keywords = [kw for kw in keywords if kw in page_content_lower]

            if found_keywords:
                verification_result['checks'].append({
                    'type': 'expected_outcome',
                    'keywords_found': found_keywords,
                    'passed': True
                })

        except:
            pass

    async def verify_page_state(self, expected_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify the current page state matches expectations

        Args:
            expected_state: Dictionary with expected state conditions

        Returns:
            Verification result
        """
        result = {
            'passed': True,
            'checks': []
        }

        # Verify URL
        if 'url' in expected_state:
            expected_url = expected_state['url']
            current_url = self.page.url

            if expected_url in current_url:
                result['checks'].append({'type': 'url', 'passed': True})
            else:
                result['passed'] = False
                result['checks'].append({
                    'type': 'url',
                    'passed': False,
                    'expected': expected_url,
                    'actual': current_url
                })

        # Verify element presence
        if 'element' in expected_state:
            selector = expected_state['element']
            try:
                count = await self.page.locator(selector).count()
                result['checks'].append({
                    'type': 'element',
                    'selector': selector,
                    'passed': count > 0
                })
                if count == 0:
                    result['passed'] = False
            except:
                result['passed'] = False
                result['checks'].append({
                    'type': 'element',
                    'selector': selector,
                    'passed': False
                })

        # Verify text presence
        if 'text' in expected_state:
            text = expected_state['text']
            try:
                count = await self.page.get_by_text(text, exact=False).count()
                result['checks'].append({
                    'type': 'text',
                    'text': text,
                    'passed': count > 0
                })
                if count == 0:
                    result['passed'] = False
            except:
                result['passed'] = False
                result['checks'].append({
                    'type': 'text',
                    'text': text,
                    'passed': False
                })

        return result
