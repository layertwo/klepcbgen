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
        self._columns = [] # type: List[List[Key]]
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
    def rows(self):
        """Keyboard rows"""
        if not self._rows:
            self._rows = [
                list(g) for _, g in groupby(self._keys, key=attrgetter("row"))
            ]
        return self._rows

    @property
    def columns(self):
        """Keyboard columns"""
        if not self._columns:
            for row in self.rows:
                for _key, col in zip(row, range(len(row))):
                    _key.column = col
            self._columns = [
                list(g)
                for _, g in groupby(
                    sorted(self._keys, key=attrgetter("column")), attrgetter("column")
                )
            ]
        return self._columns

    def print_key_info(self) -> None:
        """Print information for this keyboard"""

        print("Keyboard information:")
        print(f"Name: {self.name}")
        print(f"Author: {self.author}")
        print(
            f"Contains: {len(self._keys)} keys, grouped into {len(self.rows)} rows and {len(self.columns)} columns"
        )
