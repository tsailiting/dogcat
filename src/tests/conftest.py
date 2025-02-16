from twilio.rest import Client
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
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv(dotenv_path="configs/.env")


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


@given(parsers.parse("I have login type {login_type}"), target_fixture="login_type")
def given_login_type(login_type) -> None:
    return login_type


@pytest.fixture
def verification_code(request, login_type, mailtm_headers):
    """
    Unified fixture to fetch the verification code based on the login type.
    """
    print(f"Debug: login_type: {login_type}")

    if login_type == "電子信箱":
        sender_info = request.getfixturevalue("sender_info")
        if not mailtm_headers or not sender_info:
            raise ValueError(
                "Missing mailtm_headers or sender_info for email verification.")
        verification_code = check_verification_code_in_5_minutes(
            mailtm_headers, sender_info)
        return verification_code

    elif login_type == "手機驗證":
        # Dynamically get the `phone_info` fixture
        phone_info = request.getfixturevalue("phone_info")
        if not phone_info:
            raise ValueError("Missing phone_info for mobile verification.")
        print(f"Debug: phone_info: {phone_info}")
        verification_code = check_phone_verification_code_in_5_minutes(
            phone_info)
        return verification_code
    else:
        raise ValueError(f"Invalid login_type: {login_type}")


@given(parsers.parse("I am in {url} page"), target_fixture="url")
def given_url(url) -> None:
    return url


BASE_URL = "https://api.mail.tm"


@given(parsers.parse("I have homepage account: {email}, {password}"), target_fixture="user")
def given_user(email, password):
    return dict(email=email, password=password)


@given(parsers.parse("I have line account: {email}, {password}"), target_fixture="user")
def given_line_user(email, password):
    return dict(email=email, password=password)


@given(parsers.parse("I have facebook account: {email}, {password}"), target_fixture="user")
def given_facebook_user(email, password):
    return dict(email=email, password=password)


@given(parsers.parse('I have sender info {sender_email}, {sender_name}'), target_fixture="sender_info")
def given_sender_info(sender_email, sender_name):
    return dict(sender_email=sender_email, sender_name=sender_name)


@given(parsers.parse("I have tm mail account info {email}, {password}"), target_fixture="mail_account")
def given_mail_account(email, password):
    return dict(email=email, password=password)


@given(parsers.parse("I have phone number {region_code} {phone_number}"), target_fixture="phone_info")
def given_phone_number(region_code=None, phone_number=None):
    if not region_code or not phone_number:
        raise ValueError(
            "Invalid phone_info format. Ensure it contains region_code and phone_number."
        )
    phone_info = {
        "region_code": region_code.strip(),
        "phone_number": phone_number.strip()
    }
    print(f"Debug: Phone info parsed: {phone_info}")
    return phone_info


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
    if login_type == "電子信箱":
        button_selector = f'role=button[name="使用 {login_type} 登入"]'
    else:
        button_selector = f'role=button[name="使用 {login_type}登入"]'
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


@when('I login the mail tm')
def mailtm_login(mail_account, mailtm_headers):
    """
    Step: Log in to mail.tm using the login_to_mailtm function.
    """
    login_to_mailtm(mail_account['email'],
                    mail_account['password'], mailtm_headers)


@when(parsers.parse("I choose region"))
def select_mobile_number_region(page: Page):
    # Wait for the element using the XPath selector
    button = page.locator(
        'xpath=//*[@id="theme-provider"]/div/div/div/div[1]/div/div[1]')
    # Ensure the element is visible before clicking
    button.wait_for(state="visible", timeout=10000)
    # Click the button
    button.click()
    page.wait_for_timeout(3000)
    page.locator("//li[@data-option-index='1']").click()


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


@when("I fill the line account email and password")
def fill_line_account_info(page: Page, user):
    page.get_by_placeholder("Email address").click()
    page.locator("input[name=\"tid\"]").fill(user['email'])
    page.wait_for_timeout(1000)
    page.get_by_placeholder("Password").click()
    page.locator("input[name=\"tpasswd\"]").fill(user['password'])
    page.wait_for_timeout(1000)
    page.get_by_role("button", name="Log in").click()
    page.wait_for_timeout(3000)


