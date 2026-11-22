"""Ordered live execution with strict matching and evidence for every attempted step."""
import asyncio
import time
from urllib.parse import urljoin

from playwright.async_api import expect


async def resolve_target(inspector, page, step):
    from core.browser_inspector import render_locator
    action, target = step['action_type'], step['target_keyword']
    # Re-read each page, including controls revealed by the previous action.
    deadline = time.monotonic() + 4
    while True:
        elements, live = await inspector._extract_elements(page)
        candidates = []
        for el in elements:
            if action in ('FILL', 'SEARCH') and el.tag not in ('input', 'textarea'):
                continue
            if action == 'SELECT' and el.tag != 'select':
                continue
            if action in ('CHECK', 'UNCHECK') and el.role != 'checkbox':
                continue
            if action == 'CLICK' and el.tag not in ('button', 'a', 'input') and el.role not in ('button', 'tab', 'link', 'menuitem'):
                continue
            names = [el.text_or_label] + [el.attributes.get(k, '') for k in ('id', 'name', 'placeholder', 'data-testid', 'aria-label')]
            names = [v.casefold().strip() for v in names if v]
            score = 2 if target.casefold() in names else 0
            if action == 'SEARCH' and (el.input_type == 'search' or any('search' in n for n in names)):
                score = max(score, 1)
            if score:
                candidates.append((score, el))
        if candidates:
            best = max(score for score, _ in candidates)
            matches = [el for score, el in candidates if score == best]
            if len(matches) != 1:
                raise ValueError(f"Ambiguous target '{target}': {len(matches)} controls match. Use a unique label or test id.")
            el = matches[0]
            return live[el.element_id], el.recommended_locator
        if action == 'VERIFY_UI':
            loc = page.get_by_text(target, exact=True)
            if await loc.count() == 1 and await loc.is_visible():
                return loc, render_locator('text', target)
        if time.monotonic() >= deadline:
            raise ValueError(f"No unique visible target found for {action}: '{target}'")
        await asyncio.sleep(.1)


async def execute_flow(inspector, page, target_url, steps, profile, credentials):
    results, last_action = [], 'page_load'
    login_performed, login_locators = False, {}
    failed = False
    for step in steps:
        result = dict(step, status='skipped', duration_s=0.0, error='', locators={})
        results.append(result)
        if failed:
            result['error'] = 'Not executed because an earlier step failed.'
            continue
        start = time.monotonic()
        action, target = step['action_type'], step['target_keyword']
        label = f"step:{step['step_order']}:{action}"
        inspector._current_action = label
        await inspector._emit('execute_flow', 45, f"Step {step['step_order']}: {action} {target}")
        try:
            if action != 'LOGIN':
                await inspector.auth_guard.check_session()
            if action == 'NAVIGATE':
                response = await page.goto(urljoin(target_url, step['input_value']), wait_until='domcontentloaded', timeout=inspector.navigation_timeout_ms)
                if response and response.status >= 400:
                    raise AssertionError(f"Navigation returned HTTP {response.status}")
                result['navigation_status'] = response.status if response else None
            elif action == 'LOGIN':
                login_performed, login_locators = await inspector._perform_auto_login(page, target or profile, credentials or {})
                if not login_performed:
                    raise AssertionError(inspector.auth_guard.error or 'Authentication failed or credentials/login form unavailable. Configure the selected role.')
            elif action == 'VERIFY_API':
                await inspector._wait_for_network_quiet(quiet_ms=500, timeout_ms=5000)
                if inspector._pending_tasks:
                    await asyncio.gather(*inspector._pending_tasks, return_exceptions=True)
                apis = [a for a in inspector._collect_apis() if a.triggered_by_action == last_action and (not target or target in a.url)]
                if not apis:
                    raise AssertionError(f"No matching API response observed for preceding action ({target or 'any endpoint'}).")
                codes = step['expected_status_codes']
                result['observed_apis'] = [a.model_dump() for a in apis]
                if any(a.status_code not in codes for a in apis):
                    raise AssertionError(f"Expected HTTP {codes}; observed {[a.status_code for a in apis]}")
            elif action == 'PRESS':
                await page.keyboard.press(target)
            elif action in ('CLICK', 'FILL', 'SEARCH', 'SELECT', 'CHECK', 'UNCHECK', 'VERIFY_UI'):
                loc, result['locators'] = await resolve_target(inspector, page, step)
                if action == 'CLICK':
                    await loc.click(timeout=5000)
                elif action in ('FILL', 'SEARCH'):
                    await loc.fill(step['input_value'], timeout=5000)
                    if action == 'SEARCH':
                        await loc.press('Enter')
                elif action == 'SELECT':
                    await loc.select_option(label=step['input_value'], timeout=5000)
                elif action in ('CHECK', 'UNCHECK'):
                    await loc.set_checked(action == 'CHECK', timeout=5000)
                else:
                    await expect(loc).to_be_visible(timeout=5000)
            else:
                raise ValueError(f"Unsupported instruction: {target}. Use explicit click, fill, search, select, login or verify steps.")
            if action not in ('VERIFY_UI', 'VERIFY_API'):
                last_action = inspector._current_action
                await inspector._wait_for_network_quiet(quiet_ms=300, timeout_ms=3000)
            await inspector.auth_guard.check_session()
            result['status'] = 'passed'
        except Exception as exc:
            result['status'], result['error'], failed = 'failed', str(exc), True
        result['duration_s'] = round(time.monotonic() - start, 3)
        result['url'] = page.url
        await inspector._capture_step_screenshot(page, f"{label} {result['status']}")
    return results, login_performed, login_locators
