"""
Execution details for all the pipeline stages.
"""

from computer import *
from instruction_cache import *
from data_cache import *


class Pipeline_Stage():
    """
    Parent class for the pipeline stages.
    """

    def __init__(self, instruction):
        """
        Initialize the pipeline stage.
        """
        self.instruction = instruction
        self.hazards = {}
        for hazard in HAZARDS:
            self.hazards[hazard] = False


