from computer import *
from instruction_cache import *
from data_cache import *
from pipeline_stage import *
from pipeline_decode_stage import *


class Fetch_Stage(Pipeline_Stage):
    """
    Class for instruction fetch stage.
    """
    
    def __init__(self, instruction):
        """
        Initialize the instruction fetch stage.
        """
        Pipeline_Stage.__init__(self, instruction)
        self.name = 'IF'
        self.isHit, self.clock_cycles = Instruction_Cache.read(self.instruction.location)


    def execute(self, instruction):
        """
        Execute the instruction fetch stage.
        """
        STAGE_FLAG[self.name] = OCCUPIED

        if (not self.isHit):
            if ((self.clock_cycles > 0) and
                (STAGE_FLAG['DBUS'] == AVAILABLE)):
                STAGE_FLAG['IBUS'] = OCCUPIED

            if (Memory_Stage.bus_access_flag):
                STAGE_FLAG['IBUS'] = OCCUPIED
                STAGE_FLAG['DBUS'] = AVAILABLE
                Memory_Stage.bus_access_flag = False

        if ((STAGE_FLAG['IBUS'] == OCCUPIED) or
            (self.isHit)):
            self.clock_cycles -= 1


    def proceed(self):
        """
        Proceed in the instruction fetch stage.
        """
        if (self.clock_cycles == 0):
            STAGE_FLAG['IBUS'] = AVAILABLE
            
        if (self.clock_cycles <= 0):
            if (REGISTERS['CLEAN']):
                STAGE_FLAG[self.name] = AVAILABLE
                STAGE_FLAG['IBUS'] = AVAILABLE
                REGISTERS['CLEAN'] = False
                return None
            if (STAGE_FLAG['ID'] == AVAILABLE):
                STAGE_FLAG[self.name] = AVAILABLE
                return Decode_Stage(self.instruction)

        return self
