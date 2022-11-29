import json

import pytest
from _pytest.config import ExitCode
from _pytest.pytester import Pytester


@pytest.mark.parametrize("conftest", [
    """
        import pytest

        @pytest.hookimpl
        def pytest_xray_test_run_description(report_description):
            return "hook description"
        """,
])
def test_execution_summary_hook(pytester: Pytester, conftest, marked_xray_pass):
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
    assert 'description' in xray_report['tests'][0]['testInfo']
    assert xray_report['tests'][0]['testInfo']['description'] == 'hook description'


@pytest.mark.parametrize("conftest", [
    """
        import pytest

        @pytest.hookimpl
        def pytest_xray_test_run_description(report_description):
            return 123
        """,
])
def test_execution_summary_hook_invalid(pytester: Pytester, conftest, marked_xray_pass):
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
    assert 'description' not in xray_report['tests'][0]['testInfo']