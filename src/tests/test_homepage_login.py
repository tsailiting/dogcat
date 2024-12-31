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


@scenario('12.feature', 'I can login successfully with phone verification code')
def test_login_with_phone_verification_code_caseid_12():
    pass


@then("I can see the member center")
def check_my_account(page: Page):
    page.get_by_role("link", name="User").click()
    page.wait_for_timeout(3000)
    assert page.get_by_role("link", name="會員中心").is_visible()
