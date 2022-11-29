import pytest
from typing import Dict, Any


@pytest.hookspec
def pytest_xray_results(results: Dict[str, Any], session: pytest.Session) -> None:
    """
    Called before uploading XRAY result to Jira server.

    :param results: xray results dictionary
    :param session: pytest session
    """


@pytest.hookspec(firstresult=True)
def pytest_xray_execution_key(execution_key: str) -> str:
    """
    Called before adding the Jira execution key to the report.

    :param execution_key: The pre-determined execution key, set from the CLI option
    """


@pytest.hookspec(firstresult=True)
def pytest_xray_project(project_key):
    """Called before setting the project on the test execution"""


@pytest.hookspec(firstresult=True)
def pytest_xray_summary(report_summary):
    """Called before setting the summary on the test execution"""


@pytest.hookspec(firstresult=True)
def pytest_xray_execution_description(description):
    """Called before setting the description on the test execution"""


@pytest.hookspec(firstresult=True)
def pytest_xray_fix_version(*fix_version):
    """Called before setting the fix_version on the test execution"""


@pytest.hookspec(firstresult=True)
def pytest_xray_revision(revision):
    """Called before setting the revision on the test execution"""


@pytest.hookspec(firstresult=True)
def pytest_xray_user(user_id):
    """Called before setting the user id of whomever executed the tests"""


@pytest.hookspec(firstresult=True)
def pytest_xray_test_plan_key(test_plan_key):
    """Called before setting the test plan key on the test execution"""


@pytest.hookspec(firstresult=True)
def pytest_xray_test_environments(*test_environments):
    """Called before setting the test environments on the test execution"""


@pytest.hookspec(firstresult=True)
def pytest_xray_status_mapping(is_cloud, node_id, report_outcome, failure_when, wasxfail):
    """Called before setting the test status, can be used to set custom statuses"""


@pytest.hookspec(firstresult=True)
def pytest_xray_test_run_description(report_description):
    """Called before setting the description on the test run"""
