def pytest_xray_execution_key(report):
    """Called before adding the Jira execution key to the report"""


def pytest_xray_project(report):
    """Called before adding the project to the report"""


def pytest_xray_summary(report):
    """Called before adding the summary to the report"""


def pytest_xray_description(report):
    """Called before adding the description to the report"""


def pytest_xray_fix_version(report):
    """Called before adding the fix_version to the report"""


def pytest_xray_revision(report):
    """Called before adding the revision to the report"""


def pytest_xray_user(report):
    """Called before adding the user to the report"""


def pytest_xray_test_plan_key(report):
    """Called before adding the test plan key to the report"""


def pytest_xray_test_environments(report):
    """Called before adding the test environments to the report"""
