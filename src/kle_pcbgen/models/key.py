from dataclasses import dataclass


@dataclass
class Key:
    """All required information about a single keyboard key"""

    x_unit: float
    y_unit: float
    width: float
    height: float
    num: int
    legend: str
    row: int = 0
    col: int = 0
    rot: int = 0
    diodenetnum: int = 0
    colnetnum: int = 0
    rownetnum: int = 0
