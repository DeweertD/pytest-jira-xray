import json
import os

from _pytest.config import ExitCode
from jsonschema import validators

import pytest
from _pytest.pytester import Pytester
from py._error import Error


def test_help_message(pytester):
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
    ]
)
def test_invalid_options(marked_xray_pass, pytester, options):
    report = pytester.runpytest(options)
    assert report.ret is ExitCode.USAGE_ERROR


@pytest.mark.parametrize(
    'options',
    [
        '--jira-url=https://jira.dummy.local:8080/',
        '--jiraurl=https://jira.dummy.local:8080/',
        '--xray-json=report.json',
        '--xrayjson=report.json',
    ]
)
def test_valid_options(marked_xray_pass, pytester, options):
    report = pytester.runpytest(options)
    assert report.ret is ExitCode.OK
    report.assert_outcomes(passed=1)

