from collections import defaultdict

import pytest
from _pytest import timing
from _pytest.config import Config, ExitCode
from _pytest.config.argparsing import Parser
from _pytest.main import Session
from _pytest.mark import Mark
from _pytest.nodes import Item
from _pytest.reports import TestReport
from _pytest.stash import StashKey
from _pytest.terminal import TerminalReporter

import os
from pathlib import Path
from typing import List, Tuple, Union, Optional, Dict

from datetime import datetime, timezone

from requests.auth import AuthBase

from pytest_jira_xray.constant import (
    JIRA_XRAY_FLAG,
    PYTEST_PLUGIN,
    XRAY_TEST_PLAN_ID,
    XRAY_EXECUTION_KEY,
    JIRA_CLOUD,
    JIRA_API_KEY,
    JIRA_TOKEN,
    JIRA_CLIENT_SECRET_AUTH,
    XRAY_PATH,
    XRAY_MARKER,
    TEST_EXECUTION_ENDPOINT,
    TEST_EXECUTION_ENDPOINT_CLOUD,
    XRAY_ALLOW_DUPLICATE_IDS
)
from pytest_jira_xray.exceptions import XrayError
from pytest_jira_xray.file_publisher import FilePublisher
from pytest_jira_xray.helper import (
    get_bearer_auth,
    get_api_key_auth,
    get_basic_auth,
    get_api_token_auth,
    _URLOrBool
)
from pytest_jira_xray.test_run import Status, STATUS_STR_MAPPER_CLOUD, STATUS_STR_MAPPER_JIRA, XrayTest
from pytest_jira_xray.test_execution import TestExecution, TestExecutionInfo
from pytest_jira_xray import hooks
from pytest_jira_xray.xray_publisher import (
    ClientSecretAuth,
    ApiKeyAuth,
    XrayPublisher,
    TokenAuth
)

xray_key = StashKey['XrayReport']()


def pytest_addoption(parser: Parser):
    xray = parser.getgroup('Jira Xray report')
    xray.addoption(
        *JIRA_XRAY_FLAG,
        action=_URLOrBool,
        metavar='URL',
        default=False,
        const=True,
        nargs='?',
        help='Upload test results to JIRA XRAY, provide a URL as the desired upload endpoint'
    )
    xray.addoption(
        *JIRA_CLOUD,
        action='store_true',
        default=False,
        help='Use with JIRA XRAY could server'
    )
    xray.addoption(
        *JIRA_API_KEY,
        action='store_true',
        default=False,
        help='Use API Key authentication',
    )
    xray.addoption(
        *JIRA_TOKEN,
        action='store_true',
        default=False,
        help='Use token authentication',
    )
    xray.addoption(
        *JIRA_CLIENT_SECRET_AUTH,
        action='store_true',
        default=False,
        help='Use client secret authentication',
    )
    xray.addoption(
        *XRAY_EXECUTION_KEY,
        action='store',
        metavar='TestExecutionKey',
        default=None,
        help='Set the XRAY Test Execution Key'
    )
    xray.addoption(
        *XRAY_TEST_PLAN_ID,
        action='store',
        metavar='TestPlanKey',
        default=None,
        help='XRAY Test Plan ID'
    )
    xray.addoption(
        *XRAY_PATH,
        action='store',
        metavar='path',
        default=False,
        const='report.json',
        nargs='?',
        help='Create a JSON report file at the given path, can be left blank to use the default report.json file name'
    )
    xray.addoption(
        *XRAY_ALLOW_DUPLICATE_IDS,
        action='store_true',
        default=False,
        help='Allow test ids to be present on multiple pytest tests'
    )


def pytest_addhooks(pluginmanager):
    pluginmanager.add_hookspecs(hooks)


def pytest_configure(config: Config) -> None:
    config.addinivalue_line(
        'markers', f'{XRAY_MARKER}(JIRA_ID): mark test with JIRA XRAY test case ID'
    )

    if (config.getoption('xray_json') is False
        and config.getoption('jira_xray') is False) \
            or hasattr(config, 'workerinput'):
        return

    xray_path = config.getoption('xray_json')
    file_publisher = FilePublisher(xray_path)

    # endpoint = TEST_EXECUTION_ENDPOINT
    # if config.getoption('cloud'):
    #     endpoint = TEST_EXECUTION_ENDPOINT_CLOUD
    #
    # options = get_basic_auth()
    # auth: Union[AuthBase, Tuple[str, str]] = (options['USER'], options['PASSWORD'])
    # if config.getoption('client_secret_auth'):
    #     options = get_bearer_auth()
    #     auth = ClientSecretAuth(
    #         options['BASE_URL'],
    #         options['CLIENT_ID'],
    #         options['CLIENT_SECRET']
    #     )
    # elif config.getoption(JIRA_API_KEY[0]):
    #     options = get_api_key_auth()
    #     auth = ApiKeyAuth(options['API_KEY'])
    # elif config.getoption(JIRA_TOKEN[0]):
    #     options = get_api_token_auth()
    #     auth = TokenAuth(options['TOKEN'])
    #
    # xray_publisher = XrayPublisher(  # type: ignore
    #     base_url=options['BASE_URL'],
    #     endpoint=endpoint,
    #     auth=auth,
    #     verify=options['VERIFY']
    # )

    plugin = XrayPlugin(config, None, file_publisher)
    config.pluginmanager.register(plugin=plugin, name=PYTEST_PLUGIN)


