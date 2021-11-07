import math
from dataclasses import dataclass
from pprint import pformat


@dataclass
class Key:
    """All required information about a single keyboard key"""

    x_unit: float
    y_unit: float
    width: float
    height: float
    number: int
    legend: str
    _column: int = 0
    rotation: int = 0
    diodenetnum: int = 0
    colnetnum: int = 0
    rownetnum: int = 0

    @property
    def row(self) -> int:
        return math.floor(self.y_unit)

    @property
    def column(self) -> int:
        return self._column

    @column.setter
    def column(self, value: int):
        self._column = value

    def __repr__(self):
        return pformat(vars(self))
