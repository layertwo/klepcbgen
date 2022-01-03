from itertools import groupby
from operator import attrgetter
from pprint import pformat
from typing import Any, Iterator, List

from kle_pcbgen.models.key import Key


class Keyboard:
    """Represents an entire keyboard layout with all the keys positioned and
    grouped in rows and columns"""

    def __init__(self, name: str = "", author: str = "") -> None:
        self._keys = []  # type: List[Key]
        self._rows = []  # type: List[List[Key]]
        self._columns = []  # type: List[List[Key]]
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

    def __repr__(self) -> str:
        return pformat({"name": self.name, "author": self.author, "keys": self._keys})

    def append(self, s: Any) -> None:
        self._keys.append(s)

    @property
    def rows(self) -> List[List[Key]]:
        """Keyboard rows"""
        return self._rows

    @property
    def columns(self) -> List[List[Key]]:
        """Keyboard columns"""
        return self._columns

    def generate_matrix(self) -> None:
        """
        Generate rows and columns
        """
        rows = [
            list(g)
            for _, g in groupby(
                sorted(self._keys, key=attrgetter("number")), key=attrgetter("row")
            )
        ]

        max_row_len = max(map(len, rows))
        for row_idx, row in enumerate(rows):
            prev_col = 0
            if row_idx > 0:
                # get previous row x values
                prev_row_x = rows[row_idx - 1]
            for key_idx, (key, col) in enumerate(zip(row, range(max_row_len))):
                if row_idx > 0 and key_idx > 0:
                    nearest_key = min(
                        prev_row_x, key=lambda v: abs(key.x_unit - v.x_unit)
                    )
                    new_col = nearest_key.column

                    # check if previous key is assigned to calculated column
                    if prev_col == new_col:
                        new_col += 1

                    if abs(new_col - prev_col) > 1 and key.width < 1.5:
                        print(f"new col {new_col} difference greater than 1 {prev_col}")
                        new_col -= 1

                    key.column = new_col
                else:
                    key.column = col

                prev_col = key.column

        columns = [
            list(g)
            for _, g in groupby(
                sorted(self._keys, key=attrgetter("column")), attrgetter("column")
            )
        ]
        self._rows = rows
        self._columns = columns

    def print_key_info(self) -> None:
        """Print information for this keyboard"""

        print("Keyboard information:")
        print(f"Name: {self.name}")
        print(f"Author: {self.author}")
        print(
            f"Contains: {len(self._keys)} keys, grouped into {len(self.rows)} rows and {len(self.columns)} columns"
        )
