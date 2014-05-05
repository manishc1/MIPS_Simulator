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


    def toString(self, isLast):
        """
        Convert to string representation.
        """
        string = ''
        for label, location in LABEL.items():
            if (self.instruction.location == location):
                string += label + ': '
        string += str(self.instruction)
        string = string.ljust(INSTRUCTION_LEFT_JUSTIFY)

        for stage in STAGES:
            if (self.cycles[stage] != 0):
                string += '\t' + str(self.cycles[stage]) + '\t'
            else:
                string += '\t\t'

        if (isLast):
            return string

        for hazard in HAZARDS:
            if (self.hazards[hazard]):
                string += '\tY\t'
            else:
                string += '\tN\t'

        return string
