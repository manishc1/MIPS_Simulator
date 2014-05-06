"""
Details of the data cache.
"""

from computer import *
from memory_cache_block import *
from memory_cache_set import *


class Data_Cache():
    """
    Class for data cache.
    """

    cache_sets = []
    cache_block_lru = [0, 0]
    requests = 0
    hits = 0


    def __init__(self):
        """
        Initialize data cache.
        """
        for id in range(NUMBER_OF_CACHE_SETS):
            Data_Cache.cache_sets.append(Cache_Set(id, NUMBER_OF_CACHE_BLOCKS / NUMBER_OF_CACHE_SETS))


    @classmethod
    def read(self, location):
        """
        Read from the location.
        """
        Data_Cache.requests += 1
        location -= DATA_MEMORY_BASE_ADDRESS
        block_id = (location >> NUMBER_OF_CACHE_BLOCKS) % NUMBER_OF_CACHE_SETS
        read_cycles = 0

        for id in range(NUMBER_OF_CACHE_SETS):
            if Data_Cache.lookup_address_in_set(location, id):
                Data_Cache.hits += 1
                Data_Cache.use_for_lru(block_id, id)
                return HIT, Data_Cache.cache_sets[id].cache_block[block_id].words[(location & 12) >> NUMBER_OF_CACHE_SETS], ACCESS_TIME['DCACHE']

        set_id = Data_Cache.cache_block_lru[block_id]

        if Data_Cache.cache_sets[set_id].cache_block[block_id].dirty_bit:
            read_cycles += Data_Cache.memory_write_back(set_id, block_id)

        Data_Cache.prepare_block(location, set_id)
        read_cycles += 2* (ACCESS_TIME['MEMORY'] + ACCESS_TIME['DCACHE'])
        return MISS, Data_Cache.cache_sets[set_id].cache_block[block_id].words[(location & 12) >> NUMBER_OF_CACHE_SETS], read_cycles


    @classmethod
    def write(self, location, data, isWritable = True):
        """
        Write to the data cache.
        """
        Data_Cache.requests += 1
        location -= DATA_MEMORY_BASE_ADDRESS
        block_id = (location >> NUMBER_OF_CACHE_BLOCKS) % NUMBER_OF_CACHE_SETS
        write_cycles = 0

        for id in range(NUMBER_OF_CACHE_SETS):
            if Data_Cache.lookup_address_in_set(location, id):
                Data_Cache.hits += 1
                Data_Cache.use_for_lru(block_id, id)
                Data_Cache.write_data(location, id, data, isWritable)
                return HIT, ACCESS_TIME['DCACHE']

        set_id = Data_Cache.cache_block_lru[block_id]

        if Data_Cache.cache_sets[set_id].cache_block[block_id].dirty_bit:
            write_cycles += Data_Cache.memory_write_back(set_id, block_id)

        Data_Cache.prepare_block(location, set_id)
        Data_Cache.write_data(location, set_id, data, isWritable)
        return MISS, write_cycles + 2 * (ACCESS_TIME['MEMORY'] + ACCESS_TIME['DCACHE'])


    @classmethod
    def lookup_address_in_set(self, location, id):
        """
        Check if the address is present in the set
        """
        tag = location >> 5
        block_id = (location >> NUMBER_OF_CACHE_BLOCKS) % NUMBER_OF_CACHE_SETS

        if ((Data_Cache.cache_sets[id].check_block_for_validity(block_id)) and
            (Data_Cache.cache_sets[id].get_block_tag(block_id) == tag)):
            return True

        return False


    @classmethod
    def use_for_lru(self, block_id, set_id):
        """
        Update the LRU for the set.
        """
        if (set_id == 0):
            Data_Cache.cache_block_lru[block_id] = 1
        else:
            Data_Cache.cache_block_lru[block_id] = 0


    @classmethod
    def memory_write_back(self, set_id, block_id):
        """
        Write Back from cache to memory.
        """
        tag = Data_Cache.cache_sets[set_id].cache_block[block_id].tag
        base_address = DATA_MEMORY_BASE_ADDRESS + ((tag << 5) | (block_id << NUMBER_OF_CACHE_BLOCKS))
        for id in range(CACHE_BLOCK_SIZE):
            DATA[base_address + (id * WORD_SIZE)] = Data_Cache.cache_sets[set_id].cache_block[block_id].words[i]
        return 2 * (ACCESS_TIME['MEMORY'] + ACCESS_TIME['DCACHE'])


    @classmethod
    def prepare_block(self, location, set_id):
        """
        Prepare the block
        """
        block_id = (location >> NUMBER_OF_CACHE_BLOCKS) % NUMBER_OF_CACHE_SETS
        Data_Cache.cache_sets[set_id].cache_block[block_id].tag = location >> 5
        Data_Cache.cache_sets[set_id].cache_block[block_id].valid_bit = True
        Data_Cache.use_for_lru(block_id, set_id)

        base_address = DATA_MEMORY_BASE_ADDRESS + ((location >> 4) << 4)
        for id in range(CACHE_BLOCK_SIZE):
            Data_Cache.cache_sets[set_id].cache_block[block_id].words[id] = DATA[base_address + (id * WORD_SIZE)]


    @classmethod
    def write_data(self, location, set_id, data, isWritable):
        block_id = (location >> NUMBER_OF_CACHE_BLOCKS) % NUMBER_OF_CACHE_SETS
        Data_Cache.cache_sets[set_id].cache_block[block_id].dirty_bit = True
        if isWritable:
            Data_Cache.cache_sets[set_id].cache_block[block_id].words[(location & 12) >> NUMBER_OF_CACHE_SETS] = data
