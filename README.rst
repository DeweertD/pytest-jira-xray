================
pytest-jira-xray
================

.. image:: https://img.shields.io/pypi/v/pytest-jira-xray.png
   :target: https://pypi.python.org/pypi/pytest-jira-xray
   :alt: PyPi
.. image:: https://github.com/fundakol/pytest-jira-xray/actions/workflows/main.yml/badge.svg?branch=master
   :target: https://github.com/fundakol/pytest-jira-xray/actions?query=workflow?master
   :alt: Build status
.. image:: https://codecov.io/gh/fundakol/pytest-jira-xray/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/fundakol/pytest-jira-xray
   :alt: Code coverage


pytest-jira-xray is a plugin for pytest that uploads test results to JIRA XRAY.


Installation
------------

.. code-block::

    pip install pytest-jira-xray

or

.. code-block::

    python setup.py install


Usage
-----

Creating Jira Xray specific json reports

.. code-block:: bash

    $ pytest --xray-json

Or to specify a file path+name

.. code-block:: bash

    $ pytest --xray-json=path/to/report.json

Uploading results to a Jira server (cloud or self hosted)

.. code-block:: bash

    $ pytest --xray-json

Or to specify a file path+name

.. code-block:: bash

    $ pytest --xray-json=path/to/report.json

Mark a test with JIRA XRAY test ID or list of IDs

.. code-block:: python

    # -- FILE: test_example.py
    import pytest

    @pytest.mark.xray('JIRA-1')
    def test_foo():
        assert True

    @pytest.mark.xray(['JIRA-2', 'JIRA-3'])
        def test_bar():
            assert True


Jira Xray configuration can be provided via Environment Variables:
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

* Jira base URL:

.. code-block:: bash

    $ export XRAY_API_BASE_URL=<Jira base URL>


- Basic authentication (default):

.. code-block:: bash

    $ export XRAY_API_USER=<jira username>
    $ export XRAY_API_PASSWORD=<user password>

- API KEY (`--api-key-auth` option)

.. code-block:: bash

    $ export XRAY_API_KEY=<api key>

- SSL Client Certificate

To disable SSL certificate verification, at the client side (no case-sensitive), default is True: 

.. code-block:: bash

    $ export XRAY_API_VERIFY_SSL=False


Or you can provide path to certificate file

.. code-block:: bash

    $ export XRAY_API_VERIFY_SSL=</path/to/PEM file>


* Authentication with client ID and client secret (`--client-secret-auth` option):

.. code-block:: bash

    $ export XRAY_CLIENT_ID=<client id>
    $ export XRAY_CLIENT_SECRET=<client secret>


* Token authentication (`--token-auth` option)

.. code-block:: bash

    $ export XRAY_API_TOKEN=<user token>

* Test Execution parameters:

.. code-block:: bash

    $ export XRAY_EXECUTION_TEST_ENVIRONMENTS="Env1 Env2 Env3"
    $ export XRAY_EXECUTION_FIX_VERSION="1.0"
    $ export XRAY_EXECUTION_REVISION=`git rev-parse HEAD`

    $ export XRAY_EXECUTION_SUMMARY="Smoke tests" # New execution only
    $ export XRAY_EXECUTION_DESC="This is an automated test execution of the smoke tests" # New execution only

If you would prefer to set the Test Execution summary programmatically, then implementing the pytest_xray_summary hook is the way to go. This hook takes one argument *report_summary* which is the value from the command line arguments above. Simply return a string from this hook, and it will be used in the Xray report as the Test Execution summary

* Set the Test Execution summary to a "Smoke tests" without needing the command line argument

.. code-block:: python

    @pytest.hookimpl
        def pytest_xray_summary(report_summary):
            return "Smoke tests"


Setting the Xray Test Execution Issue Key
+++++++++++++++++++++++++++++++++++++++++

When running auto tests, sometimes it may be desirable to set, update, or overwrite the results of an existing Test Execution. Providing the issue key for the existing Test Execution can be done using one of the following configuration options.

* Use the Command Line Options to set the test execution issue key to "JIRAEX-1":

.. code-block:: bash

    $ pytest --xray-json --execution=JIRAEX-1
    $ pytest --xray-json --xrayexecution=JIRAEX-1
    $ pytest --xray-json --xray-execution=JIRAEX-1

If you would prefer to set the Test Execution Key programmatically, then implementing the pytest_xray_execution_key hook is the way to go. This hook takes one argument *execution_key* which is the value from the command line arguments above. Simply return a string from this hook, and it will be used in the Xray report as the Test Execution Key

