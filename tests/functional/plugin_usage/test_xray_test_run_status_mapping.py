import json

import pytest
from _pytest.config import ExitCode
from _pytest.pytester import Pytester


@pytest.mark.parametrize("conftest", [
    pytest.param(
        """
        import pytest
        from pytest_jira_xray.test_run import OrderedEnum
        
        @pytest.hookimpl
        def pytest_xray_status_mapping(is_cloud, node_id, report_outcome, failure_when, wasxfail):
            TestStatus = OrderedEnum("TestStatus", [("TESTPASS", "FUNCTIONAL PASS"),("TESTFAIL", "FUNCTIONAL FAIL")])
            return TestStatus.TESTPASS
        """),

])
def test_status_map_hook(pytester: Pytester, conftest, marked_xray_pass):
    pytester.makeconftest(conftest)
    report = pytester.runpytest('--xray-json', '--execution=JIRAEX-1')
    assert report.ret is ExitCode.OK
    report.assert_outcomes(passed=1)
    assert not report.errlines
    assert pytester.path.joinpath('report.json').exists()
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 1
    assert 'status' in xray_report['tests'][0]
    assert xray_report['tests'][0]['status'] == "FUNCTIONAL PASS"


@pytest.mark.parametrize("conftest", [
    pytest.param(
        """
        import pytest
        
        @pytest.hookimpl
        def pytest_xray_status_mapping(is_cloud, node_id, report_outcome, failure_when, wasxfail):
            return 1
        """),
    pytest.param(
        """
        import pytest
        
        @pytest.hookimpl
        def pytest_xray_status_mapping(is_cloud, node_id, report_outcome, failure_when, wasxfail):
            return dict()
        """),
    pytest.param(
        """
        import pytest
        
        @pytest.hookimpl
        def pytest_xray_status_mapping(is_cloud, node_id, report_outcome, failure_when, wasxfail):
            return list()
        """),
    pytest.param(
        """
        import pytest
        
        @pytest.hookimpl
        def pytest_xray_status_mapping(is_cloud, node_id, report_outcome, failure_when, wasxfail):
            return 1
        """)

])
def test_invalid_status_map_hook(pytester: Pytester, conftest, marked_xray_pass):
    pytester.makeconftest(conftest)
    report = pytester.runpytest('--xray-json', '--execution=JIRAEX-1')
    assert report.ret is ExitCode.INTERNAL_ERROR


def test_cloud_status_map_hook(pytester: Pytester, marked_xray_pass):
    report = pytester.runpytest('--xray-json', '--execution=JIRAEX-1', '--cloud')
    assert report.ret is ExitCode.OK
    report.assert_outcomes(passed=1)
    assert not report.errlines
    assert pytester.path.joinpath('report.json').exists()
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 1
    assert 'status' in xray_report['tests'][0]
    assert xray_report['tests'][0]['status'] == "PASSED"
