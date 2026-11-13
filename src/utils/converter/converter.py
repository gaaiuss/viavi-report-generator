import csv
import json
import os
from pathlib import Path
from typing import Any

import pandas as pd

from utils.converter.vars import (
    CSV_CONFIG_FILE,
    CSV_OUTPUT_FILE,
    JSON_FILES_PATHS,
)


class Converter:
    def __init__(self, json_files_path: list[Path]) -> None:
        self.json_files = json_files_path
        self.merged_json = []

        self.merge_json_files()
        self.format_json()
        # print(self.merged_json, len(self.merged_json))
        self.write_csv()

    def merge_json_files(self) -> None:
        for json_file in self.json_files:
            with Path.open(json_file, encoding="utf-8") as file:
                data = json.load(file)

                if isinstance(data, list):
                    self.merged_json.extend(data)
                else:
                    self.merged_json.append(data)

    def format_json(self) -> None:
        self.merged_json = self.format_all_json_list_keys()
        self.merged_json = self.format_ont_serial_number()

    def format_all_json_list_keys(self) -> list[dict[str, str]]:
        return [self.format_json_keys(json_item) for json_item in self.merged_json]

    def format_json_keys(
        self,
        json_item: dict[str, Any],
        parent_key: str = "",
        result: dict[str, Any] | None = None,
    ) -> dict[str, str]:
        """
        Format all json items into a single "key, value" pattern.

        If the item is a dictionary: Format each object key to append its parent
        key to its own.

        If the item is a list: Format all its children into a enumerated object
        to flatten it later as a dictionary.

        When there are no more lists or dicts items: Append the formatted key
        to its respective item.
        """
        if result is None:
            result = {}

        for key, value in json_item.items():
            if isinstance(value, dict):
                for value_key, value_value in value.items():
                    new_key = (
                        f"{parent_key}.{value_key}"
                        if parent_key
                        else f"{key}.{value_key}"
                    )
                    result[new_key] = value_value

            elif isinstance(value, list):
                for i in value:
                    self.format_json_keys(i, key, result)

        return result

    def new_format_keys(self) -> None: ...

    def format_ont_serial_number(
        self,
    ) -> list[dict[str, str]]:
        """
        Format the ONT Serial Number which part of it is ascii and the other
        hexadecimal numbers.
        """
        fmt_json = []

        for json_obj in self.merged_json:
            serial_number_key = "results.data.gpon.ontSerialNumber"
            serial_number = json_obj.get(serial_number_key, {})

            # If it finds the serial pattern (list of hexadecimal) formats the
            # serial to ascii
            if isinstance(serial_number, list):
                fmt_serial = self.format_to_4ascii_4hex(serial_number)
                json_obj[serial_number_key] = fmt_serial

            fmt_json.append(json_obj)

        return fmt_json

    def format_to_4ascii_4hex(self, serial_number: list[int]) -> str:
        ascii_part = "".join(chr(b) for b in serial_number[:4])
        hex_part = "".join(f"{b:02X}" for b in serial_number[4:])
        return f"{ascii_part}-{hex_part}"

    def write_csv(self) -> None:
        column_order = self.load_column_order(CSV_CONFIG_FILE)

        with Path.open(CSV_OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=column_order)
            writer.writeheader()

            for json_item in self.merged_json:
                ordered_row = {col: json_item.get(col, "") for col in column_order}
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

    def __str__(self) -> str:
        return f"{__class__.__name__}\n(JSON files selected:{self.json_files})"


if __name__ == "__main__":
    converter = Converter(JSON_FILES_PATHS)
