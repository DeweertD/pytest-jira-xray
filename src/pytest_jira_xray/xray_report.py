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
from .xray_result import XrayExecutionInfo, XrayTest


class XrayReport:

    def __init__(self, file_path=None, server_url=None, execution_key = None, test_plan_key=None, api_key=None, token=None, basic_auth=None, cloud=False):
        self.cloud = cloud
        self.basic_auth = basic_auth
        self.token = token
        self.api_key = api_key
        self.file_publisher = FilePublisher(file_path)
        # self.xray_publisher = XrayPublisher(server_url, config)
        self.test_execution_key: Optional[str] = execution_key
        self.info: XrayExecutionInfo = XrayExecutionInfo(test_plan_key)
        self._xray_test_results: list[XrayTest] = list()
        self.reports: dict[str, list[TestReport]] = defaultdict(list[TestReport])
        self.exception: list = []

    # def to_json(self) -> dict:
    #     xray_json = {}
    #     if self.test_execution_key:
    #         xray_json['testExecutionKey'] = self.test_execution_key
    #     if info := self.info.to_json():
    #         xray_json['info'] = info
    #     xray_json["tests"] = [test.to_json() for test in self._xray_test_results]
    #     return xray_json

    # def _finalize(self) -> None:
    #     if self.test_execution_key is None and not self.info.is_valid():
    #         raise ValueError(
    #             "Report has neither a Test Execution Key nor a Project Key, can't create valid Xray report")
    #     for tests in self.reports.values():
    #         xray_test_result = sum(map(XrayTest, tests))
    #         xray_test_result.validate()
    #         self._xray_test_results.append(xray_test_result)

    def pytest_sessionstart(self, session: Session):
        self.info.start_date = timing.time()

    def pytest_runtest_logreport(self, report: TestReport):
        self.reports[report.nodeid].append(report)

    def pytest_sessionfinish(self, session):
        self.info.finish_date = timing.time()
        # self._finalize()
        # self._save_report()
        # self._publish_report()

    def pytest_terminal_summary(self, terminalreporter: TerminalReporter) -> None:
        terminalreporter.write_sep("-", f"Writing terminal report")

    def _save_report(self):
        self.file_publisher.publish(self.to_json())
