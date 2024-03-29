"""
Wrapper that wraps the instruction for passing between the stages in the pipeline.
"""

from computer import *
from output import *

import pipeline_fetch_stage


class Instruction_Container():
    """
    Container for the instruction and its state.
    """

    def __init__(self, instruction, clock_cycle):
        """
        Initialize the container.
        """
        self.current_pipeline_stage = pipeline_fetch_stage.Fetch_Stage(instruction)
        self.instruction = instruction
        self.current_pipeline_stage.execute(self.instruction)
        self.output = Output(instruction, clock_cycle)


    def __str__(self):
        """
        Represent the instruction container as string.
        """
        return "\nInstruction:%s\nOutput:%s" % (self.instruction, self.output)


    def keep_executing(self):
        """
        Continue the execution in the same stage or enter the next stage.        
        """
        prev_pipeline_stage = self.current_pipeline_stage
        self.current_pipeline_stage = prev_pipeline_stage.proceed()

        if (self.current_pipeline_stage != prev_pipeline_stage):
            for hazard in HAZARDS:
                self.output.hazards[hazard] |= prev_pipeline_stage.hazards[hazard]

        if (self.current_pipeline_stage == None):
            return False

        self.increment_cycles(prev_pipeline_stage)
        self.current_pipeline_stage.execute(self.instruction)
        return True


    def increment_cycles(self, prev_pipeline_stage):
        """
        Increment the pipeline stage cycles of the instruction.
        """
        for i in range(len(STAGES)-1):
            if ((prev_pipeline_stage.name == STAGES[i]) and
                (self.current_pipeline_stage.name == STAGES[i])):
                self.output.cycles[STAGES[i]] += 1
            elif ((prev_pipeline_stage.name == STAGES[i]) and
                  (self.current_pipeline_stage.name == STAGES[i+1])):
                self.output.cycles[STAGES[i+1]] = self.output.cycles[STAGES[i]] + 1
