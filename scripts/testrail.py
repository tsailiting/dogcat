import argparse
import os
import xml.etree.ElementTree as ET
import requests
import re

from dotenv import load_dotenv

# Load .env file
load_dotenv(dotenv_path="configs/.env")


def add_result_for_test(run_id, case_id, status_id, comment=None):
    """
    Update test result to TestRail
    :param run_id: TestRail run ID
    :param case_id: TestRail case ID
    :param status_id: TestRail status ID (1: Passed, 5: Failed, 2: Blocked)
    :param comment: test comment
    """
    TESTRAIL_URL = os.getenv("TESTRAIL_URL")
    TESTRAIL_ACCOUNT = os.getenv("TESTRAIL_ACCOUNT")
    TESTRAIL_TOKEN = os.getenv("TESTRAIL_TOKEN")

    if not TESTRAIL_URL or not TESTRAIL_ACCOUNT or not TESTRAIL_TOKEN:
        raise EnvironmentError(
            "TestRail environment variables are not set correctly.")

    url = f"{TESTRAIL_URL}/add_result_for_case/{run_id}/{case_id}"
    headers = {"Content-Type": "application/json"}
    auth = (TESTRAIL_ACCOUNT, TESTRAIL_TOKEN)
    payload = {
        "status_id": status_id,
        "comment": comment or "Test result uploaded via automation."
    }

    response = requests.post(url, headers=headers, auth=auth, json=payload)
    if response.status_code == 200:
        print(
            f"Successfully added result for case_id {case_id} in run_id {run_id}.")
    else:
        print(
            f"Failed to add result for case_id {case_id}: {response.status_code} - {response.text}")


def parse_pytest_results(xml_file, run_id):
    """
    analysis pytest generated JUnit XML and update result to TestRail
    :param xml_file: pytest test result file (XML format)
    :param run_id: TestRail run ID
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    for testcase in root.iter("testcase"):
        test_name = testcase.get("name")
        if not test_name:
            continue

        # extract case_id
        # Split and process only before the parameterized part
        match = re.search(r"caseid_(\d+)", test_name.split("[")[0])
        if not match:
            print(f"Skipping test without valid case_id: {test_name}")
            continue
        case_id = int(match.group(1))  # Extract case_id as an integer
        login_info = test_name.split("[")[
            1][:-1] if "[" in test_name else "No additional info"

        # check test status
        # Determine test status
        if testcase.find("failure") is not None:
            status_id = 5  # Failed
            failure_details = testcase.find(
                "failure").text or "No failure details provided."
            comment = f"Test failed. {failure_details}\nLogin Info: {login_info}"
        else:
            status_id = 1  # Passed
            comment = f"Test passed successfully.\nLogin Info: {login_info}"

        print('case_id: ', case_id, 'result: ',
              status_id, 'comment: ', comment)
        add_result_for_test(run_id, case_id, status_id, comment)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Upload pytest results to TestRail")
    parser.add_argument("-run_id", required=True, type=int,
                        help="TestRail Test Run ID")
    args = parser.parse_args()

    # Step 1: get pytest xml result
    results_dir = "results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    pytest_results_file = os.path.join(results_dir, "results.xml")
    # os.system(f"pytest --junitxml={pytest_results_file}")

    # Step 2
    parse_pytest_results(pytest_results_file, args.run_id)
