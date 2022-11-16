import json
import textwrap

import pytest
from _pytest.config import ExitCode
from _pytest.pytester import Pytester


@pytest.mark.parametrize(
    'options,conftest',
    [
        pytest.param(('--xray-json=report.json', ''),
                     """
                     import pytest
                     """),
        pytest.param(('--xray-json=report.json', '--execution='),
                     """
                     import pytest
                     """),
        pytest.param(('--xray-json=report.json', '--execution='),
                     """
                     import pytest

                     def pytest_xray_execution_key():
                         return None
                     """),
        pytest.param(('--xray-json=report.json', '--execution='),
                     """
                     import pytest

                     def pytest_xray_execution_key():
                         return ''
                     """),
        pytest.param(('--xray-json=report.json', '--execution='),
                     """
                     import pytest

                     def pytest_xray_execution_key():
                         return []
                     """),
        pytest.param(('--xray-json=report.json', '--execution='),
                     """
                     import pytest

                     def pytest_xray_execution_key():
                         return {}
                     """),
        pytest.param(('--xray-json=report.json', '--execution='),
                     """
                     import pytest

                     def pytest_xray_execution_key():
                         return False
                     """),
        pytest.param(('--xray-json=report.json', '--execution='),
                     """
                     import pytest

                     def pytest_xray_execution_key():
                         return True
                     """),
        pytest.param(('--xray-json=report.json', '--execution='),
                     """
                     import pytest

                     def pytest_xray_execution_key():
                         return 0
                     """),
        pytest.param(('--xray-json=report.json', '--execution='),
                     """
                     import pytest

                     def pytest_xray_execution_key():
                         return 1
                     """),
    ]
)
def test_execution_key_is_required_without_test_plan(marked_xray_pass, pytester: Pytester, options: tuple,
                                                     conftest: str):
    pytester.makeconftest(conftest)
    report = pytester.runpytest(*options)
    assert report.ret is ExitCode.INTERNAL_ERROR


@pytest.mark.parametrize(
    'options,conftest',
    [
        pytest.param(('--xray-json=report.json', '--execution=JIRA-2'),
                     """
                     import pytest

                     def pytest_xray_execution_key():
                         return 'JIRA-1'
                     """),
        pytest.param(('--xray-json=report.json', '--execution='),
                     """
                     import pytest

                     def pytest_xray_execution_key():
                         return 'JIRA-1'
                     """),
        pytest.param(('--xray-json=report.json', ''),
                     """
                     import pytest

                     def pytest_xray_execution_key():
                         return 'JIRA-1'
                     """),
    ]
)
def test_execution_key_hook_sets_value(marked_xray_pass, pytester: Pytester, options: tuple, conftest: str):
    pytester.makeconftest(conftest)
    report = pytester.runpytest(*options)
    assert report.ret is ExitCode.OK


def test_if_user_can_modify_results_with_hooks(xray_tests):
    xray_file = xray_tests.tmpdir.join('xray.json')
    xray_tests.makeconftest("""
        def pytest_xray_results(results):
            results['info']['user'] = 'Test User'
    """)
    result = xray_tests.runpytest('--jira-xray', '--xraypath', str(xray_file))
    assert result.ret == 0
    xray_result = json.load(xray_file.open())
    assert 'user' in xray_result['info']
    assert xray_result['info']['user'] == 'Test User'


def test_if_tests_without_xray_id_are_not_included(testdir):
    testdir.makepyfile(textwrap.dedent(
        """\
        import pytest

        @pytest.mark.xray('JIRA-1')
        def test_pass():
            assert True

        def test_pass_without_id():
            assert True
        """)
    )

    report_file = testdir.tmpdir / 'xray.json'

    result = testdir.runpytest(
        '--jira-xray',
        f'--xraypath={report_file}',
        '-v',
    )

    assert result.ret == 0
    result.assert_outcomes(passed=2)
    assert report_file.exists()
    with open(report_file) as file:
        data = json.load(file)

    xray_statuses = set((t['testKey'], t['status']) for t in data['tests'])
    assert xray_statuses == {
        ('JIRA-1', 'PASS'),
    }


def test_duplicated_ids(testdir):
    testdir.makepyfile(textwrap.dedent(
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

    report_file = testdir.tmpdir / 'xray.json'

    result = testdir.runpytest(
        '--jira-xray',
        f'--xraypath={report_file}',
        '-v',
    )

    assert result.ret == 3
    assert 'Duplicated test case ids' in str(result.stdout)

    result = testdir.runpytest(
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
