"""Generate runnable tests from the exact execution plan, without canned sample actions."""
import json
from urllib.parse import urlparse


def build_flow_test(context, language):
    steps = (context.get('scenarios') or [{}])[0].get('steps', [])
    name = context['seq_str'] + '_' + context['flow_slug']
    profile = context['active_access_profile']
    quote = lambda value: json.dumps(value, ensure_ascii=True)
    lines = []
    for step in steps:
        action = step['action']
        target = step.get('element_name', '')
        value = step.get('input_data', '')
        loc = step.get('locators', {}).get(language, '')
        code = []
        if action == 'NAVIGATE':
            parsed = urlparse(value)
            path = (parsed.path or '/') + ('?' + parsed.query if parsed.query else '') + ('#' + parsed.fragment if parsed.fragment else '')
            if step['step_number'] == 1:
                path = ''
            if language == 'python':
                code = [f'response = page.goto(urljoin(base_url, {quote(path)}))', 'assert response is None or response.status < 400, "Navigation failed"']
            elif language in ('ts', 'js'):
                code = [f'const response{step["step_number"]} = await page.goto(new URL({quote(path)}, baseURL).href);', f'expect(response{step["step_number"]}?.status() || 200).toBeLessThan(400);']
            else:
                # URI.resolve("") drops the final path segment in Java. Preserve
                # the supplied login/deployment URL for the initial navigation.
                destination = 'TARGET_URL' if not path else f'java.net.URI.create(TARGET_URL).resolve({quote(path)}).toString()'
                code = [f'Response navigation{step["step_number"]} = page.navigate({destination});', f'Assert.assertTrue(navigation{step["step_number"]} == null || navigation{step["step_number"]}.status() < 400, "Navigation failed");']
        elif action == 'LOGIN':
            role = target or profile
            if language == 'python':
                code = [f'guard.login(lambda: LoginPage(page, base_url).login_with_profile({quote(role)}))']
            elif language in ('ts', 'js'):
                code = [f'await guard.login(() => new LoginPage(page).loginWithProfile({quote(role)}));']
            else:
                code = [f'guard.login(() -> loginPage.loginWithProfile({quote(role)}));']
        elif action == 'PRESS':
            code = [f'page.keyboard.press({quote(target)})'] if language == 'python' else ([f'await page.keyboard.press({quote(target)});'] if language in ('ts', 'js') else [f'page.keyboard().press({quote(target)});'])
        elif action == 'VERIFY_API':
            pattern = step.get('api_url_pattern', '')
            codes = step.get('expected_status_codes') or [200, 201, 204]
            if language == 'python':
                code = [f'verify_api(page, responses, {quote(pattern)}, {codes})']
            elif language in ('ts', 'js'):
                code = [f'await expect.poll(() => responses.filter(r => r.url().includes({quote(pattern)})).length).toBeGreaterThan(0);', f'for (const response of responses.filter(r => r.url().includes({quote(pattern)}))) expect({quote(codes)}).toContain(response.status());']
            else:
                code = [f'page.waitForCondition(() -> responses.stream().anyMatch(r -> r.url().contains({quote(pattern)})));', f'for (Response response : responses) if (response.url().contains({quote(pattern)})) Assert.assertTrue(java.util.Arrays.asList({", ".join(map(str,codes))}).contains(response.status()), "Unexpected API status: " + response.status());']
        elif loc and action in ('CLICK', 'FILL', 'SEARCH', 'SELECT', 'CHECK', 'UNCHECK', 'VERIFY_UI'):
            if language == 'python':
                code = {'CLICK': [f'{loc}.click()'], 'FILL': [f'{loc}.fill({quote(value)})'], 'SEARCH': [f'{loc}.fill({quote(value)})', f'{loc}.press("Enter")'], 'SELECT': [f'{loc}.select_option(label={quote(value)})'], 'CHECK': [f'{loc}.check()'], 'UNCHECK': [f'{loc}.uncheck()'], 'VERIFY_UI': [f'expect({loc}).to_be_visible()']}[action]
            elif language in ('ts', 'js'):
                code = {'CLICK': [f'await {loc}.click();'], 'FILL': [f'await {loc}.fill({quote(value)});'], 'SEARCH': [f'await {loc}.fill({quote(value)});', f'await {loc}.press("Enter");'], 'SELECT': [f'await {loc}.selectOption({{ label: {quote(value)} }});'], 'CHECK': [f'await {loc}.check();'], 'UNCHECK': [f'await {loc}.uncheck();'], 'VERIFY_UI': [f'await expect({loc}).toBeVisible();']}[action]
            else:
                code = {'CLICK': [f'{loc}.click();'], 'FILL': [f'{loc}.fill({quote(value)});'], 'SEARCH': [f'{loc}.fill({quote(value)});', f'{loc}.press("Enter");'], 'SELECT': [f'{loc}.selectOption(new SelectOption().setLabel({quote(value)}));'], 'CHECK': [f'{loc}.check();'], 'UNCHECK': [f'{loc}.uncheck();'], 'VERIFY_UI': [f'assertThat({loc}).isVisible();']}[action]
        else:
            message = quote(f'Unresolved {action} target: {target}. Correct the flow and regenerate.')
            code = [f'raise AssertionError({message})'] if language == 'python' else ([f'throw new Error({message});'] if language in ('ts', 'js') else [f'Assert.fail({message});'])
        if action not in ('VERIFY_API', 'VERIFY_UI'):
            code.insert(0, 'responses.clear()' if language == 'python' else ('responses.length = 0;' if language in ('ts', 'js') else 'responses.clear();'))
        lines.extend(code)
        lines.append('guard.check()' if language == 'python' else 'await guard.check();' if language in ('ts','js') else 'guard.check();')
    if not lines:
        lines = ['raise AssertionError("No executable flow")'] if language == 'python' else ['throw new Error("No executable flow");'] if language in ('ts','js') else ['Assert.fail("No executable flow");']
    body = '\n'.join('    ' + line for line in lines)
    if language == 'python':
        return f'''import time
from urllib.parse import urljoin
from playwright.sync_api import expect
from pages.login_page import LoginPage
from auth_session import SessionGuard
import pytest

def verify_api(page, responses, pattern, codes):
    deadline = time.monotonic() + 5
    while not any(pattern in r.url for r in responses) and time.monotonic() < deadline:
        page.wait_for_timeout(50)
    matches = [r for r in responses if pattern in r.url]
    assert matches, f"No API response observed for {{pattern}}"
    assert all(r.status in codes for r in matches), f"Expected {{codes}}, observed {{[r.status for r in matches]}}"

@pytest.mark.qa_profile({quote(profile)})
def test_{name}(page, base_url):
    assert base_url, "Set BASE_URL in the project .env"
    responses = []
    guard = SessionGuard(page)
    page.on("response", lambda r: responses.append(r) if r.request.resource_type in ("fetch", "xhr") else None)
{body}
'''
    if language in ('ts', 'js'):
        imports = "import { Response } from '@playwright/test';\nconst { test, expect, SessionGuard } = require('../session-fixtures');\nimport { LoginPage } from '../pages/LoginPage';" if language == 'ts' else "const { test, expect, SessionGuard } = require('../session-fixtures');\nconst { LoginPage } = require('../pages/LoginPage');"
        return f'''{imports}
test.use({{qaRole: {quote(profile)}}});
test({quote(name)}, async ({{ page, baseURL }}) => {{
    if (!baseURL) throw new Error('Set BASE_URL in the project .env');
    const responses{': Response[]' if language == 'ts' else ''} = [];
    const guard = new SessionGuard(page);
    page.on('response', r => {{ if (['fetch', 'xhr'].includes(r.request().resourceType())) responses.push(r); }});
{body}
}});
'''
    return f'''package com.corp.qa.tests;
import com.microsoft.playwright.*;
import com.microsoft.playwright.options.*;
import org.testng.Assert;
import org.testng.annotations.Test;
import java.util.ArrayList;
import java.util.List;
import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;
public class Test{context['seq_str']}{context['flow_pascal']} extends BaseTest {{
  @Override protected String accessProfile() {{ return {quote(profile)}; }}
  @Test public void testFlow() {{
    List<Response> responses = new ArrayList<>();
    SessionGuard guard = new SessionGuard(page);
    page.onResponse(r -> {{ if (r.request().resourceType().equals("fetch") || r.request().resourceType().equals("xhr")) responses.add(r); }});
{body}
  }}
}}
'''
