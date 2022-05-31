import datetime as dt
from typing import Optional, List, Union, Dict, Any

from .helper import _from_environ_or_none, _from_environ, _first_from_environ
from .xray_test import Test


class TestExecution:

    def __init__(
        self,
        test_execution_key: Optional[str] = None,
        test_plan_key: Optional[str] = None,
        user: Optional[str] = None,
        revision: Optional[str] = None,
        tests: Optional[List[Test]] = None,
        test_environments: Optional[List[str]] = None,
        fix_version: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
    ):
        self.test_execution_key = test_execution_key
        self.test_plan_key = test_plan_key or ''
        self.user = user or ''
        self.revision = revision or _from_environ_or_none(constant.ENV_TEST_EXECUTION_REVISION)
        self.start_date = dt.datetime.now(tz=dt.timezone.utc)
        self.finish_date = None
        self.tests = tests or []
        self.test_environments = test_environments or _from_environ(
            constant.ENV_TEST_EXECUTION_TEST_ENVIRONMENTS,
            constant.ENV_MULTI_VALUE_SPLIT_PATTERN
        )
        self.fix_version = fix_version or _first_from_environ(constant.ENV_TEST_EXECUTION_FIX_VERSION)
        self.summary = summary or _from_environ_or_none(constant.ENV_TEST_EXECUTION_SUMMARY)
        self.description = description or _from_environ_or_none(constant.ENV_TEST_EXECUTION_DESC)

    def append(self, test: Union[dict, Test]) -> None:
        if not isinstance(test, Test):
            test = Test(**test)
        self.tests.append(test)

    def find_test_case(self, test_key: str) -> Test:
        """
        Searches a stored test case by identifier.
        If not found, raises KeyError
        """
        # Linear search, but who cares really of performance here?

        for test in self.tests:
            if test.test_key == test_key:
                return test

        raise KeyError(test_key)

    def as_dict(self) -> Dict[str, Any]:
        if self.finish_date is None:
            self.finish_date = dt.datetime.now(tz=dt.timezone.utc)  # type: ignore

        tests = [test.as_dict() for test in self.tests]
        info = dict(
            startDate=self.start_date.strftime(DATETIME_FORMAT),
            finishDate=self.finish_date.strftime(DATETIME_FORMAT),  # type: ignore
        )

        if self.fix_version:
            info['version'] = self.fix_version

        if self.test_environments and len(self.test_environments) > 0:
            info['testEnvironments'] = self.test_environments

        if self.summary:
            info['summary'] = self.summary

        if self.description:
            info['description'] = self.description

        if self.revision:
            info['revision'] = self.revision

        data = dict(
            info=info,
            tests=tests
        )
        if self.test_plan_key:
            info['testPlanKey'] = self.test_plan_key
        if self.test_execution_key:
            data['testExecutionKey'] = self.test_execution_key
        return data
