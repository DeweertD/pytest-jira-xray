import copy
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Union, Literal


class OrderedEnum(str, Enum):
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return list(self.__class__.__members__.keys()).index(self.name) \
                   >= list(self.__class__.__members__.keys()).index(other.name)
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return list(self.__class__.__members__.keys()).index(self.name) \
                   > list(self.__class__.__members__.keys()).index(other.name)
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return list(self.__class__.__members__.keys()).index(self.name) \
                   <= list(self.__class__.__members__.keys()).index(other.name)
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return list(self.__class__.__members__.keys()).index(self.name) \
                   < list(self.__class__.__members__.keys()).index(other.name)
        return NotImplemented


statuses = ['PASS', 'TODO', 'EXECUTING', 'PENDING', 'FAIL', 'ABORTED', 'BLOCKED']
cloud_status_values = ['PASSED', 'TODO', 'EXECUTING', 'PENDING', 'FAILED', 'ABORTED', 'BLOCKED']

Status = OrderedEnum("Status", zip(statuses, statuses))
CloudStatus = OrderedEnum("Status", zip(statuses, cloud_status_values))


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

    def to_dict(self):
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
    test_type: Optional[Literal['Generic', 'Manual', 'Cucumber']] = field(default='Generic')
    requirement_keys: Optional[list[str]] = field(default_factory=list)
    labels: Optional[list[str]] = field(default_factory=list)
    steps: Optional[list[XrayStep]] = field(default_factory=list)
    definition: Optional[str] = None
    scenario: Optional[str] = None
    scenario_type: Optional[list[str]] = field(default_factory=list)

    def to_cloud_dict(self):
        test_info = self.to_dict()
        if self.test_type:
            test_info['type'] = self.test_type
        if self.steps:
            test_info['steps'] = [step.to_cloud_dict() for step in self.steps]
        return test_info

    def to_server_dict(self):
        test_info = self.to_dict()
        if self.test_type:
            test_info['testType'] = self.test_type
        if self.steps:
            test_info['steps'] = [step.to_server_dict() for step in self.steps]
        return test_info

    def to_dict(self):
        test_info = {}
        if self.project_key:
            test_info['projectKey'] = self.project_key
        if self.summary:
            test_info['summary'] = self.summary
        if self.description:
            test_info['description'] = self.description
        if self.requirement_keys:
            test_info['requirementKeys'] = self.requirement_keys
        if self.labels:
            test_info['labels'] = self.labels
        if self.definition:
            test_info['definition'] = self.definition
        if self.scenario:
            test_info['scenario'] = self.scenario
        if self.scenario_type:
            test_info['scenarioType'] = self.scenario_type
        return test_info

    def add_requirements(self, *requirement_keys):
        if any(type(requirement_key) != str for requirement_key in requirement_keys):
            raise TypeError(f"A Requirement key was not of type String")
        self.requirement_keys += requirement_keys

    def validate(self) -> bool:
        if self.__key() is not None:
            return True
        raise ValueError("Test Info was not present for automatic test matching or creation")

    def __key(self):
        if self.test_type in ("Manual", "Cucumber"):
            return self.test_type, self.summary
        if self.test_type == "Generic":
            return self.test_type, self.definition

    def __eq__(self, other):
        if isinstance(other, XrayTestInfo):
            return self.__key() == other.__key()
        return NotImplemented

    def __add__(self, other):
        if self.test_type != other.test_type:
            return NotImplemented
        if self.test_type in ("Manual", "Cucumber"):
            return self.summary == other.summary
        if self.test_type == "Generic":
            return self.definition == other.definition
        return False

    def __hash__(self):
        return hash(self.__key())


@dataclass
class XrayTest:
    test_key: Optional[str] = None
    test_info: Optional[XrayTestInfo] = None
    start: Optional[datetime] = None
    finish: Optional[datetime] = None
    status: Union[Status, str] = field(default=Status.TODO)
    comment: Optional[str] = None
    executed_by: Optional[str] = None
    assignee: Optional[str] = None
    evidence: list[XrayEvidence] = field(default_factory=list)

    # steps: list[XraySteps] = field(default_factory=list)
    # examples: list[str] = field(default_factory=list)
    # iterations: list[XrayIteration] = field(default_factory=list)
    # defects: list[str] = field(default_factory=list)
    # custom_fields: list[XrayCustomField] = field(default_factory=list)

    def add_requirements(self, *requirement_keys):
        self.test_info.add_requirements(*requirement_keys)

    def to_dict(self) -> dict:
        self.validate()
        xray_test = dict(status=self.status.__str__())
        if self.test_key:
            xray_test['testKey'] = self.test_key
        if self.test_info:
            xray_test['testInfo'] = self.test_info.to_dict()
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

    def validate(self) -> bool:
        if self.test_key and isinstance(self.test_key, str):
            return True
        try:
            raise ValueError("No Test Key was specified")
        except ValueError as e:
            return self.test_info.validate()

    def __key(self):
        return (self.test_key, None, None) if self.test_key else (None, self.test_info._XrayTestInfo__key())

    def __add__(self, other: 'XrayTest') -> 'XrayTest':
        """
        Merges this test case with other to obtain a combined result. Comments will be just appended one after the
        other. status will be merged according to a priority list. Merge is only possible if the two tests have the
        same identity.
        """

        if self.__class__ is not other.__class__:
            raise TypeError("Cannot merge incompatible test types")
        if self != other:
            raise ValueError(
                f'Cannot merge two different tests: '
                f'{self.test_key} {other.test_key}'
            )
        new_xray_test_values = dict()
        if self.test_key is not None:
            new_xray_test_values['test_key'] = self.test_key

        if self.test_info is not None and other.test_info is not None:
            new_xray_test_values['test_info'] = self.test_info + other.test_info
        elif self.test_info is not None and other.test_info is None:
            new_xray_test_values['test_info'] = copy.deepcopy(self.test_info)
        elif self.test_info is None and other.test_info is not None:
            new_xray_test_values['test_info'] = copy.deepcopy(other.test_info)

        new_xray_test_values['comment'] = f'{self.comment}\n{"":->80}\n{other.comment}'

        new_xray_test_values['status'] = max(self.status, other.status)

        # TODO Add other values together in new XrayTest object

        return XrayTest(**new_xray_test_values)

    def __eq__(self, other):
        if isinstance(other, XrayTest):
            return self.__key() == other.__key()
        return NotImplemented

    def __hash__(self):
        return hash(self.__key())
