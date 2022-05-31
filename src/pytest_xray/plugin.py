from typing import Tuple, Union

from _pytest.config import Config
from _pytest.config.argparsing import Parser
from requests.auth import AuthBase

from .constants import *
from .file_publisher import FilePublisher
from .helper import (
    get_bearer_auth,
    get_api_key_auth,
    get_basic_auth, get_api_token_auth,
)
from .xray_publisher import (
    ClientSecretAuth,
    ApiKeyAuth,
    XrayPublisher,
    TokenAuth
)
from .xray_report import XrayReport


def pytest_addoption(parser: Parser):
    xray = parser.getgroup('Jira Xray report')
    xray.addoption(
        JIRA_XRAY_FLAG,
        action='store_true',
        default=False,
        help='Upload test results to JIRA through the XRAY results importer endpoint'
    )
    xray.addoption(
        JIRA_CLOUD,
        action='store_true',
        default=False,
        help='Use with JIRA XRAY cloud server'
    )
    xray.addoption(
        JIRA_API_KEY,
        action='store_true',
        default=False,
        help='Use API Key authentication',
    )
    xray.addoption(
        JIRA_TOKEN,
        action='store_true',
        default=False,
        help='Use token authentication',
    )
    xray.addoption(
        JIRA_CLIENT_SECRET_AUTH,
        action='store_true',
        default=False,
        help='Use client secret authentication',
    )
    xray.addoption(
        XRAY_EXECUTION_ID,
        action='store',
        metavar='ExecutionId',
        default=None,
        help='XRAY Test Execution ID'
    )
    xray.addoption(
        XRAY_TEST_PLAN_ID,
        action='store',
        metavar='TestplanId',
        default=None,
        help='XRAY Test Plan ID'
    )
    xray.addoption(
        XRAY_PATH,
        action='store',
        metavar='path',
        default=None,
        help='Do not upload to a server but create JSON report file at given path'
    )
    xray.addoption(
        XRAY_ALLOW_DUPLICATE_IDS,
        action='store_true',
        default=False,
        help='Allow test ids to be present on multiple pytest tests'
    )


def pytest_configure(config: Config) -> None:
    config.addinivalue_line(
        'markers', 'xray(JIRA_ID): mark test with JIRA XRAY test case ID'
    )

    if not config.getoption(JIRA_XRAY_FLAG) or hasattr(config, 'workerinput'):
        return

    xray_path = config.getoption(XRAY_PATH)

    if xray_path:
        publisher = FilePublisher(xray_path)  # type: ignore
    else:
        if config.getoption(JIRA_CLOUD):
            endpoint = TEST_EXECUTION_ENDPOINT_CLOUD
        else:
            endpoint = TEST_EXECUTION_ENDPOINT

        if config.getoption(JIRA_CLIENT_SECRET_AUTH):
            options = get_bearer_auth()
            auth: Union[AuthBase, Tuple[str, str]] = ClientSecretAuth(
                options['BASE_URL'],
                options['CLIENT_ID'],
                options['CLIENT_SECRET']
            )
        elif config.getoption(JIRA_API_KEY):
            options = get_api_key_auth()
            auth = ApiKeyAuth(options['API_KEY'])
        elif config.getoption(JIRA_TOKEN):
            options = get_api_token_auth()
            auth = TokenAuth(options['TOKEN'])
        else:
            options = get_basic_auth()
            auth = (options['USER'], options['PASSWORD'])

        publisher = XrayPublisher(  # type: ignore
            base_url=options['BASE_URL'],
            endpoint=endpoint,
            auth=auth,
            verify=options['VERIFY']
        )

    plugin = XrayReport(config, publisher)
    config.pluginmanager.register(plugin=plugin, name=XRAY_PLUGIN)


