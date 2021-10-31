from typing import Any, List

from kle_pcbgen.models.key import Key
from kle_pcbgen.models.keyblock import KeyBlockCollection


class Keyboard:
    """Represents an entire keyboard layout with all the keys positioned and
    grouped in rows and columns"""

    def __init__(self, name: str = "", author: str = "") -> None:
        self.keys = []  # type: List[Key]
        self.rows = KeyBlockCollection()
        self.columns = KeyBlockCollection()
        self.name = name
        self.author = author

    def __getitem__(self, idx: int) -> Key:
        return self.keys[idx]

    def __setitem__(self, idx: int, data: Any) -> None:
        self.keys[idx] = data

    def add_key_to_row(self, row_index: int, key_index: int) -> None:
        """Add a key to a specific row"""
        self.rows.add_key_to_block(row_index, key_index)

    def add_key_to_col(self, col_index: int, key_index: int) -> None:
        """Add a key to a specific column"""
        self.columns.add_key_to_block(col_index, key_index)

    def print_key_info(self) -> None:
        """Print information for this keyboard"""

        print("Keyboard information:")
        print(f"Name: {self.name}")
        print(f"Author: {self.author}")
        print(
            f"Contains: {len(self.keys)} keys, grouped into {len(self.rows.blocks)} rows and {len(self.columns.blocks)} columns"
        )
