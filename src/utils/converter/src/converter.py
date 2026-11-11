import csv
import json
import os
from pathlib import Path
from typing import Any

import pandas as pd

from utils.converter.src.vars import CSV_CONFIG_FILE, CSV_OUTPUT_FILE, JSON_OUTPUT_FILE


class Converter:
    def __init__(self, json_files: list[str]) -> None:
        self.json_files = json_files
        self.merged_data = self.merge_json_files()

        self.write_merged_data()

    def merge_json_files(self) -> list[list[str] | Any]:
        merged_data = []

        for file_path in self.json_files:
            path_obj = Path(file_path)

            with Path.open(path_obj, encoding="utf-8") as file:
                data = json.load(file)

                if isinstance(data, list):
                    self.merged_data.extend(data)
                else:
                    self.merged_data.append(data)

        return merged_data

    def write_merged_data(self) -> None:
        with Path.open(JSON_OUTPUT_FILE, "w", encoding="utf-8") as file:
            json.dump(self.merged_data, file)

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
        json_list: list[dict[str, Any]],
    ) -> list[Any]:
        formatted_json_list = []

        for json_lmt in json_list:
            formatted_json_lmt = self.format_keys(json_lmt)
            formatted_json_list.append(formatted_json_lmt)

        return formatted_json_list

    def load_json_from_file_to_format(self) -> list[Any]:
        with Path.open(JSON_OUTPUT_FILE, encoding="utf-8") as file:
            json_file = json.load(file)
            serial_formatted_json_file = self.fmt_serial_number(json_file)

            return self.format_json_list_keys(serial_formatted_json_file)

    def fmt_4ascii_4hex(self, serial: list[int]) -> str:
        ascii_part = "".join(chr(b) for b in serial[:4])
        hex_part = "".join(f"{b:02X}" for b in serial[4:])
        return f"{ascii_part}-{hex_part}"

    def fmt_serial_number(
        self,
        json_list: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        fmt_json = []

        for json_obj in json_list:
            for test in json_obj.get("tests", []):
                serial_path = test.get("results", {}).get("data", {}).get("gpon", {})

                if isinstance(serial_path.get("ontSerialNumber"), list):
                    serial_number = serial_path["ontSerialNumber"]
                    fmt_serial = self.fmt_4ascii_4hex(serial_number)
                    serial_path["ontSerialNumber"] = fmt_serial

            fmt_json.append(json_obj)

        return fmt_json

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

    def write_csv(self, resource: list[dict[str, str]]) -> None:
        column_order = self.load_column_order(CSV_CONFIG_FILE)

        with Path.open(CSV_OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=column_order)
            writer.writeheader()

            for row in resource:
                ordered_row = {col: row.get(col, "") for col in column_order}
                writer.writerow(ordered_row)

    def save_to_excel(self, output_path: str) -> str:
        data_frame = pd.read_csv(CSV_OUTPUT_FILE, encoding="latin-1")
        excel_path = output_path.partition(".")[0] + ".xlsx"
        data_frame.to_excel(excel_path, index=False)
        return excel_path

    def open_report(self, file_path: str) -> None:
        os.startfile(file_path)
