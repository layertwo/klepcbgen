from typing import Any, List


class KeyBlockCollection:
    """Maintains a collection of blocks of keyboard keys, such as columns or rows"""

    def __init__(self) -> None:
        self.blocks = []  # type: List[Any]

    def add_key_to_block(self, block_index: int, key_index: int) -> None:
        """Add a keyboard key to one of the blocks in the collection at the specified index.
        If the block does not exist, it gets created at the specified index, inserting a
        number of empty blocks if necessary"""
        # Check if the block exists, and add a number of blocks if needed
        blocks_to_add = (block_index + 1) - len(self.blocks)
        if blocks_to_add > 0:
            for _ in range(blocks_to_add):
                self.blocks.append([])
        self.blocks[block_index].append(key_index)

    def get_block(self, block_index: int) -> Any:
        """Get the coimplete"""
        return self.blocks[block_index]
