def test_help_message(pytester):
    result = pytester.runpytest(
        '--help',
    )
    result.stdout.fnmatch_lines([
        'Jira Xray report:',
        '*--jira-xray*Upload test results to JIRA XRAY*',
        '*--cloud*Use with JIRA XRAY could server*',
        '*--api-key-auth*Use API Key authentication*',
        '*--token-auth*Use token authentication*',
        '*--client-secret-auth*Use client secret authentication*',
        '*--execution=TestExecutionKey*',
        '*Set the XRAY Test Execution Key*',
        '*--test-plan=TestPlanKey*',
        '*XRAY Test Plan ID*',
        '*--xray-json=[[]path]*Create a JSON report file at the given path, can be left*',
        '*blank to use the default report.json file name*',
    ])
