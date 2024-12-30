import pytest
import requests

api_url = "https://api.mail.tm/accounts"
base_url = "https://api.mail.tm"


@pytest.fixture(scope="session")
def mailtm_account(email, password):
    # Endpoint for Mail.tm account creation
    # Account creation payload
    payload = {
        "address": email,
        "password": password
    }

    # Send the account creation request
    response = requests.post(api_url, json=payload)
    if response.status_code == 201:
        account_data = response.json()
        return {"email": email, "password": password, "id": account_data["id"]}
    else:
        pytest.fail(f"Failed to create Mail.tm account: {response.text}")


def get_mailtm_domains():

    response = requests.get(api_url)
    if response.status_code == 200:
        domains_data = response.json()
        return [domain["domain"] for domain in domains_data["hydra:member"]]
    else:
        raise Exception(f"Failed to fetch domains: {response.text}")


def create_account(email, password):
    payload = {
        "address": email,
        "password": password
    }
    response = requests.post(api_url, json=payload)
    if response.status_code == 201:
        account_data = response.json()
        return {"email": email, "password": password, "id": account_data["id"]}
    elif response.status_code == 422:
        # Email already used, return a specific message or handle as needed
        print(f"Email address already in use: {email}")
        return {"email": email, "password": password, "already_exists": True}
    else:
        raise Exception(f"Failed to create Mail.tm account: {response.text}")


def new_mailtm_email():
    try:
        domains = get_mailtm_domains()
        # Assuming you want to use the first domain and a fixed local part
        email_local_part = "testuser"
        email_address = f"{email_local_part}@{domains[0]}"
        return email_address
    except Exception as e:
        pytest.fail(f"Failed to get Mail.tm domain: {str(e)}")
# Usage example
# try:
#     domains = get_mailtm_domains()
#     print("Available domains:", domains)
# except Exception as e:
#     print(str(e))


def login_to_mailtm(mail_account, mail_password, mailtm_headers):
    """
    Logs in to mail.tm and updates the mailtm_headers with the token.
    """
    token_url = f"{base_url}/token"

    if mailtm_headers.get("Authorization"):
        print("Already logged in, reusing token.")
        return

    login_payload = {
        "address": mail_account,
        "password": mail_password
    }

    response = requests.post(
        token_url,
        headers={
            "accept": "application/json",
            "Content-Type": "application/json"
        },
        json=login_payload,
        timeout=10
    )

    if response.status_code != 200:
        print(f"Login failed with status code: {response.status_code}")
        print(f"Response content: {response.text}")
        pytest.fail("Login failed.")

    response_data = response.json()
    token = response_data.get("token")
    if not token:
        print(f"Failed to retrieve token from response: {response_data}")
        pytest.fail("Login failed: No token received.")

    mailtm_headers["Authorization"] = f"Bearer {token}"
    print(f"Login successful. Token: {token}")
