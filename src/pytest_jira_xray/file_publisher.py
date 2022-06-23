import json
import os
from pathlib import Path
from typing import Union


class FilePublisher:

    def __init__(self, filepath: str):
        if filepath is None:
            return
        if os.path.split(filepath)[1] == '':
            raise FileNotFoundError("Provided a path without a trialing file name")

        self._terminal_summary = []
        self.publish = self._publish
        self._filepath: Path = Path(filepath).absolute().resolve()
        self._terminal_summary.append(f"Report File path is {self._filepath}")

    def _publish(self, report_data: Union[dict, list]):
        """
        Save results to a file or raise XrayError.

        :param report_data: test report data to be saved in the file
        """
        if not isinstance(report_data, (list, dict)):
            raise TypeError("Trying to write report of incorrect type")
        self._filepath.parents[0].mkdir(parents=True, exist_ok=True)
        with open(self._filepath, 'w') as report_file:
            json.dump(report_data, report_file, indent=2)
            self._terminal_summary.append(f"Report has been successfully written to {self._filepath}")

    def publish(self, report_data: Union[list, dict]):
        pass  # Do nothing function in case no report file was requested
