from typing import Optional, Dict

from .helper import _merge_status
from .xray_statuses import Status, STATUS_STR_MAPPER_JIRA


class Test:
    def __init__(
        self,
        test_key: str,
        status: Status,
        comment: Optional[str] = None,
        status_str_mapper: Dict[Status, str] = None
    ):
        self.test_key = test_key
        self.status = status
        self.comment = comment or ''
        if status_str_mapper is None:
            status_str_mapper = STATUS_STR_MAPPER_JIRA
        self.status_str_mapper = status_str_mapper

    def merge(self, other: 'Test'):
        """
        Merges this test case with other, in order to obtain
        a combined result. Comments will be appended one after the other.
        Status will be merged according to a priority list.
        Merge is only possible if the two tests have the same test_key
        """

        if self.test_key != other.test_key:
            raise ValueError(
                f'Cannot merge test with different test keys: '
                f'{self.test_key} {other.test_key}'
            )

        if self.comment == '':
            if other.comment != '':
                self.comment = other.comment
        else:
            if other.comment != '':
                self.comment += ('\n' + '-'*80 + '\n')
                self.comment += other.comment

        self.status = _merge_status(self.status, other.status)

    def as_dict(self) -> Dict[str, str]:
        return dict(
            testKey=self.test_key,
            status=self.status_str_mapper[self.status],
            comment=self.comment,
        )
