import pytest
from _pytest.pytester import Pytester

pytest_plugins = "pytester"


@pytest.fixture
def marked_xray_pass(pytester: Pytester):
    pytester.makepyfile("""
        import pytest

        @pytest.mark.xray('JIRA-1')
        def test_pass():
            assert True
        """)


@pytest.fixture
def marked_xray_expected_exception(pytester: Pytester):
    pytester.makepyfile("""
        import pytest

        @pytest.mark.xray('JIRA-4')
        def test_expected_exception():
            with pytest.raises(ValueError) as v_error:
                raise ValueError("This is expected to happen")
        """)


@pytest.fixture
def marked_xray_expected_fail(pytester: Pytester):
    pytester.makepyfile("""
        import pytest

        @pytest.mark.xray('JIRA-3')
        @pytest.mark.xfail
        def test_expected_fail():
            assert False
        """)


@pytest.fixture
def marked_xray_fail(pytester: Pytester):
    pytester.makepyfile("""
        import pytest

        @pytest.mark.xray('JIRA-2')
        def test_fail():
            assert False
        """)


@pytest.fixture
def anonymous_xray_pass(pytester: Pytester):
    pytester.makepyfile("""
        import pytest

        def test_pass():
            assert True
        """)


@pytest.fixture
def anonymous_xray_expected_exception(pytester: Pytester):
    pytester.makepyfile("""
        import pytest

        def test_expected_exception():
            with pytest.raises(ValueError) as v_error:
                raise ValueError("This is expected to happen")
        """)


@pytest.fixture
def anonymous_xray_expected_fail(pytester: Pytester):
    pytester.makepyfile("""
        import pytest

        @pytest.mark.xfail
        def test_expected_fail():
            assert False
        """)


@pytest.fixture
def anonymous_xray_fail(pytester: Pytester):
    pytester.makepyfile("""
        import pytest

        def test_fail():
            assert False
        """)
