import json
from collections import Counter

import pytest
from _pytest.config import ExitCode
from _pytest.fixtures import FixtureRequest
from _pytest.pytester import Pytester


def test_report_exists(pytester: Pytester, marked_xray_pass):
    report = pytester.runpytest('--xray-json', '--execution=JIRAEX-1')
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


@pytest.mark.parametrize("marked_xray_tests", [
    pytest.param("marked_xray_pass", marks=pytest.mark.usefixtures("marked_xray_pass"), id="pass"),
    pytest.param("marked_xray_fail", marks=pytest.mark.usefixtures("marked_xray_fail"), id="fail"),
    pytest.param("marked_xray_exception", marks=pytest.mark.usefixtures("marked_xray_exception"), id="exception"),
    pytest.param("marked_xray_expected_fail",
                 marks=pytest.mark.usefixtures("marked_xray_expected_fail"),
                 id="expected_fail"),
    pytest.param("marked_xray_expected_exception",
                 marks=pytest.mark.usefixtures("marked_xray_expected_exception"),
                 id="expected_exception"),
    pytest.param("marked_xray_expected_exception_failed",
                 marks=pytest.mark.usefixtures("marked_xray_expected_exception_failed"),
                 id="expected_exception_failed"),
    pytest.param("marked_xray_test_error", marks=pytest.mark.usefixtures("marked_xray_test_error"), id="test_error"),
    pytest.param("marked_xray_test_skipped",
                 marks=pytest.mark.usefixtures("marked_xray_test_skipped"),
                 id="test_skipped"),
])
def test_report_has_marked_test(pytester: Pytester, request, marked_xray_tests):
    marked_xray_test = request.getfixturevalue(marked_xray_tests)
    report = pytester.runpytest('--xray-json', '--execution=JIRAEX-1')
    path = pytester.path.joinpath('report.json')
    assert report.ret is marked_xray_test["exit_code"]
    report.assert_outcomes(**marked_xray_test["status"])
    assert not report.errlines
    assert path.exists()
    with open(path) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 1
    assert 'testKey' in xray_report['tests'][0]
    assert xray_report['tests'][0]['testKey'] is not None
    assert xray_report['tests'][0]['status'] == marked_xray_test["xray_status"]


def test_report_ignores_not_xray_marks(pytester: Pytester, marked_xray_ignore):
    report = pytester.runpytest('--xray-json', '--execution=JIRAEX-1')
    path = pytester.path.joinpath('report.json')
    assert report.ret is marked_xray_ignore["exit_code"]
    report.assert_outcomes(**marked_xray_ignore["status"])
    assert not report.errlines
    assert path.exists()
    with open(path) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 0


@pytest.mark.parametrize("anonymous_tests", [
    pytest.param("anonymous_pass", marks=pytest.mark.usefixtures("anonymous_pass"), id="pass"),
    pytest.param("anonymous_fail", marks=pytest.mark.usefixtures("anonymous_fail"), id="fail"),
    pytest.param("anonymous_exception", marks=pytest.mark.usefixtures("anonymous_exception"), id="exception"),
    pytest.param("anonymous_expected_fail",
                 marks=pytest.mark.usefixtures("anonymous_expected_fail"),
                 id="expected_fail"),
    pytest.param("anonymous_expected_exception",
                 marks=pytest.mark.usefixtures("anonymous_expected_exception"),
                 id="expected_exception"),
    pytest.param("anonymous_expected_exception_failed",
                 marks=pytest.mark.usefixtures("anonymous_expected_exception_failed"),
                 id="expected_exception_failed"),
    pytest.param("anonymous_test_error", marks=pytest.mark.usefixtures("anonymous_test_error"), id="test_error"),
    pytest.param("anonymous_test_skipped",
                 marks=pytest.mark.usefixtures("anonymous_test_skipped"),
                 id="test_skipped"),
])
def test_report_has_anon_test(pytester: Pytester, anonymous_tests, request):
    anonymous_test = request.getfixturevalue(anonymous_tests)
    report = pytester.runpytest('--xray-json', '--execution=JIRAEX-1')
    assert report.ret is anonymous_test["exit_code"]
    report.assert_outcomes(**anonymous_test['status'])
    assert not report.errlines
    assert pytester.path.joinpath('report.json').exists()
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 1
    assert 'test_key' not in xray_report['tests'][0]
    assert 'testInfo' in xray_report['tests'][0]
    assert 'testType' in xray_report['tests'][0]['testInfo']
    assert xray_report['tests'][0]['status'] == anonymous_test['xray_status']