@pytest.hookimpl(trylast=True)
def pytest_xray_execution_key(execution_key: str) -> str:
    return execution_key


@pytest.hookimpl(trylast=True)
def pytest_xray_project(project_key):
    """Called before adding the project to the report"""


@pytest.hookimpl(trylast=True)
def pytest_xray_summary():
    return "Automated test execution report from the pytest-jira-xray plugin"


@pytest.hookimpl(trylast=True)
def pytest_xray_description(report_description):
    """Called before adding the description to the report"""


@pytest.hookimpl(trylast=True)
def pytest_xray_fix_version(*fix_version):
    """Called before adding the fix_version to the report"""


@pytest.hookimpl(trylast=True)
def pytest_xray_revision(revision):
    """Called before adding the revision to the report"""


@pytest.hookimpl(trylast=True)
def pytest_xray_user(user_id):
    """Called before adding the user to the report"""


@pytest.hookimpl(trylast=True)
def pytest_xray_test_plan_key(test_plan_key):
    """Called before adding the test plan key to the report"""


@pytest.hookimpl(trylast=True)
def pytest_xray_test_environments(*test_environments):
    """Called before adding the test environments to the report"""


@pytest.hookimpl(trylast=True)
def pytest_xray_status_mapping(node_id, report_outcome, failure_when, wasxfail):
    if report_outcome == "failed":
        if wasxfail:
            return Status.PASS
        elif failure_when != "call":
            return Status.ABORTED
        return Status.FAIL
    elif report_outcome == "skipped":
        return Status.ABORTED
    return Status.PASS


