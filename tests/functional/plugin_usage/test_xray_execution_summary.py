import json

import pytest
from _pytest.config import ExitCode
from _pytest.pytester import Pytester


def test_execution_summary(pytester: Pytester, marked_xray_pass):
    report = pytester.runpytest('--xray-json', '--execution=JIRAEX-1', '--execution-summary=hey')
    assert report.ret is ExitCode.OK
    report.assert_outcomes(passed=1)
    assert not report.errlines
    assert pytester.path.joinpath('report.json').exists()
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 1
    assert 'summary' in xray_report['info']
    assert xray_report['info']['summary'] == 'hey'


def test_execution_summary_empty(pytester: Pytester, marked_xray_pass):
    report = pytester.runpytest('--xray-json', '--execution=JIRAEX-1', '--execution-summary=')
    assert report.ret is ExitCode.OK
    report.assert_outcomes(passed=1)
    assert not report.errlines
    assert pytester.path.joinpath('report.json').exists()
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 1
    assert 'summary' not in xray_report['info']


@pytest.mark.parametrize("conftest", [
    """
        import pytest

        @pytest.hookimpl
        def pytest_xray_summary(report_summary):
            return "hooks"
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
    assert 'summary' in xray_report['info']
    assert xray_report['info']['summary'] == 'hooks'


@pytest.mark.parametrize("conftest", [
    """
        import pytest

        @pytest.hookimpl
        def pytest_xray_summary(report_summary):
            return 1
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
    assert 'summary' not in xray_report['info']


@pytest.mark.parametrize("conftest", [
    """
        import pytest

        @pytest.hookimpl
        def pytest_xray_summary(report_summary):
            return "hooks"
        """,
])
def test_execution_summary_hook_override_args(pytester: Pytester, conftest, marked_xray_pass):
    pytester.makeconftest(conftest)
    report = pytester.runpytest('--xray-json', '--execution=JIRAEX-1', '--summary=command')
    assert report.ret is ExitCode.OK
    report.assert_outcomes(passed=1)
    assert not report.errlines
    assert pytester.path.joinpath('report.json').exists()
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 1
    assert 'summary' in xray_report['info']
    assert xray_report['info']['summary'] == 'hooks'

