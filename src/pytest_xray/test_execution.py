import datetime
from dataclasses import dataclass
from typing import Optional, List, Union, Dict, Any

from pytest_xray import constant
from pytest_xray.constant import DATETIME_FORMAT
from pytest_xray.helper import _from_environ_or_none, _from_environ, _first_from_environ
from pytest_xray.test_run import TestCase


@dataclass
class TestExecutionInfo:
    project: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    fix_version: Optional[str] = None
    revision: Optional[str] = None
    user: Optional[str] = None
    start_date: Optional[datetime] = None
    finish_date: Optional[datetime] = None
    test_plan_key: Optional[str] = None
    test_environments: Optional[list[str]] = None

    def to_dict(self) -> dict:
        info = {}
        if self.project:
            info['project'] = self.project
        if self.summary:
            info['summary'] = self.summary
        if self.description:
            info['description'] = self.description
        if self.fix_version:
            info['fix_version'] = self.fix_version
        if self.revision:
            info['revision'] = self.revision
        if self.user:
            info['user'] = self.user
        if self.start_date:
            info['startDate'] = self.start_date
        if self.finish_date:
            info['finishDate'] = self.finish_date
        if self.test_plan_key:
            info['testPlanKey'] = self.test_plan_key
        if self.test_environments:
            info['testEnvironments'] = self.test_environments
        return info

    def is_valid(self) -> bool:
        return self.project is not None


@dataclass
class TestExecution:
    test_execution_key: Optional[str] = None,
    info: Optional[TestExecutionInfo] = None,
    tests: Optional[List[TestCase]] = None,

    def add_test_case(self, test: Union[dict, TestCase]) -> None:
        if not isinstance(test, TestCase):
            test = TestCase(**test)
        self.tests.append(test)

    def find_test_case(self, test_key: str) -> TestCase:
        """
        Searches a stored test case by identifier.
        If not found, raises KeyError
        """
        # Linear search, but who cares really of performance here?

        for test in self.tests:
            if test.test_key == test_key:
                return test

        raise KeyError(test_key)

    def to_dict(self) -> Dict[str, Any]:
        json_report = dict(
            tests=[test.to_dict() for test in self.tests]
        )

        if self.info:
            json_report['info'] = self.info.to_dict()
        if self.test_execution_key:
            json_report['testExecutionKey'] = self.test_execution_key

        return json_report