* Set the Test Execution Key to "JIRAEX-1" without needing the command line argument

.. code-block:: python

    @pytest.hookimpl
    def pytest_xray_execution_key():
        return "JIRAEX-1"

* Modify the command line value as desired, or overwrite it with a different key entirely. This results in the Test Execution Key "JIRAEX-2"

.. code-block:: bash

    $ pytest --xray-json --execution=JIRAEX

.. code-block:: python

    @pytest.hookimpl
    def pytest_xray_execution_key(execution_key):
        return f"{execution_key}-2"

Read more about Pytest Hooks `here <https://docs.pytest.org/en/7.1.x/how-to/writing_hook_functions.html>`_

Setting the Xray Test Execution's Project Key
+++++++++++++++++++++++++++++++++++++++++++++

When running auto tests, you will usually want to create a new Test Execution for the most recent test results. Providing a project key for the Test Execution allows Xray to automatically create a Test Execution with all the results from the Pytest execution. This can easily be done using one of the following configuration options.

* Use the Command Line Options to set the Project Key to "JIRAEX":

.. code-block:: bash

    $ pytest --xray-json --project-key=JIRAEX
    $ pytest --xray-json --projectkey=JIRAEX
    $ pytest --xray-json --project=JIRAEX

If you would prefer to set the Project Key programmatically, then implementing the pytest_xray_project hook is the way to go. This hook takes one argument *project_key* which is the value from the command line arguments above. Simply return a string from this hook, and it will be used in the Xray report as the Test Execution's Project Key, allowing Xray to automatically create the Test Execution in the desired Jira Project.

* Set the Project Key to "JIRAEX" without needing the command line argument

.. code-block:: python

    @pytest.hookimpl
    def pytest_xray_project(project_key):
        return "JIRAEX"

* Modify the command line value as desired, or overwrite it with a different key entirely. Running Pytest as shown below results in the Project Key of "JIRA_EX"

.. code-block:: bash

    $ pytest --xray-json --project=JIRA

.. code-block:: python

    @pytest.hookimpl
    def pytest_xray_project(project_key):
        return f"{project_key}_EX"

Read more about Pytest Hooks `here <https://docs.pytest.org/en/7.1.x/how-to/writing_hook_functions.html>`_


Setting the Xray Test Execution Summary
+++++++++++++++++++++++++++++++++++++++

When running auto tests, setting the test execution summary can be useful in explaining the purpose of the execution

* Use the Command Line Options to set the test execution summary to "smoke tests":

.. code-block:: bash

    $ pytest --xray-json --execution=JIRAEX-1 --execution-summary='smoke tests'
    $ pytest --xray-json --execution=JIRAEX-1 --executionsummary='smoke tests'
    $ pytest --xray-json --execution=JIRAEX-1 --summary='smoke tests'

If you would prefer to set the summary programmatically, then implementing the pytest_xray_summary hook is the way to go. This hook takes one argument *execution_summary* which is the value from the command line arguments above. Simply return a string from this hook, and it will be used in the Xray report as the Test Execution summary

* Set the Test Execution summary to "smoke tests" without needing the command line argument

.. code-block:: python

    @pytest.hookimpl
    def pytest_xray_summary():
        return "smoke tests"


Test Run Status
++++++++++++++

Xray test run statuses are represented by simple strings, the pytest-jira-xray plugin automatically supports the default statuses from self hosted Jira servers, or Jira Cloud servers. Switching between which status is used is as easy as adding the `--cloud` command line parameter to your pytest run.

* Uses Jira Server defined test run status:

.. code-block:: bash

    $ pytest --xray-json

* Uses Jira Cloud defined test run status:

.. code-block:: bash

    $ pytest --xray-json --cloud

You can also implement your own logic for setting the final test run status by implementing the `pytest_xray_status_mapping` hook. In the simplest case, you only need to return a string from this hook which matches the values from your Jira Server's test run status.

.. note::
    The pytest-jira-xray plugin supports merging tests with :ref:`Duplicate IDs<Duplicate ID>` into a single result. This is done using the python `max` function.  Therefore, if you use custom IDs or logic for test run statuses, you should utilise the OrderedEnum FunctionalAPI to define a status hierarchy.

* Manually define test run status in the `pytest_xray_status_mapping` hook method, and support merging:

