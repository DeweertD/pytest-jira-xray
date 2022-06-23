import json
import os

from _pytest.config import ExitCode

import pytest
from _pytest.pytester import Pytester
from py._error import Error


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
        ('--jiraurl=https://jira.dummy.local:8080/', '--execution=PROJECT-1', '--test-plan=PROJECT-2', '--api-key=AB213400ASDFSDGWEDA12314ADDNCE4DFS'),
        ('--jiraurl=https://jira.dummy.local:8080/', '--execution=PROJECT-1', '--test-plan=PROJECT-2', '--token=AB213400ASDFSDGWEDA12314ADDNCE4DFS'),
        ('--jiraurl=https://jira.dummy.local:8080/', '--execution=PROJECT-1', '--test-plan=PROJECT-2', '--basic-auth=firstname.lastname:password'),
        ('--jiraurl=https://jira.dummy.local:8080/', '--execution=PROJECT-1', '--test-plan=PROJECT-2', '--cloud'),
        ('--jiraurl=https://jira.dummy.local:8080/', '--execution=PROJECT-1', '--test-plan=PROJECT-2', '--cloud', '--api-key=AB213400ASDFSDGWEDA12314ADDNCE4DFS'),
        ('--jiraurl=https://jira.dummy.local:8080/', '--execution=PROJECT-1', '--test-plan=PROJECT-2', '--cloud', '--token=AB213400ASDFSDGWEDA12314ADDNCE4DFS'),
        ('--jiraurl=https://jira.dummy.local:8080/', '--execution=PROJECT-1', '--test-plan=PROJECT-2', '--cloud', '--basic-auth=firstname.lastname:password'),
        ('--xrayjson=report.json', '--execution=PROJECT-1'),
        ('--xrayjson=report.json', '--test-plan=PROJECT-2'),
        ('--xrayjson=report.json', '--execution=PROJECT-1', '--test-plan=PROJECT-2'),
        ('--xrayjson=report.json', '--execution=PROJECT-1'),
        ('--xray-json=report.json', '--execution=PROJECT-1'),
        ('--xray-json=report.json', '--execution=PROJECT-1'),
        ('--xray-json=report.json', '--execution=PROJECT-1'),
        ('--xray-json=report.json', '--execution=PROJECT-1')
    ]
)
def test_plugin_is_enabled_with_valid_options(marked_xray_pass, pytester: Pytester, options):
    report = pytester.runpytest(*options)
    assert report.ret is ExitCode.OK
    report.assert_outcomes(passed=1)


@pytest.mark.parametrize(
    'options,conftest',
    [
        pytest.param(('--xray-json=report.json', '--execution=JIRA-1'), """
        import pytest
        
        pytest_set_execution_key(execution):
            return ''
        """),
        pytest.param(('--xray-json=report.json', '--execution='), """
        
        """),
        pytest.param(('--xray-json=report.json', '--execution='), """
        
        """),
        pytest.param(('--xray-json=report.json', '--execution='), """
        
        """),
        pytest.param(('--xray-json=report.json', ''), """
        
        """),
        pytest.param(('--xray-json=report.json', ''), """
        
        """),
        pytest.param(('--xray-json=report.json', ''), """
        
        """),
        pytest.param(('--xray-json=report.json', ''), """
        
        """)
    ]
)
def test_execution_key_is_required(marked_xray_pass, pytester: Pytester, options, conftest):
    pytester.makeconftest(conftest)
    report = pytester.runpytest(options)
    assert report.ret is ExitCode.USAGE_ERROR

