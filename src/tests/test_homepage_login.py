import pytest
import re
from playwright.sync_api import sync_playwright, Page
from pytest_bdd import given, when, then, parsers, scenario


@pytest.mark.case_id(1)
@scenario('1.feature', 'I can login successfully with email and password')
def test_login_with_email_password_caseid_1():
    pass


@pytest.mark.case_id(2)
@scenario('2.feature', 'I can login successfully with email and Verification Code')
def test_login_with_email_verification_code_caseid_2():
    pass


@pytest.mark.case_id(12)
@scenario('12.feature', 'I can login successfully with phone verification code')
def test_login_with_phone_verification_code_caseid_12():
    pass


@pytest.mark.case_id(10)
@scenario('10.feature', 'I can login successfully with my line account')
def test_login_with_sso_line_caseid_10():
    pass


@pytest.mark.case_id(11)
@scenario('11.feature', 'I can login successfully with my facebook account')
def test_login_with_sso_facebook_caseid_11():
    pass


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item, call):
    """
    After running a test case, sync results to corresponding logout case IDs.
    """
    # Check if the test has a case_id marker
    case_id_marker = item.get_closest_marker("case_id")
    if not case_id_marker:
        return

    # Extract the case_id
    case_id = case_id_marker.args[0]

    # Check if the case_id has a corresponding logout case_id
    if case_id in CASE_MAPPING and call.when == "call":
        # Determine test status
        status_id = 1 if call.excinfo is None else 5  # 1: Passed, 5: Failed
        comment = f"Test {'passed' if status_id == 1 else 'failed'} for case_id {case_id}."

        # Upload result for the login case_id
        add_result_for_test(RUN_ID, case_id, status_id, comment)

        # Sync result to the corresponding logout case_id
        logout_case_id = CASE_MAPPING[case_id]
        add_result_for_test(
            RUN_ID,
            logout_case_id,
            status_id,
            f"Synced result from login case_id {case_id}:\n{comment}",
        )


@then("I can see the member center")
def check_my_account(page: Page):
    page.get_by_role("link", name="User").click()
    page.wait_for_timeout(3000)
    assert page.get_by_role("link", name="會員中心").is_visible()