.. code-block:: python

    from pytest-jira-xray.test_run import OrderedEnum

    @pytest.hookimpl
    def pytest_xray_status_mapping(is_cloud, node_id, report_outcome, failure_when, wasxfail):
        TestStatus = OrderedEnum("TestStatus", [("TESTPASS", "FUNCTIONAL PASS"),("TESTFAIL", "FUNCTIONAL FAIL")])
        return TestStatus.TESTPASS if report_outcome == "pass" else TestStatus.TESTFAIL

Read more about Python's Enum Functional API `here <https://docs.python.org/3.9/library/enum.html#functional-api>`_

Upload results
++++++++++++++

* Upload results to new test execution:

.. code-block:: bash

    $ pytest --jira-xray


* Upload results to existing test execution:

.. code-block:: bash

    $ pytest --jira-xray --execution TestExecutionId


* Upload results to existing test plan (new test execution will be created):

.. code-block:: bash

    $ pytest --jira-xray --testplan TestPlanId


* Store results in a file instead of exporting directly to a XRAY server

.. code-block:: bash

    $ pytest --jira-xray --xraypath=xray.json


* Use with Jira cloud:

.. code-block:: bash

    $ pytest --jira-xray --cloud


Jira authentication
+++++++++++++++++++

Default Jira authentication is basic authentication, but you can select different authentication.

* Jira client secret authentication:

.. code-block:: bash

    $ pytest --jira-xray --client-secret-auth


* Jira API KEY authentication:

.. code-block:: bash

    $ pytest --jira-xray --api-key-auth


* Jira token authentication:

.. code-block:: bash

    $ pytest --jira-xray --token-auth

.. _Multiple ID:

Multiple ID Support
+++++++++++++++++++

Tests can be marked to handle multiple Jira tests by adding multiple issue keys. Example:

.. code-block:: python

    # -- FILE: test_example.py
    import pytest

    @pytest.mark.xray('JIRA-1', 'JIRA-2')
    def test_my_process():
        assert True

If the test fails, both JIRA-1 and JIRA-2 tests will be marked as fail. The
failure comment will contain the same message for both tests.

This situation can be useful for validation tests or tests that probe multiple
functionalities in a single run, to reduce execution time.

.. _Duplicate ID:

Duplicated ID Support
++++++++++++++++++++++

By default, the jira-xray plugin does not allow to have multiple tests marked with
the same identifier, like in this case:

.. code-block:: python

    # -- FILE: test_example.py
    import pytest

    @pytest.mark.xray('JIRA-1')
    def test_my_process_1():
        assert True

    @pytest.mark.xray('JIRA-1')
    def test_my_process_2():
        assert True

However, depending how the user story and the associated test are formulated,
this scenario may be useful. The option --allow-duplicate-ids will perform the tests
even when duplicate ids are present. The JIRA-1 test result will be created according to
the following rules:

- The comment will be the comment from each of the test, separated by a horizontal divider.
- The status will be the intuitive combination of the individual results: if ``test_my_process_1`` 
  is a ``PASS`` but ``test_my_process_2`` is a ``FAIL``, ``JIRA-1`` will be marked as ``FAIL``.


Hooks
+++++

There is possibility to modify a XRAY report before it is send to a server by ``pytest_xray_results`` hook.

.. code-block:: python

    def pytest_xray_results(results, session):
        results['info']['user'] = 'pytest'


IntelliJ integration
++++++++++++++++++++

When you want to synchronize your test results via. Pytest integration in IntelliJ, you need to configure the following:

1. Use the *pytest* test configuration template and add `--jira-xray -o log_cli=true` to *Additional Arguments*

.. image:: https://user-images.githubusercontent.com/22340156/145638520-c6bf56d2-089e-430c-94ae-ac8122a3adea.png
   :target: https://user-images.githubusercontent.com/22340156/145638520-c6bf56d2-089e-430c-94ae-ac8122a3adea.png

2. Disable `--no-summary` in *Settings*

.. image:: https://user-images.githubusercontent.com/22340156/145638538-71590ec8-86c6-4b93-9a99-460b4e38e153.png
   :target: https://user-images.githubusercontent.com/22340156/145638538-71590ec8-86c6-4b93-9a99-460b4e38e153.png


Troubleshooting
+++++++++++++++

This section holds information about common issues.

`The Test XXX is in a non-executable status`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Problem: The test is not executable by the user.

* Solution: Make sure, that your test is not deactivated, approved and ready to use in Jira.

`Error message from server: fixVersions: fixVersions`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Problem: The version is malformed or doesn't exist.

* Solution: Make sure the version exists and the name matches the existing version and that only one version is used.


References
----------

- XRay import execution endpoint: `<https://docs.getxray.app/display/XRAY/Import+Execution+Results>`_
