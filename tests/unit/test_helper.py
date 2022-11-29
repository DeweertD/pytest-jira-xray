import pytest

from pytest_jira_xray.test_run import Status, XrayTest, CloudStatus
from pytest_jira_xray.test_execution import TestExecution


@pytest.mark.parametrize(
    'status, expected_status',
    [
        (Status.PASS, 'PASS'),
        (Status.FAIL, 'FAIL'),
        (Status.ABORTED, 'ABORTED'),
        (CloudStatus.PASS, 'PASSED'),
        (CloudStatus.FAIL, 'FAILED'),
        (CloudStatus.ABORTED, 'ABORTED')
    ]
)
def test_testcase_returns_expected_status(status, expected_status):
    test = XrayTest(
        test_key='JIRA-1',
        status=status,
        comment='hello'
    )
    assert test.to_dict()['status'].value == expected_status


def test_merge_test_cases():
    t1 = XrayTest(
        test_key='JIRA-1',
        status=Status.PASS,
        comment='hello'
    )

    t2 = XrayTest(
        test_key='JIRA-1',
        status=Status.FAIL,
        comment='hi'
    )

    t12 = t1 + t2
    assert t12 is not t1
    assert t12 is not t2

    assert t12.test_key == 'JIRA-1'
    assert t12.status == Status.FAIL
    assert t12.comment == 'hello\n' + '-' * 80 + '\nhi'


def test_xray_test_does_not_merge_different_keys():
    t1 = XrayTest(
        test_key='JIRA-1',
        status=Status.PASS,
        comment='hello'
    )

    t2 = XrayTest(
        test_key='JIRA-2',
        status=Status.FAIL,
        comment='hi'
    )
    with pytest.raises(ValueError):
        t3 = t1 + t2


def test_find_test_case_works():
    execution = TestExecution()
    t1 = XrayTest(
        test_key='JIRA-1',
        status=Status.PASS,
        comment=''
    )
    t2 = XrayTest(
        test_key='JIRA-2',
        status=Status.FAIL,
        comment='hi'
    )
    execution.add_test_case(t1)
    execution.add_test_case(t2)

    found = execution.find_test_case('JIRA-1')
    assert found is t1

    found = execution.find_test_case('JIRA-2')
    assert found is t2


def test_find_test_case_raises_key_error():
    execution = TestExecution()
    with pytest.raises(KeyError):
        execution.find_test_case('JIRA-42')
