from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from _pytest.reports import TestReport


@dataclass
class XrayCustomField:
    id: Optional[str] = None
    value: Optional[str] = None

    def to_json(self):
        pass


@dataclass
class XrayEvidence:
    data: Optional[str] = None
    filename: Optional[str] = None
    content_type: Optional[str] = None

    def to_json(self):
        pass


@dataclass
class XrayParameter:
    name: Optional[str] = None
    value: Optional[str] = None


@dataclass
class XrayIteration:
    name: Optional[str] = None
    parameters: Optional[list[XrayParameter]] = field(default_factory=list)
    status: Optional[str] = None

    def to_json(self):
        pass


@dataclass
class XraySteps:
    action: Optional[str] = None
    data: Optional[str] = None
    result: Optional[str] = None

    def to_json(self):
        pass


@dataclass
class XrayTestInfo:
    project_key: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    test_type: Optional[str] = None
    requirement_keys: Optional[list[str]] = field(default_factory=list)
    labels: Optional[list[str]] = field(default_factory=list)
    steps: Optional[list[XraySteps]] = field(default_factory=list)
    definition: Optional[str] = None
    scenario: Optional[str] = None
    scenario_type: Optional[list[str]] = field(default_factory=list)

    def _set_test_type(self):
        if self.definition is not None:
            self.test_type = "Generic"
        elif self.steps:
            self.test_type = "Manual"
        elif self.scenario is not None or self.scenario_type:
            self.test_type = "Cucumber"

    def to_json(self):
        test_info = {}
        if self.project_key:
            test_info['project_key'] = self.project_key
        if self.summary:
            test_info['summary'] = self.summary
        if self.description:
            test_info['description'] = self.description
        if self.test_type:
            test_info['test_type'] = self.test_type
        if self.requirement_keys:
            test_info['requirement_keys'] = self.requirement_keys
        if self.labels:
            test_info['labels'] = self.labels
        if self.steps:
            test_info['steps'] = [step.to_json() for step in self.steps]
        if self.definition:
            test_info['definition'] = self.definition
        if self.scenario:
            test_info['scenario'] = self.scenario
        if self.scenario_type:
            test_info['scenario_type'] = self.scenario_type
        return test_info

    def xray_can_match(self) -> bool:
        self._set_test_type()
        return (self.test_type is not None
                and ((self.summary is not None and self.test_type in ("Manual", "Cucumber"))
                     or (self.definition is not None and self.test_type == "Generic")))


@dataclass
class XrayTest:
    test_key: Optional[str] = None
    test_info: Optional[XrayTestInfo] = None
    start: Optional[datetime] = None
    finish: Optional[datetime] = None
    comment: Optional[str] = None
    executed_by: Optional[str] = None
    assignee: Optional[str] = None
    status: str = field(default="TODO")
    steps: list[XraySteps] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    iterations: list[XrayIteration] = field(default_factory=list)
    defects: list[str] = field(default_factory=list)
    evidence: list[XrayEvidence] = field(default_factory=list)
    custom_fields: list[XrayCustomField] = field(default_factory=list)

    def add_requirement(self, *requirement_keys):
        for requirement_key in requirement_keys:
            self.test_info.requirement_keys.append(requirement_key)

    def to_json(self):
        xray_test = {}
        if self.test_key:
            xray_test['testKey'] = self.test_key
        if self.test_info:
            xray_test['testInfo'] = self.test_info.to_json()
        if self.start:
            xray_test['start'] = self.start
        if self.finish:
            xray_test['finish'] = self.finish
        if self.comment:
            xray_test['comment'] = self.comment
        if self.executed_by:
            xray_test['executedBy'] = self.executed_by
        if self.assignee:
            xray_test['assignee'] = self.assignee
        if self.status:
            xray_test['status'] = self.status
        if self.steps:
            xray_test['steps'] = [step.to_json() for step in self.steps]
        if self.examples:
            xray_test['examples'] = self.examples
        if self.iterations:
            xray_test['iterations'] = [iteration.to_json() for iteration in self.iterations]
        if self.defects:
            xray_test['defects'] = self.defects
        if self.evidence:
            xray_test['evidence'] = [evidence_item.to_json() for evidence_item in self.evidence]
        if self.custom_fields:
            xray_test['customFields'] = [custom_field.to_json() for custom_field in self.custom_fields]
        return xray_test

    def validate(self) -> None:
        if self.test_key is None and self.test_info.xray_can_match() is False:
            raise ValueError(
                "No Test Key was specified, and Test Info was not present for automatic test matching or creation")

    def __add__(self, other):
        if not isinstance(other, XrayTest):
            raise TypeError("Attempting to add unsupported type to the XrayTest report")

    def __radd__(self, other):
        if not other:
            return self
        if not isinstance(other, XrayTest):
            raise TypeError(f"Attempting to add {type(other)} to XrayTest")


@dataclass
class XrayExecutionInfo:
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

    def to_json(self) -> dict:
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


