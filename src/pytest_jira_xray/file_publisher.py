import json
import logging
from pathlib import Path
from typing import Union

from pytest_jira_xray.exceptions import XrayError

logger = logging.getLogger(__name__)


class FilePublisher:

    def __init__(self, filepath: Union[str, bool]):
        if filepath is False:
            self.publish = self._publish_none
            return
        self.publish = self._publish
        self.filepath: Path = Path(filepath)

    def _publish(self, data: dict) -> str:
        """
        Save results to a file or raise XrayError.

        :param data: data to save
        :return: file path where data was saved
        """
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.filepath, 'w', encoding='UTF-8') as file:
                json.dump(data, file, indent=2)
        except TypeError as e:
            logger.exception(e)
            raise XrayError(f'Cannot save data to file: {self.filepath}') from e
        return f'{self.filepath}'

    def _publish_none(self, data: dict):
        pass
