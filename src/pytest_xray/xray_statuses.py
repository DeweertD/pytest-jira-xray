import enum


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
