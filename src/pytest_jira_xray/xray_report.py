from collections import defaultdict
from typing import List, Optional, Union

import pytest
from _pytest import timing
from _pytest.config import Config, ExitCode
from _pytest.main import Session
from _pytest.nodes import Item
from _pytest.reports import TestReport
from _pytest.runner import CallInfo
from _pytest.terminal import TerminalReporter

from .file_publisher import FilePublisher
from .xray_publisher import XrayPublisher
from .xray_result import XrayExecutionInfo, XrayTest, XrayTestInfo


class XrayReport:

    def __init__(self, file_path=None, server_url=None, execution_key=None, test_plan_key=None, api_key=None,
                 token=None, basic_auth=None, cloud=False):
        self.cloud = cloud
        self.basic_auth = basic_auth
        self.token = token
        self.api_key = api_key
        self.file_publisher = FilePublisher(file_path)
        # self.xray_publisher = XrayPublisher(server_url, config)
        self.test_execution_key: Optional[str] = execution_key
        self.info: XrayExecutionInfo = XrayExecutionInfo(test_plan_key)
        self._xray_tests: list[XrayTest] = list()
        self.reports: dict = defaultdict(list)
        self.exception: list = []

    def to_json(self) -> dict:
        xray_json = {}
        if self.test_execution_key:
            xray_json['testExecutionKey'] = self.test_execution_key
        if info := self.info.to_json():
            xray_json['info'] = info
        xray_json["tests"] = [test.to_json() for test in self._xray_tests]
        return xray_json

    def _finalize(self, session: Session) -> None:
        hook_execution_key = session.config.hook.pytest_xray_execution_key()
        if bool(hook_execution_key) and isinstance(hook_execution_key, str):
            self.test_execution_key = hook_execution_key
        if (not self.test_execution_key or not isinstance(self.test_execution_key, str)) and not self.info.is_valid():
            raise ValueError(
                "Report has neither a Test Execution Key nor a Project Key, can't create valid Xray report")
        for test_name, test_reports in self.reports.items():

            wasxfail = False
            failure_when = None
            full_text = ""
            duration = 0.0

            for test_report in test_reports:
                if test_report.outcome == "rerun":
                    # reruns are separate test runs for all intensive purposes
                    # self.append_rerun(test_report)
                    print("Handle rerun in an Xray way")
                else:
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

            xray_test_dict = dict(status=session.config.hook.pytest_xray_status_mapping(report_outcome, failure_when, wasxfail))
            if test_report.test_keys:
                xray_tests = [XrayTest(test_key=test_key, *xray_test_dict) for test_key in test_report.test_keys]
            else:
                xray_tests = [XrayTest(test_info=XrayTestInfo(definition=test_report.nodeid), *xray_test_dict)]
            self._xray_tests += xray_tests

    def pytest_sessionstart(self, session: Session):
        self.info.start_date = timing.time()

    def pytest_runtest_logreport(self, report: TestReport):
        self.reports[report.nodeid].append(report)

    # def pytest_collectreport(self, report: TestReport):
    #     if report.failed:
    #         self.append_failed(report)

    def pytest_sessionfinish(self, session):
        self.info.finish_date = timing.time()
        self._finalize(session)
        self._save_report()
        # self._publish_report()

    def pytest_terminal_summary(self, terminalreporter: TerminalReporter) -> None:
        terminalreporter.write_sep("-", f"Writing terminal report")

    def _save_report(self):
        self.file_publisher.publish(self.to_json())