def test_report_ignores_anonymous_not_xray_marks(pytester: Pytester, anonymous_ignore):
    report = pytester.runpytest('--xray-json', '--execution=JIRAEX-1')
    path = pytester.path.joinpath('report.json')
    assert report.ret is anonymous_ignore["exit_code"]
    report.assert_outcomes(**anonymous_ignore["status"])
    assert not report.errlines
    assert path.exists()
    with open(path) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 0


@pytest.mark.usefixtures('marked_xray_fail',
                         'marked_xray_exception',
                         'marked_xray_expected_exception',
                         'marked_xray_expected_exception_failed',
                         'marked_xray_test_error',
                         'marked_xray_pass',
                         'marked_xray_test_skipped',
                         'marked_xray_expected_fail')
def test_multiple_ids(pytester: Pytester, request: FixtureRequest):
    outcomes = dict(sum((Counter(request.getfixturevalue(fixture)['status']) for fixture in request.fixturenames if
                         fixture.startswith("marked_xray")), Counter()))
    report = pytester.runpytest('--xray-json', '--execution=JIRAEX-1')
    assert report.ret is ExitCode.TESTS_FAILED
    report.assert_outcomes(**outcomes)
    assert not report.errlines
    assert pytester.path.joinpath('report.json').exists()
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == sum(v for _, v in outcomes.items())
    assert all('testKey' in test for test in xray_report['tests'])


@pytest.mark.parametrize("duplicate_marked_xray_test", [
    pytest.param("duplicate_marked_xray_pass", marks=pytest.mark.usefixtures("duplicate_marked_xray_pass"), id="pass"),
    pytest.param("duplicate_marked_xray_fail", marks=pytest.mark.usefixtures("duplicate_marked_xray_fail"), id="fail"),
    pytest.param("duplicate_marked_xray_exception",
                 marks=pytest.mark.usefixtures("duplicate_marked_xray_exception"),
                 id="exception"),
    pytest.param("duplicate_marked_xray_expected_fail",
                 marks=pytest.mark.usefixtures("duplicate_marked_xray_expected_fail"),
                 id="expected_fail"),
    pytest.param("duplicate_marked_xray_expected_exception",
                 marks=pytest.mark.usefixtures("duplicate_marked_xray_expected_exception"),
                 id="expected_exception"),
    pytest.param("duplicate_marked_xray_expected_exception_failed",
                 marks=pytest.mark.usefixtures("duplicate_marked_xray_expected_exception_failed"),
                 id="expected_exception_failed"),
    pytest.param("duplicate_marked_xray_test_error",
                 marks=pytest.mark.usefixtures("duplicate_marked_xray_test_error"),
                 id="test_error"),
    pytest.param("duplicate_marked_xray_test_skipped",
                 marks=pytest.mark.usefixtures("duplicate_marked_xray_test_skipped"),
                 id="test_skipped"),
])
def test_duplicate_ids(pytester: Pytester, duplicate_marked_xray_test, request):
    duplicate_marked_xray_test = request.getfixturevalue(duplicate_marked_xray_test)
    report = pytester.runpytest('--xray-json', '--execution=JIRAEX-1', '--duplicates')
    assert report.ret is duplicate_marked_xray_test['exit_code']
    report.assert_outcomes(**duplicate_marked_xray_test['status'])
    assert not report.errlines
    assert pytester.path.joinpath('report.json').exists()
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 1
    assert 'testKey' in xray_report['tests'][0]
    assert xray_report['tests'][0]['testKey'] == "JIRA-1"
    assert 'status' in xray_report['tests'][0]
    assert xray_report['tests'][0]['status'] == duplicate_marked_xray_test['xray_status']


