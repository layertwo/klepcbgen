from typing import Any, Iterator, List


class KeyBlockCollection:
    """Maintains a collection of _blocks of keyboard keys, such as columns or rows"""

    def __init__(self) -> None:
        self._blocks = []  # type: List[Any]

    def __getitem__(self, idx: int) -> Any:
        return self._blocks[idx]

    def __setitem__(self, idx: int, data: Any) -> None:
        """Add key to one of the _blocks in collection at the specified index.
        Check if the block exists, and add a number of _blocks if needed"""
        for _ in range((idx + 1) - len(self._blocks)):
            self._blocks.append([])
        self._blocks[idx].append(data)

    def __iter__(self) -> Iterator[Any]:
        for block in self._blocks:
            yield block

    def __len__(self) -> int:
        return len(self._blocks)
