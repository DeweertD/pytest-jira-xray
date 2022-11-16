import pytest
from _pytest.pytester import Pytester

import responses

pytest_plugins = "pytester"

http_server = "http://jira.test.local"


# @pytest.fixture(autouse=True)
# def chdir(tmp_path_factory, monkeypatch):
#     base_dir = tmp_path_factory.mktemp('publisher', numbered=True)
#     monkeypatch.chdir(base_dir)


@pytest.fixture
def make_test_py_file(pytester: Pytester):
    def _make_test_py_file(name, file_content):
        test = dict()
        test[f"test_{name}"] = file_content
        pytester.makepyfile(**test)

    return _make_test_py_file


@pytest.fixture
def marked_xray_pass(request, make_test_py_file):
    make_test_py_file(request.fixturename,
                      """
                          import pytest
              
              
                          @pytest.mark.xray('JIRA-1')
                          def test_pass():
                              '''This is a test Doc String'''
                              assert True
                          """)


@pytest.fixture
def marked_xray_fail(request, make_test_py_file):
    make_test_py_file(request.fixturename,
                      """
                      import pytest
              
                      @pytest.mark.xray('JIRA-2')
                      def test_fail():
                          assert False
                      """)


@pytest.fixture
def marked_xray_exception(request, make_test_py_file):
    make_test_py_file(request.fixturename,
                      """
                      import pytest
              
                      @pytest.mark.xray('JIRA-3')
                      def test_expected_exception():
                          raise ValueError("This is not expected to happen")
                      """)


@pytest.fixture
def marked_xray_expected_fail(request, make_test_py_file):
    make_test_py_file(request.fixturename,
                      """
                      import pytest
              
                      @pytest.mark.xray('JIRA-4')
                      @pytest.mark.xfail
                      def test_expected_fail():
                          assert False
                      """)


@pytest.fixture
def marked_xray_expected_exception(request, make_test_py_file):
    make_test_py_file(request.fixturename,
                      """
                      import pytest
              
                      @pytest.mark.xray('JIRA-5')
                      def test_expected_exception():
                          with pytest.raises(ValueError) as v_error:
                              raise ValueError("This is expected to happen")
                      """)


@pytest.fixture
def marked_xray_ignore(request, make_test_py_file):
    make_test_py_file(request.fixturename,
                      """
                      import pytest
              
                      @pytest.mark.not_xray
                      def test_ignored():
                          assert True
                      """)


@pytest.fixture
def marked_xray_test_error(request, make_test_py_file):
    make_test_py_file(request.fixturename,
                      """
                      import pytest
              
                      @pytest.mark.xray('JIRA-6')
                      def test_error(undefined_fixture):
                          assert True
                      """)


@pytest.fixture
def marked_xray_test_skipped(request, make_test_py_file):
    make_test_py_file(request.fixturename,
                      """
                      import pytest
              
                      @pytest.mark.xray('JIRA-7')
                      @pytest.mark.skip
                      def test_skipped():
                          assert True
                      """)


@pytest.fixture
@pytest.mark.usefixtures('marked_xray_pass',
                         'marked_xray_fail',
                         'marked_xray_exception',
                         'marked_xray_expected_fail',
                         'marked_xray_expected_exception',
                         'marked_xray_ignore',
                         'marked_xray_test_error',
                         'marked_xray_test_skipped')
def marked_xray_test_all():
    pass


@pytest.fixture
def anonymous_pass(request, make_test_py_file):
    make_test_py_file(request.fixturename,
                      """
                      import pytest
              
                      def test_pass():
                          assert True
                      """)


@pytest.fixture
def anonymous_fail(request, make_test_py_file):
    make_test_py_file(request.fixturename,
                      """
                      import pytest
              
                      def test_fail():
                          assert False
                      """)


@pytest.fixture
def anonymous_exception(request, make_test_py_file):
    make_test_py_file(request.fixturename,
                      """
                      import pytest
              
                      def test_expected_exception():
                          raise ValueError("This is not expected to happen")
                      """)


@pytest.fixture
def anonymous_expected_fail(request, make_test_py_file):
    make_test_py_file(request.fixturename,
                      """
                      import pytest
              
                      @pytest.mark.xfail
                      def test_expected_fail():
                          assert False
                      """)


@pytest.fixture
def anonymous_expected_exception(request, make_test_py_file):
    make_test_py_file(request.fixturename,
                      """
                      import pytest
              
                      def test_expected_exception():
                          with pytest.raises(ValueError) as v_error:
                              raise ValueError("This is expected to happen")
                      """)


@pytest.fixture
def anonymous_test_error(request, make_test_py_file):
    make_test_py_file(request.fixturename,
                      """
                      import pytest
              
                      def test_expected_exception(undefined_fixture):
                          assert True
                      """)


@pytest.fixture
def anonymous_test_skipped(request, make_test_py_file):
    make_test_py_file(request.fixturename,
                      """
                      import pytest
              
                      @pytest.mark.skip
                      def test_expected_exception(undefined_fixture):
                          assert True
                      """)


@pytest.fixture
def environment_variables(monkeypatch):
    monkeypatch.setenv('XRAY_API_BASE_URL', http_server)
    monkeypatch.setenv('XRAY_API_USER', 'jirauser')
    monkeypatch.setenv('XRAY_API_PASSWORD', 'jirapassword')
    monkeypatch.setenv('XRAY_CLIENT_ID', 'client_id')
    monkeypatch.setenv('XRAY_CLIENT_SECRET', 'client_secret')
    monkeypatch.setenv('XRAY_API_TOKEN', 'token')
    monkeypatch.setenv('XRAY_API_KEY', 'api_key')


@pytest.fixture(scope='session')
def mock_server():
    with responses.RequestsMock() as resp:
        # dc server
        resp.post(
            f'{http_server}/rest/raven/2.0/import/execution',
            json={'testExecIssue': {'key': '1000'}},
        )
        # cloud server
        resp.post(
            f'{http_server}/api/v2/import/execution',
            json={'key': '1000'},
        )
        resp.post(
            f'{http_server}/api/v2/import/execution',
            body='token',
        )
        yield