@pytest.mark.usefixtures('anonymous_fail',
                         'anonymous_exception',
                         'anonymous_expected_exception',
                         'anonymous_expected_exception_failed',
                         'anonymous_test_error',
                         'anonymous_pass',
                         'anonymous_test_skipped',
                         'anonymous_expected_fail')
def test_multiple_anonymous(pytester: Pytester, request: FixtureRequest):
    outcomes = dict(sum((Counter(request.getfixturevalue(fixture)['status']) for fixture in request.fixturenames if
                         fixture.startswith("anonymous")), Counter()))
    report = pytester.runpytest('--xray-json', '--execution=JIRA-1')
    assert report.ret is ExitCode.TESTS_FAILED
    report.assert_outcomes(**outcomes)
    assert not report.errlines
    assert pytester.path.joinpath('report.json').exists()
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == sum(v for _, v in outcomes.items())
    assert all('testInfo' in test for test in xray_report['tests'])

# @pytest.mark.usefixtures('mock_server')
# def test_jira_xray_plugin_multiple_ids_fail(xray_tests_multi_fail):
#     result = xray_tests_multi_fail.runpytest(
#         '--xraypath',
#         str(xray_file)
#     )
#     result.assert_outcomes(failed=1)
#     result.stdout.fnmatch_lines([
#         '*Generated XRAY execution report file:*xray.json*',
#     ])
#     assert result.ret == 1
#     assert pytester.path.joinpath('report.json').exists()
#     with open(xray_file) as f:
#         data = json.load(f)
#
#     assert len(data['tests']) == 2
#     print(data['tests'])


# def test_xray_with_all_test_types(testdir):
#     testdir.makepyfile(textwrap.dedent(
#         """\
#         import pytest
#
#         @pytest.fixture
#         def error_fixture():
#             assert 0
#
#         @pytest.mark.xray('JIRA-1')
#         def test_ok():
#             print("ok")
#
#         @pytest.mark.xray('JIRA-2')
#         def test_fail():
#             assert 0
#
#         @pytest.mark.xray('JIRA-3')
#         def test_error(error_fixture):
#             pass
#
#         @pytest.mark.xray('JIRA-4')
#         def test_skip():
#             pytest.skip("skipping this test")
#
#         @pytest.mark.xray('JIRA-5')
#         def test_xfail():
#             pytest.xfail("xfailing this test")
#
#         @pytest.mark.xfail(reason="always xfail")
#         @pytest.mark.xray('JIRA-6')
#         def test_xpass():
#             pass
#         """))
#
#     result = testdir.runpytest(
#         '--xraypath',
#         '-v',
#     )
#
#     assert result.ret == 1
#     result.assert_outcomes(errors=1, failed=1, passed=1, skipped=1, xfailed=1, xpassed=1)
#     # assert path.exists()
#     with open(report_file) as file:
#         data = json.load(file)
#
#     xray_statuses = set((t['testKey'], t['status']) for t in data['tests'])
#     assert xray_statuses == {
#         ('JIRA-1', 'PASS'),
#         ('JIRA-2', 'FAIL'),
#         ('JIRA-3', 'FAIL'),
#         ('JIRA-4', 'ABORTED'),
#         ('JIRA-5', 'FAIL'),
#         ('JIRA-6', 'PASS')
#     }
#
#
# def test_jira_xray_plugin_multiple_ids(pytester: Pytester, marked_xray_pass):
#     result = pytester.runpytest('--xray-path')
#     result.assert_outcomes(passed=1)
#     result.stdout.fnmatch_lines([
#         '*Generated XRAY execution report file:*xray.json*',
#     ])
#     assert result.ret == 0
#     assert not result.errlines
#     assert xray_file.exists()
#     with open(xray_file) as f:
#         data = json.load(f)
#
#     assert len(data['tests']) == 2
#     assert data['tests'][0]['testKey'] == 'JIRA-1'
#     assert data['tests'][1]['testKey'] == 'JIRA-2'
