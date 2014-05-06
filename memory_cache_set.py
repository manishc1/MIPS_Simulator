"""
Sets of blocks in cache.
"""

from memory_cache_block import *
from computer import *


class Cache_Set:
    """
    Class for the cache set.
    """

    def __init__(self, id, size):
        """
        Initialize cache set.
        """
        self.id = 0
        self.size = size
        self.cache_block = []
        for i in range(self.size):
            self.cache_block.append(Cache_Block(i, CACHE_BLOCK_SIZE))
