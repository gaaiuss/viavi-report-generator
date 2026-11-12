import csv
import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd

from utils.converter.vars import (
    CSV_CONFIG_FILE,
    CSV_OUTPUT_FILE,
    JSON_OUTPUT_FILE,
    JSON_TEST_DATA_FOLDER,
)

if TYPE_CHECKING:
    from collections.abc import Iterator


class Converter:
    def __init__(self, json_files_path: Iterator[Any]) -> None:
        self.merged_json = []
        self.json_files = json_files_path

        self.merge_json_files()
        self.format_json()
        self.write_json()

    def merge_json_files(self) -> None:
        for json_file in self.json_files:
            json_path = Path(json_file)

            with Path.open(json_path, encoding="utf-8") as file:
                data = json.load(file)

                if isinstance(data, list):
                    self.merged_json.extend(data)
                else:
                    self.merged_json.append(data)

    def format_json(self) -> None:
        self.merged_json = self.format_json_list_keys()
        self.merged_json = self.format_serial_number()

    def write_json(self) -> None:
        with Path.open(JSON_OUTPUT_FILE, "w", encoding="utf-8") as file:
            json.dump(self.merged_json, file)

    def format_keys(
        self,
        json_item: Any,
        parent_key: str = "",
    ) -> dict[str, Any]:
        """
        Format all json items into a single "key, value" pattern.

        If the item is a dictionary: Format each object key to append its parent
        key to its own.

        If the item is a list: Format all its children into a enumerated object
        to flatten it later as a dictionary.

        When there are no more lists or dicts items: Append the formatted key
        to its respective item.
        """
        result = {}

        # Format the dict json item key name appending the parent key to its key
        # if it has a parent.
        if isinstance(json_item, dict):
            for key, value in json_item.items():
                full_key = f"{parent_key}.{key}" if parent_key else key

                # calls itself again with the correct key
                self.format_keys(value, full_key)

        # Checks if the json item is a list and if all its children are instances
        # of a list or dict. If this is the case, flattens then with enumerate
        # to send the correct keys to the final result.
        elif isinstance(json_item, list) and all(
            isinstance(i, (dict, list)) for i in json_item
        ):
            for _index, item in enumerate(json_item):
                self.format_keys(item)

        # If the items are already flattened, append the correct item in the
        # result dict
        else:
            result[parent_key] = json_item

        return result

    def format_json_list_keys(
        self,
    ) -> list[dict[str, str]]:
        formatted_json_list: list[dict[str, str]] = []

        for json_lmt in self.merged_json:
            formatted_json_lmt = self.format_keys(json_lmt)
            formatted_json_list.append(formatted_json_lmt)

        return formatted_json_list

    def format_serial_number(
        self,
    ) -> list[dict[str, str]]:
        fmt_json = []

        for json_obj in self.merged_json:
            for test in json_obj.get("tests", []):
                serial_path = test.get("results", {}).get("data", {}).get("gpon", {})

                if isinstance(serial_path.get("ontSerialNumber"), list):
                    serial_number = serial_path["ontSerialNumber"]
                    fmt_serial = self.fmt_4ascii_4hex(serial_number)
                    serial_path["ontSerialNumber"] = fmt_serial

            fmt_json.append(json_obj)

        return fmt_json

    def fmt_4ascii_4hex(self, serial: list[int]) -> str:
        ascii_part = "".join(chr(b) for b in serial[:4])
        hex_part = "".join(f"{b:02X}" for b in serial[4:])
        return f"{ascii_part}-{hex_part}"

    def write_csv(self, resource: list[dict[str, str]]) -> None:
        column_order = self.load_column_order(CSV_CONFIG_FILE)

        with Path.open(CSV_OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=column_order)
            writer.writeheader()

            for row in resource:
                ordered_row = {col: row.get(col, "") for col in column_order}
                writer.writerow(ordered_row)

    def load_column_order(self, csv_config_path: Path) -> list[str]:
        with Path.open(csv_config_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [
                row["column"]
                for row in sorted(
                    reader,
                    key=lambda r: int(r["order"]),
                )
            ]

    def save_to_excel(self, output_path: str) -> str:
        data_frame = pd.read_csv(CSV_OUTPUT_FILE, encoding="latin-1")
        excel_path = output_path.partition(".")[0] + ".xlsx"
        data_frame.to_excel(excel_path, index=False)
        return excel_path

    def open_report(self, file_path: str) -> None:
        os.startfile(file_path)


if __name__ == "__main__":
    PDFS_FOLDER_PATH = JSON_TEST_DATA_FOLDER
    PDF_FILES_PATH = Path(PDFS_FOLDER_PATH).iterdir()
    converter = Converter(PDF_FILES_PATH)
