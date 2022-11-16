import pytest


@pytest.mark.parametrize(
    'cli_options',
    [
        ('--jira-xray',),
        ('--jira-xray', '--cloud', '--client-secret-auth'),
        ('--jira-xray', '--cloud', '--token-auth'),
        ('--jira-xray', '--cloud', '--api-key-auth')
    ],
    ids=['DC Server', 'Cloud client secret', 'Could token', 'Could api key']
)
@pytest.mark.usefixtures('mock_server')
def test_jira_xray_plugin(xray_tests, cli_options):
    result = xray_tests.runpytest(*cli_options)
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines([
        '*Uploaded results to JIRA XRAY. Test Execution Id: 1000*',
    ])
    assert result.ret == 0
    assert not result.errlines


