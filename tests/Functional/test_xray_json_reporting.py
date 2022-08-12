import json

import pytest
from _pytest.config import ExitCode
from _pytest.pytester import Pytester


def test_report_exists(pytester: Pytester, marked_xray_pass):
    report = pytester.runpytest('--xrayjson=report.json', '--execution=JIRA_EX-1')
    assert report.ret is ExitCode.OK
    report.assert_outcomes(passed=1)
    assert not report.errlines
    assert pytester.path.joinpath('report.json').exists()


def test_report_has_passed_test(pytester: Pytester, marked_xray_pass):
    report = pytester.runpytest('--xrayjson=report.json', '--execution=JIRA_EX-1')
    path = pytester.path.joinpath('report.json')
    assert report.ret is ExitCode.OK
    report.assert_outcomes(passed=1)
    assert not report.errlines
    assert path.exists()
    with open(path) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 1
    assert 'testKey' in xray_report['tests'][0]
    assert xray_report['tests'][0]['testKey'] is not None
    assert xray_report['tests'][0]['status'] == "PASS"


def test_report_has_failed_test(pytester: Pytester, marked_xray_fail):
    report = pytester.runpytest('--xrayjson=report.json', '--execution=JIRA_EX-1')
    report = pytester.runpytest('--xrayjson=report.json', '--execution=JIRA_EX-1', '--lf')
    assert report.ret is ExitCode.TESTS_FAILED
    report.assert_outcomes(failed=1)
    assert not report.errlines
    assert pytester.path.joinpath('report.json').exists()
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 1
    assert not hasattr(xray_report['tests'][0], 'test_key')
    assert hasattr(xray_report['tests'][0], 'test_info')
    assert hasattr(xray_report['tests'][0]['test_info'], 'test_type')


def test_report_has_xfailed_test(pytester: Pytester, marked_xray_expected_exception):
    report = pytester.runpytest('--xrayjson=report.json', '--execution=JIRA_EX-1')
    assert report.ret is ExitCode.OK
    report.assert_outcomes(passed=1)
    assert not report.errlines
    assert pytester.path.joinpath('report.json').exists()
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 1
    assert not hasattr(xray_report['tests'][0], 'test_key')
    assert hasattr(xray_report['tests'][0], 'test_info')
    assert hasattr(xray_report['tests'][0]['test_info'], 'test_type')


def test_report_has_skipped_test(pytester: Pytester, marked_xray_test_skipped):
    report = pytester.runpytest('--xrayjson=report.json', '--execution=JIRA_EX-1')
    assert report.ret is ExitCode.OK
    report.assert_outcomes(skipped=1)
    assert not report.errlines
    assert pytester.path.joinpath('report.json').exists()
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 1
    assert not hasattr(xray_report['tests'][0], 'test_key')
    assert hasattr(xray_report['tests'][0], 'test_info')
    assert hasattr(xray_report['tests'][0]['test_info'], 'test_type')


def test_report_has_exception_test(pytester: Pytester, marked_xray_exception):
    report = pytester.runpytest('--xrayjson=report.json', '--execution=JIRA_EX-1')
    assert report.ret is ExitCode.TESTS_FAILED
    report.assert_outcomes(failed=1)
    assert not report.errlines
    assert pytester.path.joinpath('report.json').exists()
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 1
    assert not hasattr(xray_report['tests'][0], 'test_key')
    assert hasattr(xray_report['tests'][0], 'test_info')
    assert hasattr(xray_report['tests'][0]['test_info'], 'test_type')


def test_report_has_error_test(pytester: Pytester, marked_xray_test_error):
    report = pytester.runpytest('--xrayjson=report.json', '--execution=JIRA_EX-1')
    assert report.ret is ExitCode.TESTS_FAILED
    report.assert_outcomes(errors=1)
    assert not report.errlines
    assert pytester.path.joinpath('report.json').exists()
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 1
    assert not hasattr(xray_report['tests'][0], 'test_key')
    assert hasattr(xray_report['tests'][0], 'test_info')
    assert hasattr(xray_report['tests'][0]['test_info'], 'test_type')