@when("I fill the facebook account email and password")
def fill_facebook_account_info(page: Page, user):
    page.fill("#email", user['email'])
    page.wait_for_timeout(1000)
    page.fill("#pass", user['password'])
    page.wait_for_timeout(1000)
    page.click("button[name='login']")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)


@when(parsers.parse("I grant the facebook permission with {username}"))
def grant_facebook_permission(page: Page, username):
    page.get_by_label(f"以 {username} 的身分繼續").click()
    page.wait_for_timeout(3000)


@when("I fill the phone number")
def fill_phone_number(page: Page, phone_info):
    print(
        f"Debug: Trying to fill the phone number: {phone_info['phone_number']}.")
    page.get_by_placeholder("請輸入", exact=True).click()
    input_field = page.wait_for_selector(
        'input[placeholder="請輸入"]', timeout=5000)
    input_field.click()
    input_field.fill(phone_info['phone_number'])
    page.get_by_placeholder("請輸入", exact=True).press("Enter")
    print("Debug: Phone number filled and confirmed.")


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


@when("I check the verification code in the email")
def check_verification_code(verification_code):
    """
    Use the verification_code fixture to ensure the verification code is available.
    """
    # Simply print or log the verification code for debugging purposes
    print("Verification Code Found:", verification_code)


@when("I check the verification code in the mobile message box")
def check_mobile_verification_code(verification_code):
    """
    Use the verification_code fixture to ensure the verification code is available.
    """
    # Simply print or log the verification code for debugging purposes
    print("Verification Code Found:", verification_code)


@when("I send the verification code in the page")
def send_verification_code(page: Page, verification_code):
    """
    Input the verification code into the webpage.
    """
    # Debug: Print to confirm the type and value of verification_code
    print(
        f"Resolved verification_code: {verification_code}, type: {type(verification_code)}")
    if callable(verification_code):
        verification_code = verification_code()
        print(f"After resolving callable: {verification_code}")
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
            "Verification code must be 6 digits and there must be 6 input boxes."
        )
    # Fill each input box with the corresponding digit
    for index, digit in enumerate(verification_code):
        input_elements[index].fill(digit)
    print(f"Finish Fill Verification Code: {verification_code}")
    page.wait_for_timeout(5000)


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
    print('GET', email_url)
    print('header:', headers)
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


def check_phone_verification_code_in_5_minutes(phone_info):
    """
    Fetch the most recent verification code from Twilio.
    """
    twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    if not twilio_account_sid or not twilio_auth_token:
        raise ValueError("Twilio credentials are not configured correctly.")

    client = Client(twilio_account_sid, twilio_auth_token)
    current_time = datetime.utcnow()

    print(f"Phone info received: {phone_info}")
    region_code = phone_info.get("region_code", "")
    phone_number = phone_info.get("phone_number", "")

    messages = client.messages.list(
        to=f"{region_code}{phone_number}",
        date_sent_after=current_time - timedelta(minutes=5),
        limit=10  # Search limit up to 10 messages
    )

    if not messages:
        raise ValueError("No messages found in the last 5 minutes.")

    for message in messages:
        print(f"Message received: {message.body}")

        match = re.search(r'\b\d{6}\b', message.body)
        if match:
            print(f"Verification code extracted: {match.group(0)}")
            return match.group(0)

    raise ValueError("No verification code found in messages.")


@when(parsers.parse('I wait for {minutes:d} minutes'))
def wait_for_minutes(page: Page, minutes: int):
    wait_time_ms = minutes * 60 * 1000
    print(f"Waiting for {minutes} minutes...")
    page.wait_for_timeout(wait_time_ms)
    print(f"Finished waiting for {minutes} minutes.")


@then('I logout')
def logout_homepage(page: Page):
    page.get_by_role("link", name="User").click()
    page.wait_for_timeout(3000)
    page.get_by_role("link", name="登出").click()
