import pytest
from playwright.sync_api import Page, expect, sync_playwright
from pytest_bdd import given, parsers, scenario, then, when

@pytest.fixture(scope="session")
def playwright():
    with sync_playwright() as playwright_instance:
        yield playwright_instance

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True, 
            args=[
                '--autoplay-policy=no-user-gesture-required',
                '--disable-web-security',
                '--enable-media-source'
            ]
        )
        yield browser
        browser.close()

@pytest.fixture(scope="session")
def context(browser):
    context = browser.new_context(permissions=['geolocation'])
    context.set_default_timeout(10000)
    yield context
    context.close()

@pytest.fixture(scope="session")
def page(context):
    page = context.new_page()
    yield page
    page.close()

@given(parsers.parse("I am in {url} page"), target_fixture="url")
def given_url(url)->None:
    return url

@given(parsers.parse("I have homepage account: {email}, {password}"), target_fixture="user")
def given_user(email,password):
    return dict(email=email,password=password)

@when("I go to page")
def navigate_to_home(url, page):
    page.goto(url)
    page.wait_for_timeout(1000)

@when("I click homepage confirm modal")
def click_homepage_confirm_modal(page: Page):
    if page.get_by_role("button", name="確定前往").is_visible():
        page.get_by_role("button", name="確定前往").click()
        page.wait_for_timeout(3000)
        
@when("I click login icon")
def click_login_icon(page: Page):
    page.get_by_role("link", name="User").click()
    page.wait_for_timeout(1000)

@when(parsers.parse("I choose login type {login_type}"))
def choose_login_type(page: Page, login_type):
    print(f"Attempting to log in using {login_type}")  # Debug print
    button_selector = f'role=button[name="使用 {login_type} 登入"]'
    page.click(button_selector)
    page.wait_for_timeout(3000)
    print(f"Clicked on login button for {login_type}")  # Debug print