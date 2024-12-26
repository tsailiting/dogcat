import pytest
from playwright.sync_api import sync_playwright
from pytest_bdd import given, when, then, parsers, scenario

@scenario ('../features/1.feature',"I can login successfully with email and password")
def test_login_with_email_password_caseid_1():
    pass

    # page.get_by_role("button", name="確定前往").click()
    # page.get_by_role("link", name="User").click()
    # page.get_by_role("button", name="使用 電子信箱 登入").click()
    # page.get_by_placeholder("請輸入", exact=True).click()
    # page.get_by_placeholder("請輸入", exact=True).fill("sherryst1@gmail.com")
    # page.get_by_role("button", name="確認").click()
    # page.get_by_role("button", name="密碼登入").click()
    # page.locator("div").filter(has_text=re.compile(r"^輸入密碼$")).locator("div").first.click()
    # page.get_by_placeholder("請輸入", exact=True).fill("St770410")
    # page.get_by_role("button", name="確認").click()