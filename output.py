"""
Stores the result of the instruction.
"""

from computer import *


class Output():
    """
    Class to present the resulting output.
    """

    def __init__(self, instruction, cycle = 0):
        """
        Initialize the output.
        """
        self.instruction = instruction
        self.cycles = {'IF': cycle, 'ID': 0, 'EX': 0, 'WB': 0}
        self.hazards = {'RAW': False, 'WAR': False, 'WAW': False, 'Struct': False}


    def __str__(self):
        """
        Convert to string representation.
        """
        string = str(self.instruction) + '\t'

        for stage in STAGES:
            if (self.cycles[stage] != 0):
                string += str(self.cycles[stage]) + '\t'
            else:
                string += '\t'

        for hazard in HAZARDS:
            if (self.hazards[hazard]):
                string += 'Y\t'
            else:
                string += 'N\t'

        return string
