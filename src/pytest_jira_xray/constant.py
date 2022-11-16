
PYTEST_PLUGIN = 'JIRA_XRAY'
# REST endpoints for DC and Cloud servers
TEST_EXECUTION_ENDPOINT = '/rest/raven/2.0/import/execution'
TEST_EXECUTION_ENDPOINT_CLOUD = '/api/v2/import/execution'
AUTHENTICATE_ENDPOINT = '/api/v2/authenticate'

# Pytest command line configuration options
XRAY_ALLOW_DUPLICATE_IDS = ('--allow-duplicate-ids', '--allow-duplicate-ids')
XRAY_TEST_PLAN_ID = ('--test-plan', '--testplan')
XRAY_EXECUTION_KEY = ('--xray-execution', '--xrayexecution', '--execution')
XRAY_EXECUTION_PROJECT = ('--project-execution', '--projectexecution')
XRAY_PATH = ('--xray-json', '--xrayjson')
JIRA_XRAY_FLAG = ('--jira-xray', '--jiraxray')
JIRA_CLOUD = ('--cloud',)
JIRA_API_KEY = ('--api-key-auth', '--apikeyauth')
JIRA_TOKEN = ('--token-auth', '--tokenauth')
JIRA_CLIENT_SECRET_AUTH = ('--client-secret-auth', '--clientsecretauth')

# Custom pytest markers
XRAY_MARKER = 'xray'

# all environment variables used by plugin
ENV_XRAY_API_BASE_URL = 'XRAY_API_BASE_URL'
ENV_XRAY_API_USER = 'XRAY_API_USER'
ENV_XRAY_API_PASSWORD = 'XRAY_API_PASSWORD'
ENV_XRAY_CLIENT_ID = 'XRAY_CLIENT_ID'
ENV_XRAY_CLIENT_SECRET = 'XRAY_CLIENT_SECRET'
ENV_XRAY_API_KEY = 'XRAY_API_KEY'
ENV_XRAY_API_TOKEN = 'XRAY_API_TOKEN'
ENV_XRAY_API_VERIFY_SSL = 'XRAY_API_VERIFY_SSL'

ENV_TEST_EXECUTION_TEST_ENVIRONMENTS = 'XRAY_EXECUTION_TEST_ENVIRONMENTS'
ENV_TEST_EXECUTION_FIX_VERSION = 'XRAY_EXECUTION_FIX_VERSION'
ENV_TEST_EXECUTION_REVISION = 'XRAY_EXECUTION_REVISION'
ENV_TEST_EXECUTION_SUMMARY = 'XRAY_EXECUTION_SUMMARY'
ENV_TEST_EXECUTION_DESC = 'XRAY_EXECUTION_DESC'
ENV_MULTI_VALUE_SPLIT_PATTERN = '\\s+'

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