class XrayPlugin:

    def __init__(self, config, xray_publisher=None, file_publisher=None):
        self.config = config
        self.xray_publisher = xray_publisher
        self.file_publisher = file_publisher
        self.reports: dict[str, list[TestReport]] = defaultdict(list)
        self.test_execution: TestExecution = self._generate_test_execution()
        self._xray_tests: list[XrayTest] = list()
        #
        # self.test_execution_id: str = self.config.getoption(XRAY_EXECUTION_KEY[0])
        # self.test_plan_id: str = self.config.getoption(XRAY_TEST_PLAN_ID)
        # self.is_cloud_server: str = self.config.getoption(JIRA_CLOUD)
        # self.allow_duplicate_ids: bool = self.config.getoption(
        #     XRAY_ALLOW_DUPLICATE_IDS
        # )
        # logfile = self.config.getoption(XRAY_PATH)
        # self.logfile: str = self._get_normalize_logfile(logfile) if logfile else None
        # self.test_keys: Dict[str, List[str]] = {}  # store nodeid and TestId
        # self.issue_id = None
        # self.exception = None
        # self.status_str_mapper = STATUS_STR_MAPPER_JIRA
        # if self.is_cloud_server:
        #     self.status_str_mapper = STATUS_STR_MAPPER_CLOUD

    # @staticmethod
    # def _get_normalize_logfile(logfile: str) -> str:
    #     logfile = os.path.expanduser(os.path.expandvars(logfile))
    #     logfile = os.path.normpath(os.path.abspath(logfile))
    #     return logfile
    #
    # def _associate_marker_metadata_for_items(self, items: List[Item]) -> None:
    #     """Store XRAY test id for test item."""
    #     jira_ids: List[str] = []
    #     duplicated_jira_ids: List[str] = []
    #
    #     for item in items:
    #         marker = self._get_xray_marker(item)
    #         if not marker:
    #             continue
    #
    #         test_keys: List[str]
    #         if isinstance(marker.args[0], str):
    #             test_keys = [marker.args[0]]
    #         elif isinstance(marker.args[0], list):
    #             test_keys = list(marker.args[0])
    #         else:
    #             raise XrayError('xray marker can only accept strings or lists')
    #
    #         for test_key in test_keys:
    #             if test_key in jira_ids:
    #                 duplicated_jira_ids.append(test_key)
    #             else:
    #                 jira_ids.append(test_key)
    #
    #         self.test_keys[item.nodeid] = test_keys
    #
    #         if duplicated_jira_ids and not self.allow_duplicate_ids:
    #             raise XrayError(f'Duplicated test case ids: {duplicated_jira_ids}')

    def pytest_sessionstart(self):
        self.test_execution.info.start_date = timing.time()

    def pytest_runtest_logreport(self, report: TestReport):
        self.reports[report.nodeid].append(report)

    def pytest_sessionfinish(self, session: Session):
        self.test_execution.info.finish_date = timing.time()
        self._finalize(session)
        self.file_publisher.publish(self.test_execution.to_dict())
        # self.xray_publisher.publish(self.test_execution.to_dict())

    def _finalize(self, session: Session):
        # status = self._get_status_from_report(report)
        # if status is None:
        #     return
        #
        # test_keys = self._get_test_keys_for_nodeid(report.nodeid)
        # if test_keys is None:
        #     return
        #
        # for test_key in test_keys:
        #     new_test_case = XrayTest(
        #         test_key=test_key,
        #         status=status,
        #         comment=report.longreprtext,
        #         status_str_mapper=self.status_str_mapper
        #     )
        #     try:
        #         test_case = self.test_execution.find_test_case(test_key)
        #     except KeyError:
        #         self.test_execution.add_test_case(new_test_case)
        #     else:
        #         test_case += new_test_case
        for test_name, test_reports in self.reports.items():

            report_outcome = "passed"
            wasxfail = False
            failure_when = None
            full_text = ""
            duration = 0.0

            for test_report in test_reports:
                full_text += test_report.longreprtext
                duration += getattr(test_report, "duration", 0.0)

                if (
                        test_report.outcome not in ("passed", "rerun")
                        and report_outcome == "passed"
                ):
                    report_outcome = test_report.outcome
                    failure_when = test_report.when

                if hasattr(test_report, "wasxfail"):
                    wasxfail = True

            xray_test_dict = dict(
                status=session.config.hook.pytest_xray_status_mapping(node_id=test_report.nodeid,
                                                                      report_outcome=report_outcome,
                                                                      failure_when=failure_when,
                                                                      wasxfail=wasxfail))
            if test_report.test_keys:
                xray_tests = [XrayTest(test_key=test_key, **xray_test_dict) for test_key in test_report.test_keys]
            else:
                xray_tests = [XrayTest(test_info=XrayTestInfo(definition=test_report.nodeid), *xray_test_dict)]
            self._xray_tests += xray_tests

    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item: Item):
        outcome = yield
        report = outcome.get_result()
        test_key_markers = item.iter_markers(name="xray")
        report.test_keys = [test_key for test_key_marker in test_key_markers for test_key in test_key_marker.args]
        node = item.obj
        report.description = node.__doc__.strip() if node.__doc__ else node.__name__

    # def pytest_collection_modifyitems(self, config: Config, items: List[Item]) -> None:
    #     self._associate_marker_metadata_for_items(items)

    # def pytest_sessionfinish(self, session: pytest.Session) -> None:
    #     results = self.test_execution.to_dict()
    #     session.config.pluginmanager.hook.pytest_xray_results(
    #         results=results, session=session
    #     )
    #     self.test_execution.finish_date = datetime.now(tz=timezone.utc)
    #     try:
    #         self.issue_id = self.publisher.publish(results)
    #     except XrayError as exc:
    #         self.exception = exc

    # def pytest_terminal_summary(
    #         self, terminalreporter: TerminalReporter, exitstatus: ExitCode, config: Config
    # ) -> None:
    #     if self.exception:
    #         terminalreporter.ensure_newline()
    #         terminalreporter.section('Jira XRAY', sep='-', red=True, bold=True)
    #         terminalreporter.write_line('Could not publish results to Jira XRAY!')
    #         if self.exception.message:
    #             terminalreporter.write_line(self.exception.message)
    #     else:
    #         if self.issue_id and self.logfile:
    #             terminalreporter.write_sep(
    #                 '-', f'Generated XRAY execution report file: {Path(self.logfile).absolute()}'
    #             )
    #         elif self.issue_id:
    #             terminalreporter.write_sep(
    #                 '-', f'Uploaded results to JIRA XRAY. Test Execution Id: {self.issue_id}'
    #             )

    @staticmethod
    def _get_xray_marker(item: Item) -> Optional[Mark]:
        return item.get_closest_marker(XRAY_MARKER)

    def _generate_test_execution(self) -> TestExecution:
        execution_params = dict()

        test_execution_key = self.config.getoption('xray_execution', None)
        hook_execution_key = self.config.hook.pytest_xray_execution_key(execution_key=test_execution_key)
        if hook_execution_key is not None and bool(hook_execution_key) and isinstance(hook_execution_key, str):
            execution_params['test_execution_key'] = hook_execution_key

        info_params = self._generate_test_execution_info_params()
        if info_params is not None:
            execution_params['info'] = TestExecutionInfo(**info_params)

        if not execution_params:
            raise ValueError("Xray report requires either an execution issue key, or a project key in which to "
                             "generate a new execution")

        return TestExecution(**execution_params)

    def _generate_test_execution_info_params(self) -> Union[dict, None]:
        info_params = dict()

        test_execution_project = self.config.getoption('project_execution', None)
        hook_execution_project = self.config.hook.pytest_xray_project(project_key=test_execution_project)
        if hook_execution_project is not None \
                and bool(hook_execution_project) \
                and isinstance(hook_execution_project, str):
            info_params['project'] = hook_execution_project

        hook_execution_summary = self.config.hook.pytest_xray_summary(report_summary=None)
        if hook_execution_summary is not None \
                and bool(hook_execution_summary) \
                and isinstance(hook_execution_summary, str):
            info_params['summary'] = hook_execution_summary

        if not info_params.keys():
            return None
        return info_params
