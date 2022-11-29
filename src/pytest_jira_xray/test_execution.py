from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Union, Dict, Any

from pytest_jira_xray.test_run import XrayTest


@dataclass()
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

    def validate(self) -> bool:
        if self.project or self.test_plan_key:
            return True
        raise ValueError("Test Execution Info did not have a Project or a Test Plan Key")


@dataclass()
class TestExecution:
    test_execution_key: Optional[str] = None
    info: TestExecutionInfo = TestExecutionInfo()
    tests: List[XrayTest] = field(default_factory=list)

    def add_test_case(self, test: Union[dict, XrayTest]) -> None:
        if not isinstance(test, XrayTest):
            test = XrayTest(**test)
        self.tests.append(test)

    def find_test_case(self, test_key: str) -> XrayTest:
        """
        Searches a stored test case by identifier.
        If not found, raises KeyError
        """
        # Linear search, but who cares really of performance here?

        for test in self.tests:
            if test.test_key == test_key:
                return test

        raise KeyError(test_key)

    def validate(self) -> bool:
        if self.test_execution_key:
            return True
        if self.info:
            try:
                raise ValueError("The Test Execution did not have a Jira Issue Key")
            except ValueError as e:
                return self.info.validate()

    def to_dict(self) -> Dict[str, Any]:
        json_report = dict(
            tests=[test.to_dict() for test in self.tests]
        )

        if self.info:
            json_report['info'] = self.info.to_dict()
        if self.test_execution_key:
            json_report['testExecutionKey'] = self.test_execution_key

        return json_report
