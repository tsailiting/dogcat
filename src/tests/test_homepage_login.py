import pytest, re
from playwright.sync_api import sync_playwright, Page
from pytest_bdd import given, when, then, parsers, scenario

@scenario('1.feature', 'I can login successfully with email and password')
def test_login_with_email_password_caseid_1():
    pass

@when("I fill the email")
def fill_email(page: Page, user):
    try:
        print("Debug: Trying to fill the email.")
        input_field = page.wait_for_selector('input[placeholder="請輸入"]', timeout=5000)
        input_field.click()
        input_field.fill(user['email'])
        page.get_by_role("button", name="確認").click()
        print("Debug: Email filled and confirmed.")
    except Exception as e:
        print(f"Error while filling the email: {e}")

@when("I choose login with password")
def choose_login_email_with_password(page: Page):
    page.get_by_role("button", name="密碼登入").click()
    page.wait_for_timeout(1000)
    
@when("I fill the password")
def fill_password(page: Page, user):
    page.locator("div").filter(has_text=re.compile(r"^輸入密碼$")).locator("div").first.click()
    page.get_by_placeholder("請輸入", exact=True).fill(user['password'])
    page.get_by_role("button", name="確認").click()
    page.wait_for_timeout(3000)

@then("I can see the member center")
def check_my_account(page: Page):
    assert page.get_by_role("link", name="會員中心").is_visible()