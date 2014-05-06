"""
Cache Block and its state.
"""

class Cache_Block():
    """
    Class for the cache block.
    """

    def __init__(self, id, size):
        """
        Initilize the cache block
        """
        self.id = id
        self.size = size
        self.words = [0] * size
        self.valid_bit = False
        self.dirty_bit = False
