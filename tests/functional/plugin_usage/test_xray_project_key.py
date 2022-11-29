import json

import pytest
from _pytest.config import ExitCode
from _pytest.pytester import Pytester


def test_project_key_is_required(marked_xray_pass, pytester: Pytester):
    report = pytester.runpytest('--xray-json')
    assert report.ret is ExitCode.INTERNAL_ERROR


@pytest.mark.parametrize(
    'options, conftest',
    [
        pytest.param(('--xray-json=report.json', '--project=JIRAEX'),
                     """
                     import pytest

                     def pytest_xray_project():
                         return ''
                     """),
        pytest.param(('--xray-json=report.json', '--project=JIRAEX'),
                     """
                     import pytest

                     def pytest_xray_project():
                         return None
                     """),
        pytest.param(('--xray-json=report.json', '--project=JIRAEX'),
                     """
                     import pytest

                     """),
    ]
)
def test_project_key_command_line_config(marked_xray_pass, pytester, options, conftest):
    pytester.makeconftest(conftest)
    report = pytester.runpytest(*options)
    path = pytester.path.joinpath('report.json')
    assert report.ret is ExitCode.OK
    assert not report.errlines
    assert path.exists()
    with open(path) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert 'project' in xray_report['info']
    assert xray_report['info']['project'] == 'JIRAEX'


def test_invalid_project_key_command_line_config(pytester: Pytester, marked_xray_pass):
    report = pytester.runpytest('--xray-json', '--project=')
    assert report.ret is ExitCode.INTERNAL_ERROR


@pytest.mark.parametrize("conftest", [
    """
        import pytest

        @pytest.hookimpl
        def pytest_xray_project(project_key):
            return "JIRAEX"
        """,
])
def test_project_key_hook(pytester: Pytester, conftest, marked_xray_pass):
    pytester.makeconftest(conftest)
    report = pytester.runpytest('--xray-json')
    assert report.ret is ExitCode.OK
    report.assert_outcomes(passed=1)
    assert not report.errlines
    assert pytester.path.joinpath('report.json').exists()
    with open(pytester.path.joinpath("report.json")) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'tests' in xray_report
    assert len(xray_report['tests']) == 1
    assert 'project' in xray_report['info']
    assert xray_report['info']['project'] == 'JIRAEX'


@pytest.mark.parametrize(
    'options,conftest',
    [
        pytest.param(('--xray-json', '--project='),
                     """
                     import pytest

                     @pytest.hookimpl
                     def pytest_xray_project(project_key):
                         return None
                     """),
        pytest.param(('--xray-json', '--project='),
                     """
                     import pytest

                     @pytest.hookimpl
                     def pytest_xray_project(project_key):
                         return ''
                     """),
        pytest.param(('--xray-json', '--project='),
                     """
                     import pytest

                     @pytest.hookimpl
                     def pytest_xray_project(project_key):
                         return []
                     """),
        pytest.param(('--xray-json', '--project='),
                     """
                     import pytest

                     @pytest.hookimpl
                     def pytest_xray_project(project_key):
                         return {}
                     """),
        pytest.param(('--xray-json', '--project='),
                     """
                     import pytest

                     @pytest.hookimpl
                     def pytest_xray_project(project_key):
                         return False
                     """),
        pytest.param(('--xray-json', '--project='),
                     """
                     import pytest

                     @pytest.hookimpl
                     def pytest_xray_project(project_key):
                         return True
                     """),
        pytest.param(('--xray-json', '--project='),
                     """
                     import pytest

                     @pytest.hookimpl
                     def pytest_xray_project(project_key):
                         return 0
                     """),
        pytest.param(('--xray-json', '--project='),
                     """
                     import pytest

                     @pytest.hookimpl
                     def pytest_xray_project(project_key):
                         return 1
                     """),
    ]
)
def test_invalid_project_key_hook(marked_xray_pass, pytester: Pytester, options: tuple,
                                        conftest: str):
    pytester.makeconftest(conftest)
    report = pytester.runpytest(*options)
    assert report.ret is ExitCode.INTERNAL_ERROR


@pytest.mark.parametrize(
    'options, conftest',
    [
        pytest.param(('--xray-json', '--project=JIRA-2'),
                     """
                     import pytest

                     def pytest_xray_project(project_key):
                         return 'JIRAEX'
                     """),
        pytest.param(('--xray-json', '--project='),
                     """
                     import pytest

                     def pytest_xray_project(project_key):
                         return 'JIRAEX'
                     """),
        pytest.param(('--xray-json',),
                     """
                     import pytest

                     def pytest_xray_project(project_key):
                         return 'JIRAEX'
                     """),
    ]
)
def test_project_key_hook_overrides_args(marked_xray_pass, pytester: Pytester, options: tuple, conftest: str):
    pytester.makeconftest(conftest)
    report = pytester.runpytest(*options)
    path = pytester.path.joinpath('report.json')
    assert report.ret is ExitCode.OK
    assert not report.errlines
    assert path.exists()
    with open(path) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'info' in xray_report
    assert 'project' in xray_report['info']
    assert xray_report['info']['project'] == 'JIRAEX'


def test_project_key_hook_can_modify_cli(marked_xray_pass, pytester: Pytester):
    pytester.makeconftest(
        """
        import pytest

        def pytest_xray_project(project_key):
            return f"{project_key}-1"
        """)
    report = pytester.runpytest('--xray-json', '--project=JIRAEX')
    path = pytester.path.joinpath('report.json')
    assert report.ret is ExitCode.OK
    assert not report.errlines
    assert path.exists()
    with open(path) as f:
        xray_report = json.load(f)
    assert xray_report is not None
    assert 'info' in xray_report
    assert 'project' in xray_report['info']
    assert xray_report['info']['project'] == 'JIRAEX-1'
