"""
Details of the instruction cache.
"""

from memory_cache_block import *
from computer import *


class InstructionCache():
    """
    Class for the instruction cache.
    """

    cache_block = []
    requests = 0
    hits = 0

    def __init__(self):
        """
        Initialize the instruction cache.
        """
        for id in range(NUMBER_OF_CACHE_BLOCKS):
            InstructionCache.cache_block.append(Cache_Block(id, CACHE_BLOCK_SIZE))


    def read(self, location):
        """
        Read instruction at location.
        """
        InstructionCache.requests += 1
        tag = location >> 6
        block_id = (location >> NUMBER_OF_CACHE_BLOCKS) % CACHE_BLOCK_SIZE

        if ((InstructionCache.cache_block[block_id].valid_bit == True) and
            (InstructionCache.cache_block[block_id].tag == tag)):
            InstructionCache.hits += 1
            return HIT, ACCESS_TIME['ICACHE']
        else:
            InstructionCache.cache_block[block_id].tag = tag
            InstructionCache.cache_block[block_id].valid_bit = True
            return MISS, 2 * (ACCESS_TIME['MEMORY'] + ACCESS_TIME['ICACHE'])
