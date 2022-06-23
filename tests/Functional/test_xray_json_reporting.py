from _pytest.config import ExitCode
from _pytest.pytester import Pytester


def test_report_exists(pytester: Pytester, marked_xray_pass):
    report = pytester.runpytest('--xrayjson=report.json --execution=JIRA-1')
    assert report.ret is ExitCode.OK
    report.assert_outcomes(passed=1)
    assert not report.errlines
    assert pytester.path.joinpath('report.json').exists()


def test_multiple_ids(xray_tests_multi):
    xray_file = xray_tests_multi.tmpdir.join('xray.json')
    result = xray_tests_multi.runpytest('--jira-xray', '--xraypath', str(xray_file))
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


def test_multiple_ids_fail(xray_tests_multi_fail):
    xray_file = xray_tests_multi_fail.tmpdir.join('xray.json')
    result = xray_tests_multi_fail.runpytest(
        '--jira-xray',
        '--xraypath',
        str(xray_file)
    )
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        '*Generated XRAY execution report file:*xray.json*',
    ])
    assert result.ret == 1
    assert xray_file.exists()
    with open(xray_file) as f:
        data = json.load(f)

    assert len(data['tests']) == 2
    print(data['tests'])


def test_xray_with_all_test_types(pytester):
    pytester.makepyfile(textwrap.dedent(
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
    report_file = pytester.tmpdir / 'xray.json'

    result = pytester.runpytest(
        '--jira-xray',
        f'--xraypath={report_file}',
        '-v',
    )

    assert result.ret == 1
    result.assert_outcomes(errors=1, failed=1, passed=1, skipped=1, xfailed=1, xpassed=1)
    assert report_file.exists()
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


def test_non_marked_tests(pytester, anonymous_xray_pass):
    report = pytester.runpytest('--xrayjson=report.json')
    assert report.ret is ExitCode.OK
    report.assert_outcomes(passed=1)
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert hasattr(xray_report, 'tests')
    assert len(xray_report['tests']) == 1
    assert not hasattr(xray_report['tests'][0], 'test_key')
    assert hasattr(xray_report['tests'][0], 'test_info')
    assert hasattr(xray_report['tests'][0]['test_info'], 'test_type')


def test_duplicated_ids(pytester):
    pytester.makepyfile(textwrap.dedent(
        """\
        import pytest

        @pytest.mark.xray('JIRA-1')
        def test_pass():
            assert True

        @pytest.mark.xray('JIRA-1')
        def test_pass_2():
            assert False
        """)
    )

    report_file = pytester.tmpdir / 'xray.json'

    result = pytester.runpytest(
        '--jira-xray',
        f'--xraypath={report_file}',
        '-v',
    )

    assert result.ret == 3
    assert 'Duplicated test case ids' in str(result.stdout)

    result = pytester.runpytest(
        '--jira-xray',
        '--allow-duplicate-ids',
        f'--xraypath={report_file}',
        '-v',
    )

    assert result.ret == 1
    assert 'Duplicated test case ids' not in str(result.stdout)

    result.assert_outcomes(passed=1, failed=1)
    assert report_file.exists()
    with open(report_file) as file:
        data = json.load(file)

    xray_statuses = set((t['testKey'], t['status']) for t in data['tests'])
    assert xray_statuses == {
        ('JIRA-1', 'FAIL'),
    }
