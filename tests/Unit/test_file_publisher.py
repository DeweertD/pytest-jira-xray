import json
from pathlib import Path, PurePosixPath

from pytest_jira_xray.file_publisher import FilePublisher
import pytest


@pytest.mark.parametrize('file_name', ['file.json', 'path/to/file', 'file', '/file.json', '/path/to/file', '/file'])
def test_file_publisher_creates_file(file_name):
    if PurePosixPath(file_name).is_absolute():
        file_name = PurePosixPath(file_name).relative_to(PurePosixPath(file_name).root)
        file_name = Path(file_name).absolute().resolve()
        assert file_name.is_absolute()
    file_path = Path(file_name)
    assert not file_path.exists()
    file_publisher = FilePublisher(str(file_path))
    file_publisher.publish({})
    assert file_path.exists()


@pytest.mark.parametrize('file_name', ['file/', 'path/to/file/', '/file/', '/path/to/file/'])
def test_file_publisher_needs_file_name(file_name):
    with pytest.raises(FileNotFoundError) as error:
        FilePublisher(file_name)


@pytest.mark.parametrize('test_data', [{}, [], {"execution": "JIRA-1", "tests": []}])
def test_file_publisher_with_good_data(test_data, tmp_path_factory):
    file_name = "report.json"
    file_publisher = FilePublisher(file_name)
    file_publisher.publish(test_data)
    assert Path(file_name).exists()
    with open(file_name) as data:
        assert json.load(data) == test_data


# noinspection PyTypeChecker
@pytest.mark.parametrize('test_data',
                         [None, '', 'file.json', '\\', Path('file.json'), 1, False, {"data": Path("bad_data")}])
def test_file_publisher_with_bad_data(test_data, tmp_path_factory):
    with pytest.raises(TypeError) as error:
        file_name = "report.json"
        file_publisher = FilePublisher(file_name)
        file_publisher.publish(test_data)
