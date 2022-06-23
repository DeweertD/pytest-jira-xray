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

from .xray_result import XrayExecutionInfo, XrayTest


class XrayReport:

    def __init__(self, file_path, server_url, config: Config):
        self.test_execution_key: Optional[str] = None
        self.info: XrayExecutionInfo = XrayExecutionInfo()
        self.reports: dict[XrayTest] = defaultdict(list)
        self.config: Config = config
        self.exception: list = []

    def to_json(self) -> dict:
        xray_json = {}
        if self.test_execution_key:
            xray_json['testExecutionKey'] = self.test_execution_key
        if info := self.info.to_json():
            xray_json['info'] = info
        xray_json["tests"] = [test.to_json() for test in self.reports.values()]
        return xray_json

    def _finalize(self) -> None:
        if self.test_execution_key is None and self.info.is_valid() is False:
            raise ValueError(
                "Report has neither a Test Execution Key nor a Project Key, can't create valid Xray report")
        for test in self.reports.values():
            test.validate()

    def pytest_sessionstart(self, session: Session):
        self.info.start_date = timing.time()

    # @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    # def pytest_runtest_makereport(self, item: Item, call: CallInfo):
    #     outcome = yield
    #     report: TestReport = outcome.get_result()
    #     if report.when == "call":
    #         print("Hello Report!")

    def pytest_runtest_logreport(self, report: XrayTest):
        self.reports[report].append(report)

    def pytest_sessionfinish(self, session):
        self.info.finish_date = timing.time()
        # self._finalize()
        # self._save_report()
        # self._publish_report()

    def pytest_terminal_summary(self, terminalreporter: TerminalReporter) -> None:
        terminalreporter.write_sep("-", f"Writing terminal report")

