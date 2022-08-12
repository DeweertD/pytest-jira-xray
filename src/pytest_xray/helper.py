import os
import re
from os import environ
from typing import (
    Any,
    Dict,
    List,
    Optional
)

from pytest_xray.constant import (
    ENV_XRAY_API_BASE_URL,
    ENV_XRAY_API_KEY,
    ENV_XRAY_API_PASSWORD,
    ENV_XRAY_API_TOKEN,
    ENV_XRAY_API_USER,
    ENV_XRAY_API_VERIFY_SSL,
    ENV_XRAY_CLIENT_ID,
    ENV_XRAY_CLIENT_SECRET
)
from pytest_xray.exceptions import XrayError



# This is the hierarchy of the Status, from bottom to top.
# When merging two statuses, the highest will be picked.
# For example, a PASS and a FAIL will result in a FAIL,
# A TODO and an ABORTED in an ABORTED, A TODO and a PASS in a TODO.

# Maps the Status from the internal Status enum to the string representations
# requested by either the Cloud Jira, or the on-site Jira

# On-site jira uses the enum strings directly


def get_base_options() -> Dict[str, Any]:
    options = {}
    try:
        base_url = environ[ENV_XRAY_API_BASE_URL]
    except KeyError as e:
        raise XrayError(
            f'pytest-jira-xray plugin requires environment variable: {ENV_XRAY_API_BASE_URL}'
        ) from e

    verify = os.environ.get(ENV_XRAY_API_VERIFY_SSL, 'True')

    if verify.upper() == 'TRUE':
        verify = True  # type: ignore
    elif verify.upper() == 'FALSE':
        verify = False  # type: ignore
    else:
        if not os.path.exists(verify):
            raise XrayError(f'Cannot find certificate file "{verify}"')

    options['VERIFY'] = verify
    options['BASE_URL'] = base_url
    return options


def get_basic_auth() -> Dict[str, Any]:
    options = get_base_options()
    try:
        user = environ[ENV_XRAY_API_USER]
        password = environ[ENV_XRAY_API_PASSWORD]
    except KeyError as e:
        raise XrayError(
            'Basic authentication requires environment variables: '
            f'{ENV_XRAY_API_USER}, {ENV_XRAY_API_PASSWORD}'
        ) from e

    options['USER'] = user
    options['PASSWORD'] = password
    return options


def get_bearer_auth() -> Dict[str, Any]:
    options = get_base_options()
    try:
        client_id = environ[ENV_XRAY_CLIENT_ID]
        client_secret = environ[ENV_XRAY_CLIENT_SECRET]
    except KeyError as e:
        raise XrayError(
            'Bearer authentication requires environment variables: '
            f'{ENV_XRAY_CLIENT_ID}, {ENV_XRAY_CLIENT_SECRET}'
        ) from e

    options['CLIENT_ID'] = client_id
    options['CLIENT_SECRET'] = client_secret
    return options


def get_api_key_auth() -> Dict[str, Any]:
    options = get_base_options()
    try:
        api_key = environ[ENV_XRAY_API_KEY]
    except KeyError as e:
        raise XrayError(
            f'API Key authentication requires environment variable: {ENV_XRAY_API_KEY}'
        ) from e

    options['API_KEY'] = api_key
    return options


def get_api_token_auth() -> Dict[str, Any]:
    options = get_base_options()
    try:
        api_token = environ[ENV_XRAY_API_TOKEN]
    except KeyError as e:
        raise XrayError(
            f'Token authentication requires environment variable: {ENV_XRAY_API_TOKEN}'
        ) from e

    options['TOKEN'] = api_token
    return options


def _from_environ_or_none(name: str) -> Optional[str]:
    if name in environ:
        val = environ[name].strip()
        if len(val) == 0:
            return None
    else:
        return None
    return val


def _first_from_environ(name: str, separator: str = None) -> Optional[str]:
    return next(iter(_from_environ(name, separator)), None)


def _from_environ(name: str, separator: str = None) -> List[str]:
    if name not in environ:
        return []

    param = environ[name]

    if separator:
        source = re.split(separator, param)
    else:
        source = [param]

    # Return stripped non empty values
    return list(filter(lambda x: len(x) > 0, map(lambda x: x.strip(), source)))



