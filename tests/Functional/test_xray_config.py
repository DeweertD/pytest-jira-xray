from _pytest.pytester import Pytester
from _pytest.config import ExitCode

import pytest


def test_help_message(pytester: Pytester):
    result = pytester.runpytest(
        '--help',
    )
    result.stdout.fnmatch_lines([
        'Jira Xray report:',
        '*--execution=EXECUTION_KEY*',
        '*--test-plan=TEST_PLAN_KEY*',
        '*--xray-json=PATH*',
        '*--jira-url=URL*',
        '*--cloud*',
        '*--api-key=API_KEY*',
        '*--token=TOKEN*',
        '*--basic-auth=CLIENT_ENCODED*',
    ])


@pytest.mark.parametrize(
    'options',
    [
        '--jira-url',
        '--jiraurl',
        '--xray-json',
        '--xrayjson',
        '--execution',
        '--test-plan',
        '--api-key',
        '--token',
        '--basic-auth',
    ]
)
def test_invalid_options(marked_xray_pass, pytester: Pytester, options):
    report = pytester.runpytest(options)
    assert report.ret is ExitCode.USAGE_ERROR


@pytest.mark.parametrize(
    'options',
    [
        ('--jiraurl=https://jira.dummy.local:8080/', '--execution=PROJECT-1'),

        ('--jiraurl=https://jira.dummy.local:8080/', '--execution=PROJECT-1', '--test-plan=PROJECT-2'),

        ('--jiraurl=https://jira.dummy.local:8080/', '--execution=PROJECT-1', '--test-plan=PROJECT-2',
         '--api-key=AB213400ASDFSDGWEDA12314ADDNCE4DFS'),

        ('--jiraurl=https://jira.dummy.local:8080/', '--execution=PROJECT-1', '--test-plan=PROJECT-2',
         '--token=AB213400ASDFSDGWEDA12314ADDNCE4DFS'),

        ('--jiraurl=https://jira.dummy.local:8080/', '--execution=PROJECT-1', '--test-plan=PROJECT-2',
         '--basic-auth=firstname.lastname:password'),

        ('--jiraurl=https://jira.dummy.local:8080/', '--execution=PROJECT-1', '--test-plan=PROJECT-2', '--cloud'),

        ('--jiraurl=https://jira.dummy.local:8080/', '--execution=PROJECT-1', '--test-plan=PROJECT-2', '--cloud',
         '--api-key=AB213400ASDFSDGWEDA12314ADDNCE4DFS'),

        ('--jiraurl=https://jira.dummy.local:8080/', '--execution=PROJECT-1', '--test-plan=PROJECT-2', '--cloud',
         '--token=AB213400ASDFSDGWEDA12314ADDNCE4DFS'),

        ('--jiraurl=https://jira.dummy.local:8080/', '--execution=PROJECT-1', '--test-plan=PROJECT-2', '--cloud',
         '--basic-auth=firstname.lastname:password'),

        ('--xrayjson=report.json', '--execution=PROJECT-1'),

        ('--xrayjson=report.json', '--test-plan=PROJECT-2'),

        ('--xrayjson=report.json', '--execution=PROJECT-1', '--test-plan=PROJECT-2'),
    ]
)
def test_plugin_is_enabled_with_valid_options(marked_xray_pass, pytester: Pytester, options):
    report = pytester.runpytest(*options)
    assert report.ret is ExitCode.OK
    report.assert_outcomes(passed=1)


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
def test_execution_key_is_required_without_test_plan(marked_xray_pass, pytester: Pytester, options, conftest):
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
def test_execution_key_hook_sets_value(marked_xray_pass, pytester: Pytester, options, conftest):
    pytester.makeconftest(conftest)
    report = pytester.runpytest(*options)
    assert report.ret is ExitCode.OK


@pytest.mark.parametrize('options,conftest', [
    pytest.param(('--xray-json=report.json', '--execution=JIRA-1'),
                 """
                 import pytest
         
                 def pytest_xray_execution_key():
                     return None
                 """),
    pytest.param(('--xray-json=report.json', '--execution=JIRA-1'),
                 """
                 import pytest
         
                 def pytest_xray_execution_key():
                     return ''
                 """),
    pytest.param(('--xray-json=report.json', '--execution=JIRA-1'),
                 """
                 import pytest
         
                 def pytest_xray_execution_key():
                     return []
                 """),
    pytest.param(('--xray-json=report.json', '--execution=JIRA-1'),
                 """
                 import pytest
         
                 def pytest_xray_execution_key():
                     return {}
                 """),
    pytest.param(('--xray-json=report.json', '--execution=JIRA-1'),
                 """
                 import pytest
         
                 def pytest_xray_execution_key():
                     return False
                 """),
    pytest.param(('--xray-json=report.json', '--execution=JIRA-1'),
                 """
                 import pytest
         
                 def pytest_xray_execution_key():
                     return True
                 """),
    pytest.param(('--xray-json=report.json', '--execution=JIRA-1'),
                 """
                 import pytest
         
                 def pytest_xray_execution_key():
                     return 1
                 """),
    pytest.param(('--xray-json=report.json', '--execution=JIRA-1'),
                 """
                 import pytest
         
                 def pytest_xray_execution_key():
                     return 0
                 """),
    pytest.param(('--xray-json=report.json', ''),
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
])
def test_execution_key_is_used_if_available(marked_xray_pass, pytester: Pytester, options, conftest):
    pytester.makeconftest(conftest)
    report = pytester.runpytest(*options)
    assert report.ret is ExitCode.OK
