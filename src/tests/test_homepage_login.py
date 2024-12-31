import pytest
import re
from playwright.sync_api import sync_playwright, Page
from pytest_bdd import given, when, then, parsers, scenario


@scenario('1.feature', 'I can login successfully with email and password')
def test_login_with_email_password_caseid_1():
    pass


@scenario('2.feature', 'I can login successfully with email and Verification Code')
def test_login_with_email_verification_code_caseid_2():
    pass


@when("I fill the email")
def fill_email(page: Page, user):
    try:
        print("Debug: Trying to fill the email.")
        page.get_by_placeholder("請輸入", exact=True).click()
        input_field = page.wait_for_selector(
            'input[placeholder="請輸入"]', timeout=5000)
        input_field.click()
        input_field.fill(user['email'])
        page.get_by_placeholder("請輸入", exact=True).press("Enter")
        print("Debug: Email filled and confirmed.")
    except Exception as e:
        print(f"Error while filling the email: {e}")


@when("I choose login with password")
def choose_login_email_with_password(page: Page):
    page.get_by_role("button", name="密碼登入").click()
    page.wait_for_timeout(1000)


@when("I fill the password")
def fill_password(page: Page, user):
    page.get_by_placeholder("請輸入", exact=True).click()
    page.locator("div").filter(has_text=re.compile(
        r"^輸入密碼$")).locator("div").first.click()
    page.get_by_placeholder("請輸入", exact=True).fill(user['password'])
    page.get_by_role("button", name="確認").click()
    page.wait_for_timeout(3000)


@when("I send the verification code in the page")
def send_verification_code(page: Page, verification_code):
    """
    Input the verification code into the webpage.
    """
    input_verification_code(page, verification_code)


def input_verification_code(page, verification_code):
    """
    Input the verification code into the webpage's input fields.
    """
    # Wait for input fields to load
    page.wait_for_selector("form input[type='tel']")

    # Locate all input fields
    input_elements = page.locator("form input[type='tel']").all()

    # Debugging: Check input elements and verification code
    print(f"Number of input elements found: {len(input_elements)}")
    print(f"Verification Code: {verification_code}")

    # Ensure input boxes and verification code are valid
    if len(input_elements) != 6 or len(verification_code) != 6:
        raise ValueError(
            "Verification code must be 6 digits and there must be 6 input boxes.")

    # Fill each input box with the corresponding digit
    for index, digit in enumerate(verification_code):
        input_elements[index].fill(digit)
    print(f"Finish Fill Verification Code: {verification_code}")
    page.wait_for_timeout(5000)


@then("I can see the member center")
def check_my_account(page: Page):
    page.get_by_role("link", name="User").click()
    page.wait_for_timeout(3000)
    assert page.get_by_role("link", name="會員中心").is_visible()
