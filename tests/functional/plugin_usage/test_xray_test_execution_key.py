import json

import pytest
from _pytest.config import ExitCode
from _pytest.pytester import Pytester


@pytest.mark.parametrize(
    'options,conftest',
    [
        pytest.param(('--xray-json', ''),
                     """
                     import pytest
                     """),
        pytest.param(('--xray-json', '--execution='),
                     """
                     import pytest
                     """),
        pytest.param(('--xray-json', '--execution='),
                     """
                     import pytest

                     def pytest_xray_execution_key():
                         return None
                     """),
        pytest.param(('--xray-json', '--execution='),
                     """
                     import pytest

                     def pytest_xray_execution_key():
                         return ''
                     """),
        pytest.param(('--xray-json', '--execution='),
                     """
                     import pytest

                     def pytest_xray_execution_key():
                         return []
                     """),
        pytest.param(('--xray-json', '--execution='),
                     """
                     import pytest

                     def pytest_xray_execution_key():
                         return {}
                     """),
        pytest.param(('--xray-json', '--execution='),
                     """
                     import pytest

                     def pytest_xray_execution_key():
                         return False
                     """),
        pytest.param(('--xray-json', '--execution='),
                     """
                     import pytest

                     def pytest_xray_execution_key():
                         return True
                     """),
        pytest.param(('--xray-json', '--execution='),
                     """
                     import pytest

                     def pytest_xray_execution_key():
                         return 0
                     """),
        pytest.param(('--xray-json', '--execution='),
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
def test_execution_key_hook_overrides_args(marked_xray_pass, pytester: Pytester, options: tuple, conftest: str):
    pytester.makeconftest(conftest)
    report = pytester.runpytest(*options)
    path = pytester.path.joinpath('report.json')
    assert report.ret is ExitCode.OK
    assert not report.errlines
    assert path.exists()
    with open(path) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'testExecutionKey' in xray_report
    assert xray_report['testExecutionKey'] == 'JIRA-1'


def test_execution_key_hook_can_modify_cli(marked_xray_pass, pytester: Pytester):
    pytester.makeconftest(
        """
        import pytest
        
        def pytest_xray_execution_key(execution_key):
            return f"{execution_key}-1"
        """)
    report = pytester.runpytest('--xray-json', '--execution=JIRAEX')
    path = pytester.path.joinpath('report.json')
    assert report.ret is ExitCode.OK
    assert not report.errlines
    assert path.exists()
    with open(path) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'testExecutionKey' in xray_report
    assert xray_report['testExecutionKey'] == 'JIRAEX-1'


@pytest.mark.parametrize(
    'conftest',
    [
        pytest.param("""
                     import pytest

                     def pytest_xray_execution_key():
                         return 'JIRA-1'
                     """),
        pytest.param("""
                     import pytest

                     def pytest_xray_execution_key():
                         return 'JIRA-1'
                     """),
        pytest.param("""
                     import pytest

                     def pytest_xray_execution_key():
                         return 'JIRA-1'
                     """),
    ]
)
def test_execution_key_hook(marked_xray_pass, pytester: Pytester, conftest: str):
    pytester.makeconftest(conftest)
    report = pytester.runpytest('--xray-json')
    path = pytester.path.joinpath('report.json')
    assert report.ret is ExitCode.OK
    assert not report.errlines
    assert path.exists()
    with open(path) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'testExecutionKey' in xray_report
    assert xray_report['testExecutionKey'] == 'JIRA-1'


@pytest.mark.parametrize('invalid_value', ["None", "[]", "''", pytest.param("", id="EMPTY"), "dict()"])
def test_invalid_execution_key_hook(marked_xray_pass, pytester: Pytester, invalid_value):
    pytester.makeconftest(f"""
                          import pytest
                            
                          def pytest_xray_execution_key():
                              return {invalid_value}
                          """)
    report = pytester.runpytest('--xray-json')
    assert report.ret is ExitCode.INTERNAL_ERROR


@pytest.mark.parametrize(
    'options, conftest',
    [
        pytest.param(('--xray-json=report.json', '--execution=JIRAEX-1'),
                     """
                     import pytest

                     def pytest_xray_execution_key():
                         return ''
                     """),
        pytest.param(('--xray-json=report.json', '--execution=JIRAEX-1'),
                     """
                     import pytest

                     def pytest_xray_execution_key():
                         return None
                     """),
        pytest.param(('--xray-json=report.json', '--execution=JIRAEX-1'),
                     """
                     import pytest

                     """),
    ]
)
def test_execution_key_command_line_config(marked_xray_pass, pytester, options, conftest):
    pytester.makeconftest(conftest)
    report = pytester.runpytest(*options)
    path = pytester.path.joinpath('report.json')
    assert report.ret is ExitCode.OK
    assert not report.errlines
    assert path.exists()
    with open(path) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'testExecutionKey' in xray_report
    assert xray_report['testExecutionKey'] == 'JIRAEX-1'


def test_invalid_execution_key_command_line_config(marked_xray_pass, pytester):
    report = pytester.runpytest('--xray-json=report.json', '--execution=')
    assert report.ret is ExitCode.INTERNAL_ERROR
