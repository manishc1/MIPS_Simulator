from computer import *
from instruction_cache import *
from data_cache import *
from pipeline_stage import *


class WriteBack_Stage(Pipeline_Stage):
    """
    Class for WriteBack stage.
    """

    def __init__(self, instruction):
        """
        Initialize WriteBack stage.
        """
        Pipeline_Stage.__init__(self, instruction)
        self.name = 'WB'


    def execute(self, instruction):
        """
        Execute WriteBack stage.
        """
        STAGE_FLAG['WB'] = OCCUPIED


    def proceed(self):
        STAGE_FLAG['WB'] = AVAILABLE
        self.release_dest_register()
        return None


    def release_dest_register(self):
        if (self.instruction.destReg != ''):
            REGISTER_FLAG[self.instruction.destReg] = AVAILABLE