def test_report_has_anon_passed_test(pytester: Pytester, anonymous_pass):
    report = pytester.runpytest('--xrayjson=report.json', '--execution=JIRA-1')
    assert report.ret is ExitCode.OK
    report.assert_outcomes(passed=1)
    assert not report.errlines
    assert pytester.path.joinpath('report.json').exists()
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 1
    assert not hasattr(xray_report['tests'][0], 'test_key')
    assert hasattr(xray_report['tests'][0], 'test_info')
    assert hasattr(xray_report['tests'][0]['test_info'], 'test_type')


def test_report_has_anon_failed_test(pytester: Pytester, anonymous_fail):
    report = pytester.runpytest('--xrayjson=report.json', '--execution=JIRA-1')
    assert report.ret is ExitCode.TESTS_FAILED
    report.assert_outcomes(failed=1)
    assert not report.errlines
    assert pytester.path.joinpath('report.json').exists()
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 1
    assert not hasattr(xray_report['tests'][0], 'test_key')
    assert hasattr(xray_report['tests'][0], 'test_info')
    assert hasattr(xray_report['tests'][0]['test_info'], 'test_type')


def test_report_has_anon_xfailed_test(pytester: Pytester, anonymous_expected_fail):
    report = pytester.runpytest('--xrayjson=report.json', '--execution=JIRA-1')
    assert report.ret is ExitCode.OK
    report.assert_outcomes(xfailed=1)
    assert not report.errlines
    assert pytester.path.joinpath('report.json').exists()
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 1
    assert not hasattr(xray_report['tests'][0], 'test_key')
    assert hasattr(xray_report['tests'][0], 'test_info')
    assert hasattr(xray_report['tests'][0]['test_info'], 'test_type')


def test_report_has_anon_skipped_test(pytester: Pytester, anonymous_test_skipped):
    report = pytester.runpytest('--xrayjson=report.json', '--execution=JIRA-1')
    assert report.ret is ExitCode.OK
    report.assert_outcomes(skipped=1)
    assert not report.errlines
    assert pytester.path.joinpath('report.json').exists()
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 1
    assert not hasattr(xray_report['tests'][0], 'test_key')
    assert hasattr(xray_report['tests'][0], 'test_info')
    assert hasattr(xray_report['tests'][0]['test_info'], 'test_type')


def test_report_ignores_marked_test(pytester: Pytester, marked_xray_ignore):
    report = pytester.runpytest('--xrayjson=report.json', '--execution=JIRA-1')
    assert report.ret is ExitCode.OK
    report.assert_outcomes(passed=1)
    assert not report.errlines
    assert pytester.path.joinpath('report.json').exists()
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 1
    assert not hasattr(xray_report['tests'][0], 'test_key')
    assert hasattr(xray_report['tests'][0], 'test_info')
    assert hasattr(xray_report['tests'][0]['test_info'], 'test_type')


@pytest.mark.usefixtures('marked_xray_fail',
                         'marked_xray_exception',
                         'marked_xray_expected_exception',
                         'marked_xray_ignore',
                         'marked_xray_test_error',
                         'marked_xray_pass',
                         'marked_xray_test_skipped',
                         'marked_xray_expected_fail')
def test_multiple_ids(pytester: Pytester):
    report = pytester.runpytest('--xrayjson=report.json', '--execution=JIRA-1')
    assert report.ret is ExitCode.TESTS_FAILED
    report.assert_outcomes(errors=1, failed=2, passed=3, skipped=1, xfailed=1)
    assert not report.errlines
    assert pytester.path.joinpath('report.json').exists()
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 1
    assert not hasattr(xray_report['tests'][0], 'test_key')
    assert hasattr(xray_report['tests'][0], 'test_info')
    assert hasattr(xray_report['tests'][0]['test_info'], 'test_type')


def test_non_marked_tests(pytester, anonymous_pass):
    report = pytester.runpytest('--xrayjson=report.json', '--execution=JIRA-1')
    assert report.ret is ExitCode.OK
    report.assert_outcomes(passed=1)
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 1
    assert not hasattr(xray_report['tests'][0], 'test_key')
    assert hasattr(xray_report['tests'][0], 'test_info')
    assert hasattr(xray_report['tests'][0]['test_info'], 'test_type')
