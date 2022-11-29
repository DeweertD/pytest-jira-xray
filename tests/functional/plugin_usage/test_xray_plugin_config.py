def test_help_message(pytester):
    result = pytester.runpytest(
        '--help',
    )
    result.stdout.fnmatch_lines([
        'Jira Xray report:',
        '*--xray-api*Upload test results to JIRA XRAY*',
        '*--cloud*Use with JIRA XRAY cloud server*',
        '*--api-key*Use API Key authentication*',
        '*--token-auth*Use token authentication*',
        '*--client-secret*Use client secret authentication*',
        '*--execution=TestExecutionKey*',
        '*Set the XRAY Test Execution Key*',
        '*--test-plan=TestPlanKey*',
        '*XRAY Test Plan ID*',
        '*--xray-json=[[]path]*Create a JSON report file at the given path, can be left*',
        '*blank to use the default report.json file name*',
        '*--project-key=PROJECT_KEY, --project=PROJECT_KEY*',
        '*Set the destination Project to use for the Execution*',
        '*--execution-summary=EXECUTION_SUMMARY, --summary=EXECUTION_SUMMARY*',
        '*Set the Test Execution\'s summary*'
    ])
