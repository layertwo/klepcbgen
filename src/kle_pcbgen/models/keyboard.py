from typing import Any, Iterator, List

from kle_pcbgen.models.key import Key
from kle_pcbgen.models.keyblock import KeyBlockCollection


class Keyboard:
    """Represents an entire keyboard layout with all the keys positioned and
    grouped in rows and columns"""

    def __init__(self, name: str = "", author: str = "") -> None:
        self._keys = []  # type: List[Key]
        self.rows = KeyBlockCollection()
        self.columns = KeyBlockCollection()
        self.name = name
        self.author = author

    def __getitem__(self, idx: int) -> Key:
        return self._keys[idx]

    def __setitem__(self, idx: int, data: Any) -> None:
        self._keys[idx] = data

    def __iter__(self) -> Iterator[Key]:
        for key in self._keys:
            yield key

    def __len__(self) -> int:
        return len(self._keys)

    def append(self, s: Any) -> None:
        self._keys.append(s)

    def add_key_to_row(self, idx: int, key_index: int) -> None:
        """Add a key to a specific row"""
        self.rows[idx] = key_index

    def add_key_to_col(self, idx: int, key_index: int) -> None:
        """Add a key to a specific column"""
        self.columns[idx] = key_index

    def print_key_info(self) -> None:
        """Print information for this keyboard"""

        print("Keyboard information:")
        print(f"Name: {self.name}")
        print(f"Author: {self.author}")
        print(
            f"Contains: {len(self._keys)} keys, grouped into {len(self.rows)} rows and {len(self.columns)} columns"
        )
