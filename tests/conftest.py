import pytest
from _pytest.pytester import Pytester

pytest_plugins = "pytester"


@pytest.fixture(autouse=True)
def chdir(tmp_path_factory, monkeypatch):
    base_dir = tmp_path_factory.mktemp('publisher', numbered=True)
    monkeypatch.chdir(base_dir)


@pytest.fixture
def make_test_py_file(pytester: Pytester) -> callable:
    def _make_test_py_file(name, file_content):
        test = dict()
        test[f"test_{name}"] = file_content
        pytester.makepyfile(**test)

    return _make_test_py_file


@pytest.fixture
def marked_xray_pass(request, make_test_py_file):
    make_test_py_file(request.fixturename, """
            import pytest
            
            
            @pytest.mark.xray('JIRA-1')
            def test_pass():
                '''This is a test Doc String'''
                assert True
            """)


@pytest.fixture
def marked_xray_fail(request, make_test_py_file):
    make_test_py_file(request.fixturename, """
        import pytest

        @pytest.mark.xray('JIRA-2')
        def test_fail():
            assert False
        """)


@pytest.fixture
def marked_xray_exception(request, make_test_py_file):
    make_test_py_file(request.fixturename, """
        import pytest

        @pytest.mark.xray('JIRA-3')
        def test_expected_exception():
            raise ValueError("This is not expected to happen")
        """)


@pytest.fixture
def marked_xray_expected_fail(request, make_test_py_file):
    make_test_py_file(request.fixturename, """
        import pytest

        @pytest.mark.xray('JIRA-4')
        @pytest.mark.xfail
        def test_expected_fail():
            assert False
        """)


@pytest.fixture
def marked_xray_expected_exception(request, make_test_py_file):
    make_test_py_file(request.fixturename, """
        import pytest

        @pytest.mark.xray('JIRA-5')
        def test_expected_exception():
            with pytest.raises(ValueError) as v_error:
                raise ValueError("This is expected to happen")
        """)


@pytest.fixture
def marked_xray_ignore(request, make_test_py_file):
    make_test_py_file(request.fixturename, """
        import pytest

        @pytest.mark.not_xray
        def test_ignored():
            assert True
        """)


@pytest.fixture
def marked_xray_test_error(request, make_test_py_file):
    make_test_py_file(request.fixturename, """
        import pytest

        @pytest.mark.xray('JIRA-6')
        def test_error(undefined_fixture):
            assert True
        """)


@pytest.fixture
def marked_xray_test_skipped(request, make_test_py_file):
    make_test_py_file(request.fixturename, """
        import pytest

        @pytest.mark.xray('JIRA-7')
        @pytest.mark.skip
        def test_skipped():
            assert True
        """)


@pytest.fixture
def anonymous_pass(request, make_test_py_file):
    make_test_py_file(request.fixturename, """
        import pytest

        def test_pass():
            assert True
        """)


@pytest.fixture
def anonymous_fail(request, make_test_py_file):
    make_test_py_file(request.fixturename, """
        import pytest

        def test_fail():
            assert False
        """)


@pytest.fixture
def anonymous_exception(request, make_test_py_file):
    make_test_py_file(request.fixturename, """
        import pytest

        def test_expected_exception():
            raise ValueError("This is not expected to happen")
        """)


@pytest.fixture
def anonymous_expected_fail(request, make_test_py_file):
    make_test_py_file(request.fixturename, """
        import pytest

        @pytest.mark.xfail
        def test_expected_fail():
            assert False
        """)


@pytest.fixture
def anonymous_expected_exception(request, make_test_py_file):
    make_test_py_file(request.fixturename, """
        import pytest

        def test_expected_exception():
            with pytest.raises(ValueError) as v_error:
                raise ValueError("This is expected to happen")
        """)


@pytest.fixture
def anonymous_test_error(request, make_test_py_file):
    make_test_py_file(request.fixturename, """
        import pytest

        def test_expected_exception(undefined_fixture):
            assert True
        """)


@pytest.fixture
def anonymous_test_skipped(request, make_test_py_file):
    make_test_py_file(request.fixturename, """
        import pytest

        @pytest.mark.skip
        def test_expected_exception(undefined_fixture):
            assert True
        """)
