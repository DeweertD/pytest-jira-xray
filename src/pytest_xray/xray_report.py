from collections import defaultdict
from typing import List, Optional

from _pytest import timing
from _pytest.config import Config, ExitCode
from _pytest.main import Session
from _pytest.nodes import Item
from _pytest.reports import TestReport
from _pytest.terminal import TerminalReporter

from .xray_result import XrayExecutionInfo, XrayTest


class XrayReport:

    def __int__(self, file_path, server_url, config: Config):
        self.test_execution_key: Optional[str] = None
        self.info: XrayExecutionInfo = XrayExecutionInfo()
        self.reports: dict[XrayTest] = defaultdict(XrayTest)
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

    def pytest_runtest_makereport(self, item, call):

    def pytest_runtest_logreport(self, report: TestReport):
        test = self.test_reporter(report)

    def pytest_sessionfinish(self, session):
        self.info.finish_date = timing.time()
        self._finalize()
        self._save_report()
        self._publish_report()

    def pytest_terminal_summary(self, terminalreporter: TerminalReporter) -> None:
        if self.exception:
            terminalreporter.ensure_newline()
            terminalreporter.section('Jira XRAY', sep='-', red=True, bold=True)
            terminalreporter.write_line('Could not publish results to Jira XRAY!')
            if self.exception.message:
                terminalreporter.write_line(self.exception.message)
        else:
            if self.issue_id and self.logfile:
                terminalreporter.write_sep(
                    '-', f'Generated XRAY execution report file: {Path(self.logfile).absolute()}'
                )
            elif self.issue_id:
                terminalreporter.write_sep(
                    '-', f'Uploaded results to JIRA XRAY. Test Execution Id: {self.issue_id}'
                )

    def test_reporter(self, report: Union[TestReport, str]) -> XrayTest:
        nodeid: Union[str, TestReport] = getattr(report, "nodeid", report)
        # Local hack to handle xdist report order.
        workernode = getattr(report, "node", None)

        key = nodeid, workernode

        if key not in self.reports:
            # TODO: breaks for --dist=each
            self.reports[key] = XrayTest(nodeid)

        return self.reports[key]
