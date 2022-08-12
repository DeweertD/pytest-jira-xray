from dataclasses import dataclass, field
import enum
from datetime import datetime
from typing import Optional, Dict, Union


class Status(str, enum.Enum):
    TODO = 'TODO'
    EXECUTING = 'EXECUTING'
    PENDING = 'PENDING'
    PASS = 'PASS'
    FAIL = 'FAIL'
    ABORTED = 'ABORTED'
    BLOCKED = 'BLOCKED'


STATUS_HIERARCHY = [
    Status.PASS,
    Status.TODO,
    Status.EXECUTING,
    Status.PENDING,
    Status.FAIL,
    Status.ABORTED,
    Status.BLOCKED,
]
STATUS_STR_MAPPER_CLOUD = {
    Status.TODO: 'TODO',
    Status.EXECUTING: 'EXECUTING',
    Status.PENDING: 'PENDING',
    Status.PASS: 'PASSED',
    Status.FAIL: 'FAILED',
    Status.ABORTED: 'ABORTED',
    Status.BLOCKED: 'BLOCKED',
}
STATUS_STR_MAPPER_JIRA = {x: x.value for x in Status}


@dataclass
class XrayCustomField:
    id: Optional[str] = None
    value: Optional[str] = None

    def to_json(self):
        return dict(
            id=self.id,
            value=self.value,
        )


@dataclass
class XrayEvidence:
    data: Optional[str] = None
    filename: Optional[str] = None
    content_type: Optional[str] = None

    def to_json(self):
        return dict(
            data=self.data,
            filename=self.filename,
            content_type=self.content_type,
        )


@dataclass
class XrayParameter:
    name: Optional[str] = None
    value: Optional[str] = None

    def to_json(self):
        return dict(
            name=self.name,
            value=self.value,
        )


@dataclass
class XrayIteration:
    name: Optional[str] = None
    parameters: Optional[list[XrayParameter]] = field(default_factory=list)
    status: Optional[str] = None

    def to_json(self):
        return dict(
            name=self.name,
            parameters=self.parameters,
            status=self.status,
        )


@dataclass
class XrayStep:
    action: Optional[str] = None
    data: Optional[str] = None
    result: Optional[str] = None

    def to_json(self):
        return dict(
            action=self.action,
            data=self.data,
            result=self.result,
        )


@dataclass
class XrayTestInfo:
    project_key: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    test_type: Optional[str] = None
    requirement_keys: Optional[list[str]] = field(default_factory=list)
    labels: Optional[list[str]] = field(default_factory=list)
    steps: Optional[list[XrayStep]] = field(default_factory=list)
    definition: Optional[str] = None
    scenario: Optional[str] = None
    scenario_type: Optional[list[str]] = field(default_factory=list)

    def __post_init__(self):
        if self.definition is not None:
            self.test_type = "Generic"
        elif self.steps:
            self.test_type = "Manual"
        elif self.scenario is not None or self.scenario_type:
            self.test_type = "Cucumber"

    def to_json(self):
        test_info = {}
        if self.project_key:
            test_info['projectKey'] = self.project_key
        if self.summary:
            test_info['summary'] = self.summary
        if self.description:
            test_info['description'] = self.description
        if self.test_type:
            test_info['testType'] = self.test_type
        if self.requirement_keys:
            test_info['requirementKeys'] = self.requirement_keys
        if self.labels:
            test_info['labels'] = self.labels
        if self.steps:
            test_info['steps'] = [step.to_dict() for step in self.steps]
        if self.definition:
            test_info['definition'] = self.definition
        if self.scenario:
            test_info['scenario'] = self.scenario
        if self.scenario_type:
            test_info['scenarioType'] = self.scenario_type
        return test_info

    def can_xray_find_match(self) -> bool:
        return (self.summary is not None
                and self.test_type in ("Manual", "Cucumber")) \
               or (self.definition is not None
                   and self.test_type == "Generic")

    def add_requirements(self, *requirement_keys):
        if any(type(requirement_key) != str for requirement_key in requirement_keys):
            raise TypeError(f"A Requirement key was not of type String")
        self.requirement_keys += requirement_keys

    def __eq__(self, other):
        if self.test_type != other.test_type:
            return False
        if self.test_type in ("Manual", "Cucumber"):
            return self.summary == other.summary
        if self.test_type == "Generic":
            return self.definition == other.definition
        return False

    def __add__(self, other):
        if self.test_type != other.test_type:
            return False
        if self.test_type in ("Manual", "Cucumber"):
            return self.summary == other.summary
        if self.test_type == "Generic":
            return self.definition == other.definition
        return False


@dataclass
class TestCase:
    test_key: Optional[str] = None
    test_info: Optional[XrayTestInfo] = None
    start: Optional[datetime] = None
    finish: Optional[datetime] = None
    status: Union[Status, str] = field(default=Status.TODO)
    comment: Optional[str] = None
    executed_by: Optional[str] = None
    assignee: Optional[str] = None

    # steps: list[XraySteps] = field(default_factory=list)
    # examples: list[str] = field(default_factory=list)
    # iterations: list[XrayIteration] = field(default_factory=list)
    # defects: list[str] = field(default_factory=list)
    # evidence: list[XrayEvidence] = field(default_factory=list)
    # custom_fields: list[XrayCustomField] = field(default_factory=list)

    def add_requirements(self, *requirement_keys):
        self.test_info.add_requirements(*requirement_keys)

    def to_dict(self) -> dict:
        self._validate()
        xray_test = dict(status=self.status.__str__())
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
        # if self.steps:
        #     xray_test['steps'] = [step.to_json() for step in self.steps]
        # if self.examples:
        #     xray_test['examples'] = self.examples
        # if self.iterations:
        #     xray_test['iterations'] = [iteration.to_json() for iteration in self.iterations]
        # if self.defects:
        #     xray_test['defects'] = self.defects
        # if self.evidence:
        #     xray_test['evidence'] = [evidence_item.to_json() for evidence_item in self.evidence]
        # if self.custom_fields:
        #     xray_test['customFields'] = [custom_field.to_json() for custom_field in self.custom_fields]
        return xray_test

    def _validate(self) -> None:
        if not self.test_key and self.test_info.can_xray_find_match() is False:
            raise ValueError(
                "No Test Key was specified, and Test Info was not present for automatic test matching or creation")

    @staticmethod
    def _merge_status(status_1: Status, status_2: Status):
        """Merges the status of two tests. """

        return STATUS_HIERARCHY[max(
            STATUS_HIERARCHY.index(status_1),
            STATUS_HIERARCHY.index(status_2)
        )]

    def __radd__(self, other):
        if not other:
            return self
        if not isinstance(other, TestCase):
            raise TypeError(f"Attempting to add {type(other)} to XrayTest")

    def __add__(self, other: 'TestCase') -> 'TestCase':
        """
        Merges this test case with other to obtain a combined result. Comments will be just appended one after the
        other. status will be merged according to a priority list. Merge is only possible if the two tests have the
        same identity.
        """

        if self is other or other == 0:
            return self
        if type(other) is not TestCase:
            raise TypeError("Cannot merge types")
        if self != other:
            raise ValueError(
                f'Cannot merge test with different test keys: '
                f'{self.test_key} {other.test_key}'
            )
        self.test_info += other.test_info
        self.comment = '\n'.join((self.comment, other.comment))
        self.status = _merge_status(self.status, other.status)

    def __eq__(self, other):
        if (self.test_key or other.test_key) and self.test_key == other.test_key:
            return True
        if (self.test_info or other.test_info) and self.test_info == other.test_info:
            return True
        return False
