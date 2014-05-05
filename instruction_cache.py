"""
Details of the instruction cache.
"""

from computer import *
from memory_cache_block import *


class Instruction_Cache():
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
            Instruction_Cache.cache_block.append(Cache_Block(id, CACHE_BLOCK_SIZE))


    def read(self, location):
        """
        Read instruction at location.
        """
        Instruction_Cache.requests += 1
        tag = location >> 6
        block_id = (location >> NUMBER_OF_CACHE_BLOCKS) % CACHE_BLOCK_SIZE

        if ((Instruction_Cache.cache_block[block_id].valid_bit == True) and
            (Instruction_Cache.cache_block[block_id].tag == tag)):
            Instruction_Cache.hits += 1
            return HIT, ACCESS_TIME['ICACHE']
        else:
            Instruction_Cache.cache_block[block_id].tag = tag
            Instruction_Cache.cache_block[block_id].valid_bit = True
            return MISS, 2 * (ACCESS_TIME['MEMORY'] + ACCESS_TIME['ICACHE'])
