import json
import math
from collections import defaultdict

import pytest
from _pytest import timing
from _pytest.config import Config, ExitCode
from _pytest.config.argparsing import Parser
from _pytest.main import Session
from _pytest.mark import Mark
from _pytest.nodes import Item
from _pytest.reports import TestReport
from _pytest.runner import CallInfo
from _pytest.stash import StashKey
from _pytest.terminal import TerminalReporter

import os
from pathlib import Path
from typing import List, Tuple, Union, Optional, Dict

from pytest_jira_xray.constant import (
    XRAY_API,
    PYTEST_PLUGIN,
    XRAY_TEST_PLAN_KEY,
    XRAY_EXECUTION_KEY,
    JIRA_CLOUD,
    JIRA_API_KEY,
    JIRA_TOKEN,
    JIRA_CLIENT_SECRET_AUTH,
    XRAY_JSON,
    XRAY_MARKER,
    TEST_EXECUTION_ENDPOINT,
    TEST_EXECUTION_ENDPOINT_CLOUD,
    XRAY_DUPLICATE_IDS,
    XRAY_EXECUTION_PROJECT,
    XRAY_EXECUTION_SUMMARY,
    XRAY_EXECUTION_DESCRIPTION
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
from pytest_jira_xray.test_run import Status, XrayTest, XrayTestInfo, CloudStatus
from pytest_jira_xray.test_execution import TestExecution, TestExecutionInfo

xray_key = StashKey['XrayReport']()


def pytest_addoption(parser: Parser):
    xray = parser.getgroup('Jira Xray report')
    xray.addoption(
        *XRAY_API,
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
        help='Use with JIRA XRAY cloud server'
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
        *XRAY_TEST_PLAN_KEY,
        action='store',
        metavar='TestPlanKey',
        default=None,
        help='XRAY Test Plan ID'
    )
    xray.addoption(
        *XRAY_JSON,
        action='store',
        metavar='path',
        default=False,
        const='report.json',
        nargs='?',
        help='Create a JSON report file at the given path, can be left blank to use the default report.json file name'
    )
    xray.addoption(
        *XRAY_DUPLICATE_IDS,
        action='store_true',
        default=False,
        help='Allow test ids to be present on multiple pytest tests'
    )
    xray.addoption(
        *XRAY_EXECUTION_PROJECT,
        action='store',
        default=None,
        help="Set the destination Project to use for the Execution"
    )
    xray.addoption(
        *XRAY_EXECUTION_SUMMARY,
        action='store',
        default=False,
        help="Set the Test Execution's summary"
    )
    xray.addoption(
        *XRAY_EXECUTION_DESCRIPTION,
        action='store',
        default=False,
        help="Set the Test Execution's description"
    )


def pytest_addhooks(pluginmanager):
    from pytest_jira_xray import hooks

    pluginmanager.add_hookspecs(hooks)


def pytest_configure(config: Config) -> None:
    config.addinivalue_line(
        'markers', f'{XRAY_MARKER}(JIRA_ID): mark test with JIRA XRAY test case ID'
    )

    if (config.getoption(XRAY_JSON[0]) is False
        and config.getoption(XRAY_API[0]) is False) \
            or hasattr(config, 'workerinput'):
        return

    xray_path = config.getoption(XRAY_JSON[0])
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


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_xray_execution_key(execution_key: str) -> str:
    outcome = yield
    user_key = outcome.get_result()
    if user_key and isinstance(user_key, str):
        return user_key
    return outcome.force_result(execution_key)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_xray_project(project_key):
    outcome = yield
    user_project_key = outcome.get_result()
    if user_project_key and isinstance(user_project_key, str):
        return user_project_key
    return outcome.force_result(project_key)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_xray_summary(report_summary):
    outcome = yield
    user_summary = outcome.get_result()
    if user_summary and isinstance(user_summary, str):
        return user_summary
    return outcome.force_result(report_summary)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_xray_execution_description(description):
    outcome = yield
    user_description = outcome.get_result()
    if user_description and isinstance(user_description, str):
        return user_description
    return outcome.force_result(description)


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
def pytest_xray_status_mapping(is_cloud, node_id, report_outcome, failure_when, wasxfail):
    default_status_enum = Status
    if is_cloud:
        default_status_enum = CloudStatus
    if report_outcome == "pass":
        if wasxfail:
            return default_status_enum.FAIL
    elif report_outcome == "skipped":
        if not wasxfail:
            return default_status_enum.TODO
    elif report_outcome == "failed":
        if failure_when != "call":
            return default_status_enum.ABORTED
        if not wasxfail:
            return default_status_enum.FAIL
    return default_status_enum.PASS


class XrayPlugin:

    def __init__(self, config, xray_publisher=None, file_publisher=None):
        self.config = config

        self.xray_publisher = xray_publisher
        self.file_publisher = file_publisher

        self.reports: dict[str, list[TestReport]] = defaultdict(list)
        self._xray_tests: dict[XrayTest, list[XrayTest]] = defaultdict(list)

        self.start_date = -math.inf

        test_execution_params = self._generate_test_execution_params()
        self.test_execution = TestExecution(**test_execution_params)
        self.test_execution.validate()

        self.is_cloud: str = self.config.getoption(JIRA_CLOUD[0])
        #
        # self.test_execution_id: str = self.config.getoption(XRAY_EXECUTION_KEY[0])
        # self.test_plan_id: str = self.config.getoption(XRAY_TEST_PLAN_ID)
        self.allow_duplicate_ids: bool = self.config.getoption(XRAY_DUPLICATE_IDS[0])
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
        self.start_date = timing.time()

    # start pytest_runtest_protocol

    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item: Item, call: CallInfo):
        outcome = yield
        report = outcome.get_result()
        test_key_markers = item.iter_markers(name="xray")
        not_xray_markers = item.iter_markers(name="not_xray")
        report.start = call.start
        report.finish = call.stop
        report.not_xray = any(not_xray_marker is not None for not_xray_marker in not_xray_markers)
        report.test_keys = [test_key for test_key_marker in test_key_markers for test_key in test_key_marker.args]
        node = item.obj
        report.description = node.__doc__.strip() if node.__doc__ else node.__name__

    def pytest_runtest_logreport(self, report: TestReport):
        if report.not_xray:
            return
        self.reports[report.nodeid].append(report)

    def pytest_runtest_logfinish(self, nodeid):
        if not self.reports.get(nodeid):
            return
        xray_test_dicts = self._generate_test_params(self.reports.get(nodeid))
        for xray_test_dict in xray_test_dicts:
            xray_test = XrayTest(**xray_test_dict)
            self._xray_tests[xray_test].append(xray_test)
            if self.allow_duplicate_ids and len(self._xray_tests[xray_test]) > 1:
                self._xray_tests[xray_test] = [sum(self._xray_tests[xray_test])]

    # end pytest_runtest_protocol

    def pytest_sessionfinish(self, session: Session):
        self.test_execution.info.finish_date = timing.time()
        self.test_execution.info.start_date = self.start_date
        for xray_tests in self._xray_tests.values():
            for xray_test in xray_tests:
                self.test_execution.add_test_case(xray_test)
        self.file_publisher.publish(self.test_execution.to_dict())
        # self.xray_publisher.publish(self.test_execution.to_dict())

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
    #
    # @staticmethod
    # def _get_xray_marker(item: Item) -> Optional[Mark]:
    #     return item.get_closest_marker(XRAY_MARKER)

    def _generate_test_execution_params(self) -> dict:
        info_params = self._generate_test_execution_info_params()
        info = TestExecutionInfo(**info_params)
        execution_params = dict(info=info)

        test_execution_key = self.config.getoption(XRAY_EXECUTION_KEY[0], None)
        hook_execution_key = self.config.hook.pytest_xray_execution_key(execution_key=test_execution_key)
        if hook_execution_key and isinstance(hook_execution_key, str):
            execution_params['test_execution_key'] = hook_execution_key

        return execution_params

    def _generate_test_execution_info_params(self) -> Union[dict, None]:
        execution_info_params = dict()

        test_execution_project = self.config.getoption(XRAY_EXECUTION_PROJECT[0], None)
        hook_execution_project = self.config.hook.pytest_xray_project(project_key=test_execution_project)
        if hook_execution_project and isinstance(hook_execution_project, str):
            execution_info_params['project'] = hook_execution_project

        test_execution_summary = self.config.getoption(XRAY_EXECUTION_SUMMARY[0], None)
        hook_execution_summary = self.config.hook.pytest_xray_summary(report_summary=test_execution_summary)
        if hook_execution_summary and isinstance(hook_execution_summary, str):
            execution_info_params['summary'] = hook_execution_summary

        test_execution_description = self.config.getoption(XRAY_EXECUTION_DESCRIPTION[0], None)
        hook_execution_description = self.config.hook.pytest_xray_execution_description(description=test_execution_description)
        if hook_execution_description and isinstance(hook_execution_description, str):
            execution_info_params['description'] = hook_execution_description

        return execution_info_params

    def _generate_test_params(self, test_reports: List[TestReport]) -> List[dict]:
        report_outcome = "passed"
        wasxfail = False
        failure_when = None
        full_text = ""
        duration = 0.0
        start = math.inf
        finish = -math.inf
        test_report = False

        for test_report in test_reports:
            full_text += test_report.longreprtext
            duration += getattr(test_report, "duration", 0.0)
            start = min(start, test_report.start)
            finish = max(finish, test_report.finish)

            if test_report.outcome not in ("passed", "rerun") and report_outcome == "passed":
                report_outcome = test_report.outcome
                failure_when = test_report.when

            if hasattr(test_report, "wasxfail"):
                wasxfail = True

        status = self.config.hook.pytest_xray_status_mapping(is_cloud=self.is_cloud,
                                                             node_id=test_report.nodeid,
                                                             report_outcome=report_outcome,
                                                             failure_when=failure_when,
                                                             wasxfail=wasxfail)
        if status is None or not isinstance(status, str):
            raise ValueError("Status is not of type STRING")

        test_info_params = self._generate_test_info_params(test_report)
        test_info = XrayTestInfo(**test_info_params)
        test_params = dict(start=start, finish=finish, comment=full_text, status=status, test_info=test_info)

        if test_report.test_keys:
            return [dict(test_key=test_key, **test_params) for test_key in test_report.test_keys]
        return [test_params]

    def _generate_test_info_params(self, test_report) -> Union[dict, None]:
        test_info_dict = dict(definition=test_report.nodeid)
        # TODO: Set project_key
        # TODO: Set summary
        # TODO: Set description
        # TODO: Set test_type
        # TODO: Set requirement_keys
        # TODO: Set labels
        # TODO: Set steps
        # TODO: Set definition
        # TODO: Set scenario
        # TODO: Set scenario_type

        if not self.is_cloud:
            test_info_dict['description'] = test_report.description

        test_run_project_key = test_report.project_key
        hook_project_key = self.config.hook.pytest_xray_test_run_project_key(project_key=test_run_project_key)
        if hook_project_key and isinstance(hook_project_key, str):
            test_info_dict['project_key'] = test_info_dict
        return
