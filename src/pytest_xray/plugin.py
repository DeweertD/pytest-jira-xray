# Copyright (C) 2021 fundakol (https://github.com/fundakol)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from argparse import Action
import urllib.parse
from typing import Callable, List

import pytest

from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.fixtures import FixtureRequest
from _pytest.nodes import Item
from _pytest.stash import StashKey

from .xray_report import XrayReport
from .xray_result import XrayTest

XRAY_EXECUTION_KEY = ('--execution')
XRAY_JSON = ('--xrayjson', '--xray-json')
XRAY_TEST_PLAN_KEY = ('--testplan', '--test-plan')
JIRA_API_KEY = ('--apikey', '--api-key')
JIRA_TOKEN = '--token'
JIRA_CLIENT_SECRET = ('--clientsecret', '--client-secret')
JIRA_SERVER = ('--serverurl', '--server-url')
JIRA_CLOUD = '--cloud'
ENV_TEST_EXECUTION_TEST_ENVIRONMENTS = 'XRAY_EXECUTION_TEST_ENVIRONMENTS'
ENV_TEST_EXECUTION_FIX_VERSION = 'XRAY_EXECUTION_FIX_VERSION'
ENV_TEST_EXECUTION_REVISION = 'XRAY_EXECUTION_REVISION'
ENV_TEST_EXECUTION_SUMMARY = 'XRAY_EXECUTION_SUMMARY'
ENV_TEST_EXECUTION_DESC = 'XRAY_EXECUTION_DESC'
ENV_NAME = 'XRAY_API_BASE_URL'
DC_ENDPOINT = '/rest/raven/2.0/import/execution'
CLOUD_ENDPOINT = '/api/v2/import/execution'

xray_key = StashKey['XrayReport']()
requirement_key = StashKey[list[str]]()
description_key = StashKey[str]()


def pytest_addoption(parser: Parser) -> None:
    xray = parser.getgroup('Jira Xray report')
    xray.addoption(
        *XRAY_EXECUTION_KEY,
        action='store',
        metavar='ExecutionId',
        default=None,
        help='Set the XRAY Test Execution Key'
    )
    xray.addoption(
        *XRAY_TEST_PLAN_KEY,
        action='store',
        metavar='TestPlanId',
        default=None,
        help='XRAY Test Plan Key'
    )
    xray.addoption(
        *JIRA_SERVER,
        action=_URLOrBool,
        default=False,
        help='Upload test results to the self hosted JIRA server through the XRAY results importer endpoint'
    )
    xray.addoption(
        JIRA_CLOUD,
        action='store_true',
        help='Set the XRAY results importer endpoint for JIRA Cloud'
    )
    xray.addoption(
        *XRAY_JSON,
        action='store',
        default=False,
        help='Store the custom Xray JSON results file in the provided file',
    )
    xray.addoption(
        *JIRA_API_KEY,
        action='store',
        default=False,
        help='Use API Key authentication',
    )
    xray.addoption(
        JIRA_TOKEN,
        action='store',
        default=False,
        help='Use token authentication',
    )
    xray.addoption(
        *JIRA_CLIENT_SECRET,
        action='store',
        default=False,
        help='Use client secret authentication',
    )


def pytest_configure(config: Config) -> None:
    config.addinivalue_line(
        'markers', 'xray(ISSUE_KEY): mark test with Jira issue key'
    )
    config.addinivalue_line(
        'markers', 'requirement(*ISSUE_KEY): Add Jira issue key(s) for requirements which are validated by the marked '
                   'test. Xray will create a "TESTS" -> "IS TESTED BY" issue link in the "TEST" -> "REQUIREMENT" '
                   'direction '
    )
    config.addinivalue_line(
        'markers', 'test_summary(SUMMARY): Set custom summary for the test'
    )
    config.addinivalue_line(
        'markers', 'test_description(DESCRIPTION): Give test a custom description'
    )

    if (config.getoption(XRAY_JSON[0], None) is not None
        or config.getoption(JIRA_SERVER[0], None) is not None) \
            and not hasattr(config, 'workerinput'):
        file_path = config.getoption(XRAY_JSON[0], None)
        server_url = config.getoption(JIRA_SERVER[0], None)
        config.stash[xray_key] = XrayReport(file_path, server_url, config)
        config.pluginmanager.register(plugin=config.stash[xray_key], name='pytest_xray')


def pytest_unconfigure(config: Config) -> None:
    xray_report = config.stash.get(xray_key, None)
    if xray_report:
        del config.stash[xray_key]
        config.pluginmanager.unregister(xray_report)


# def pytest_collection_modifyitems(items: List[Item]) -> None:
#     for item in items:
#         item.stash[]


# TODO Add fixtures for recording test info properties
@pytest.fixture
def record_requirement(request: FixtureRequest) -> Callable[[str], None]:
    """Add extra requirement links to the calling test.
    Example::
        def test_function(record_requirement):
            record_requirement("example_project-123", "example_project-124", ...)
    """

    # Declare noop
    def add_req_noop(*args: str) -> None:
        pass

    req_func = add_req_noop

    xray = request.config.stash.get(xray_key, None)
    if xray is not None:
        test_reporter: XrayTest = xray.test_reporter(request.node.nodeid)
        req_func = test_reporter.add_requirement

    return req_func


class _URLOrBool(Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        print('%r %r %r' % (namespace, values, option_string))
        if values is False or values.upper() in ("FALSE", "F"):
            setattr(namespace, self.dest, False)
            return
        if values is True or values is None or values.upper() in ("TRUE", "T", ""):
            setattr(namespace, self.dest, True)
            return
        setattr(namespace, self.dest, str(values))


def _validate_url(url) -> str:
    valid_schemes = ("http", "https")
    url = urllib.parse.urlparse(url)
    if url.netloc == "":
        url = urllib.parse.urlparse(f"https://{urllib.parse.urlunparse(url)}")
    elif url.scheme != "" and url.scheme not in valid_schemes:
        raise ValueError(
            f"URL Scheme was not an expected REST compatible scheme, got {url.scheme}, expected one of {valid_schemes}")
    elif url.scheme == "":
        url = urllib.parse.urlparse(f"https:{urllib.parse.urlunparse(url)}")
    return urllib.parse.urlunparse(url)
