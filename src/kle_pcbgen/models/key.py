import math
from dataclasses import dataclass
from pprint import pformat


@dataclass
class Key:
    """All required information about a single keyboard key"""

    x_unit: float
    y_unit: float
    number: int
    legend: str
    width: float = 1.0
    height: float = 1.0
    _column: int = 0
    rotation: int = 0
    diodenetnum: int = 0
    colnetnum: int = 0
    rownetnum: int = 0
    x2_unit: float = 0.0
    y2_unit: float = 0.0

    @property
    def row(self) -> int:
        return math.floor(self.y_unit)

    @property
    def column(self) -> int:
        return self._column

    @column.setter
    def column(self, value: int):
        if value < 0:
            self._column = 0
        else:
            self._column = value

    def __repr__(self) -> str:
        data = vars(self)
        data["column"] = self._column
        data["row"] = self.row
        return pformat(data)
