"""
Cache Block and its state.
"""

class CacheBlock():
    """
    Class for the cache block.
    """

    def __init__(self, id, size):
        """
        Initilize the cache block
        """
        self.id = id
        self.size = size
        self.words = [0] * CACHE_BLOCK_SIZE
        self.valid_bit = False
        self.dirty_bit = False


    def copy(self, words):
        self.words = words
