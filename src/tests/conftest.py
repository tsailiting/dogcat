import pytest
from playwright.sync_api import Page, expect, sync_playwright
from pytest_bdd import given, parsers, scenario, then, when
import requests
from requests.exceptions import RequestException
import json
from datetime import datetime, timedelta
import pytz
import time
from mailtm import get_mailtm_domains, login_to_mailtm
import re


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


# Fixture to store headers globally after login
@pytest.fixture(scope="session")
def mailtm_headers():
    return {"Authorization": None}


@pytest.fixture
def verification_code(mailtm_headers, sender_info):
    """
    Fixture to fetch and store the verification code from Mail.tm.
    """
    return check_verification_code_in_5_minutes(mailtm_headers, sender_info)


@given(parsers.parse("I am in {url} page"), target_fixture="url")
def given_url(url) -> None:
    return url


@given(parsers.parse("I have homepage account: {email}, {password}"), target_fixture="user")
def given_user(email, password):
    return dict(email=email, password=password)


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


@when('I generate mailtm account')
def mailtm_generate_account(request):
    version = request.config.getoption("deploy_version")
    print(version)
    domains = get_mailtm_domains()
    email_address = f"{version}@{domains[0]}"
    print(email_address)


BASE_URL = "https://api.mail.tm"


@given(parsers.parse('I have sender info {sender_email}, {sender_name}'), target_fixture="sender_info")
def given_sender_info(sender_email, sender_name):
    return dict(sender_email=sender_email, sender_name=sender_name)


@given(parsers.parse("I have tm mail account info {email}, {password}"), target_fixture="mail_account")
def given_mail_account(email, password):
    return dict(email=email, password=password)


@when('I login the mail tm')
def mailtm_login(mail_account, mailtm_headers):
    """
    Step: Log in to mail.tm using the login_to_mailtm function.
    """
    login_to_mailtm(mail_account['email'],
                    mail_account['password'], mailtm_headers)


@when("I check the verification code in the email")
def check_verification_code(verification_code):
    """
    Use the verification_code fixture to ensure the verification code is available.
    """
    # Simply print or log the verification code for debugging purposes
    print("Verification Code Found:", verification_code)


def check_verification_code_in_5_minutes(headers, sender_info):
    """
    Check the inbox for a verification code email from a specific sender within the last 5 minutes.
    """
    messages_url = f"{BASE_URL}/messages"
    try:
        # Fetch messages
        response = requests.get(
            messages_url, headers=headers, timeout=30, verify=False)
        response.raise_for_status()

    except RequestException as e:
        pytest.fail(f"An error occurred while fetching messages: {e}")

    filtered_messages = []
    if response.status_code == 200:
        messages = json.loads(response.text)['hydra:member']
        current_time = datetime.now().replace(tzinfo=pytz.utc)
        sorted_messages = sorted(
            messages,
            key=lambda x: datetime.fromisoformat(
                x['createdAt'].replace('Z', '+00:00')),
            reverse=True
        )

        # Filter messages from the last 5 minutes
        for message in sorted_messages:
            time.sleep(2)  # Optional delay for debugging
            if all(key in message for key in ('createdAt', 'from', 'subject')):
                received_time = datetime.fromisoformat(
                    message['createdAt'].replace('Z', '+00:00'))
                time_n_minutes_ago = current_time - timedelta(minutes=5)

                if received_time > time_n_minutes_ago:
                    if 'from' in message and len(message['from']) > 0:
                        if (message['from']['name'] == sender_info['sender_name'] and
                                message['from']['address'] == sender_info['sender_email']):
                            filtered_messages.append(message)
                            print(
                                f"Verification code email found: {message['id']}")
                    else:
                        pytest.fail("The 'from' field is missing or empty.")
            else:
                pytest.fail(
                    "One of the required fields is missing in the message.")

        if not filtered_messages:
            pytest.fail(f"No matching emails found in the last {5} minutes.")
    else:
        pytest.fail(
            f"Failed to fetch emails. Status code: {response.status_code}")

    # Sort and select the most recent matched mail
    filtered_messages.sort(
        key=lambda x: datetime.fromisoformat(
            x['createdAt'].replace('Z', '+00:00')),
        reverse=True
    )
    email_id = filtered_messages[0]['id']
    email_url = f"{BASE_URL}/messages/{email_id}"
    print('Verification mail URL is:', email_url)

    # Fetch the email content
    response = requests.get(email_url, headers=headers)
    if response.status_code != 200:
        pytest.fail(
            f"Failed to fetch email. Status code: {response.status_code}")

    verification_email_html = response.json().get('text', '')

    # Extract the verification code using regex
    match = re.search(r'\b\d{6}\b', verification_email_html)
    if match:
        verification_code = match.group(0)
        print("Verification Code:", verification_code)
        return verification_code
    else:
        pytest.fail("No verification code found.")


@when(parsers.parse('I wait for {minutes:d} minutes'))
def wait_for_minutes(page: Page, minutes: int):
    wait_time_ms = minutes * 60 * 1000
    print(f"Waiting for {minutes} minutes...")
    page.wait_for_timeout(wait_time_ms)
    print(f"Finished waiting for {minutes} minutes.")
