import json
import textwrap

import pytest
from _pytest.config import ExitCode
from _pytest.pytester import Pytester


def test_report_exists(pytester: Pytester, marked_xray_pass):
    report = pytester.runpytest('--xray-json', '--execution=JIRA_EX-1')
    path = pytester.path.joinpath('report.json')
    assert report.ret is ExitCode.OK
    assert path.exists()


@pytest.mark.parametrize('report_name', ['report', 'test_name.txt', 'some/path/report.json'])
def test_report_name_and_path_can_be_customized(report_name, pytester: Pytester, marked_xray_pass):
    report_cli = '--xray-json=' + report_name
    report = pytester.runpytest(report_cli, '--execution=JIRA_EX-1')
    path = pytester.path.joinpath(report_name)
    assert report.ret is ExitCode.OK
    assert path.exists()


def test_report_has_passed_test(pytester: Pytester, marked_xray_pass):
    report = pytester.runpytest('--xray-json', '--execution=JIRA_EX-1')
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
    report = pytester.runpytest('--xray-json', '--execution=JIRA_EX-1')
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
    report = pytester.runpytest('--xray-json', '--execution=JIRA_EX-1')
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
    report = pytester.runpytest('--xray-json', '--execution=JIRA_EX-1')
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
    report = pytester.runpytest('--xray-json', '--execution=JIRA_EX-1')
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
    report = pytester.runpytest('--xray-json', '--execution=JIRA_EX-1')
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
    report = pytester.runpytest('--xray-json', '--execution=JIRA-1')
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
    report = pytester.runpytest('--xray-json', '--execution=JIRA-1')
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
    report = pytester.runpytest('--xray-json', '--execution=JIRA-1')
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
    report = pytester.runpytest('--xray-json', '--execution=JIRA-1')
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
    report = pytester.runpytest('--xray-json', '--execution=JIRA-1')
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
    report = pytester.runpytest('--xray-json', '--execution=JIRA-1')
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
    report = pytester.runpytest('--xray-json', '--execution=JIRA-1')
    assert report.ret is ExitCode.OK
    report.assert_outcomes(passed=1)
    assert pytester.path.joinpath('report.json').exists()
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 1
    assert not hasattr(xray_report['tests'][0], 'test_key')
    assert hasattr(xray_report['tests'][0], 'test_info')
    assert hasattr(xray_report['tests'][0]['test_info'], 'test_type')


@pytest.mark.usefixtures('mock_server')
def test_jira_xray_plugin_multiple_ids_fail(xray_tests_multi_fail):
    result = xray_tests_multi_fail.runpytest(
        '--xraypath',
        str(xray_file)
    )
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        '*Generated XRAY execution report file:*xray.json*',
    ])
    assert result.ret == 1
    assert pytester.path.joinpath('report.json').exists()
    with open(xray_file) as f:
        data = json.load(f)

    assert len(data['tests']) == 2
    print(data['tests'])


def test_xray_with_all_test_types(testdir):
    testdir.makepyfile(textwrap.dedent(
        """\
        import pytest

        @pytest.fixture
        def error_fixture():
            assert 0

        @pytest.mark.xray('JIRA-1')
        def test_ok():
            print("ok")

        @pytest.mark.xray('JIRA-2')
        def test_fail():
            assert 0

        @pytest.mark.xray('JIRA-3')
        def test_error(error_fixture):
            pass

        @pytest.mark.xray('JIRA-4')
        def test_skip():
            pytest.skip("skipping this test")

        @pytest.mark.xray('JIRA-5')
        def test_xfail():
            pytest.xfail("xfailing this test")

        @pytest.mark.xfail(reason="always xfail")
        @pytest.mark.xray('JIRA-6')
        def test_xpass():
            pass
        """))

    result = testdir.runpytest(
        '--xraypath',
        '-v',
    )

    assert result.ret == 1
    result.assert_outcomes(errors=1, failed=1, passed=1, skipped=1, xfailed=1, xpassed=1)
    # assert path.exists()
    with open(report_file) as file:
        data = json.load(file)

    xray_statuses = set((t['testKey'], t['status']) for t in data['tests'])
    assert xray_statuses == {
        ('JIRA-1', 'PASS'),
        ('JIRA-2', 'FAIL'),
        ('JIRA-3', 'FAIL'),
        ('JIRA-4', 'ABORTED'),
        ('JIRA-5', 'FAIL'),
        ('JIRA-6', 'PASS')
    }


def test_jira_xray_plugin_multiple_ids(pytester: Pytester, marked_xray_pass):
    result = pytester.runpytest('--xray-path')
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines([
        '*Generated XRAY execution report file:*xray.json*',
    ])
    assert result.ret == 0
    assert not result.errlines
    assert xray_file.exists()
    with open(xray_file) as f:
        data = json.load(f)

    assert len(data['tests']) == 2
    assert data['tests'][0]['testKey'] == 'JIRA-1'
    assert data['tests'][1]['testKey'] == 'JIRA-2'
