import pytest
from playwright.sync_api import sync_playwright, Page
from pytest_bdd import given, when, then, parsers

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def page(browser):
    page = browser.new_page()
    yield page
    page.close()
    
@given(parsers.parse("I am in {url} page"), target_fixture="url")
def given_url(url)->None:
    return url

@given(parsers.parse("I have homepage account: {email}, {password}"), target_fixture="user")
def given_user(email,password):
    return dict(email=email,password=password)

@when("I go to page")
def navigate_to_home(url, page:Page):
    page.goto(url)
    page.wait_for_timeout(1000)

