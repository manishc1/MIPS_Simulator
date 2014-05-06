"""
Class that provides functionality to print to the files.
"""

from computer import *
from data_cache import *
from instruction_cache import *
from utils import *

class Printer():
    """
    Class for printing to the file.
    """

    @classmethod
    def print_output(self, fileName, output):
        """
        Print the final output.
        """
        result = sorted(output, key=lambda o: o.cycles[STAGES[0]])
        result[len(result) - 1].cycles[STAGES[1]] = 0

        string = 'instruction'.ljust(INSTRUCTION_LEFT_JUSTIFY)
        for stage in STAGES:
            string += '\t' + stage + '\t'
        for hazard in HAZARDS:
            string += '\t' + hazard + '\t'
        string += '\n'

        for i in range(len(result)):
            string += str(result[i]) + '\n'

        string += '\nTotal number of requests to instruction cache  ' + str(Instruction_Cache.requests)
        string += '\nTotal number of instruction cache hit  ' + str(Instruction_Cache.hits)
        string += '\nTotal number of requests to data cache  ' + str(Data_Cache.requests)
        string += '\nTotal number of data cache hit  ' + str(Data_Cache.hits)

        writeString(fileName, string)
        #print string
