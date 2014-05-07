from computer import *
from instruction_cache import *
from data_cache import *
from pipeline_stage import *
from pipeline_execute_stage import *


class Decode_Stage(Pipeline_Stage):
    """
    Class for instruction decode stage.
    """

    def __init__(self, instruction):
        """
        Initialize the instruction decode stage.
        """
        Pipeline_Stage.__init__(self, instruction)
        self.name = 'ID'


    def execute(self, instruction):
        """
        Execute the instruction decode stage.
        """
        STAGE_FLAG[self.name] = OCCUPIED


    def proceed(self):
        """
        Proceed in the instruction decode stage.
        """
        exec_functional_unit = self.instruction.determine_exec_functional_unit()
        self.discover_hazards(exec_functional_unit)

        if ((exec_functional_unit == 'NO_UNIT') and
            (not self.check_hazard(exec_functional_unit))):
            self.perform_branch_instruction()
            STAGE_FLAG[self.name] = AVAILABLE
            return None

        if (not self.check_hazard(exec_functional_unit)):
            STAGE_FLAG[self.name] = AVAILABLE
            return self.select_execution_stage(exec_functional_unit)

        return self


    def discover_hazards(self, exec_functional_unit):
        """
        Discover the hazards in the instruction decode stage.
        """
        if (not self.check_hazard(exec_functional_unit)):
            return

        self.hazards['Struct'] = False
        if ((exec_functional_unit != 'NO_UNIT') and
            (STAGE_FLAG[exec_functional_unit] == OCCUPIED)):
            self.hazards['Struct'] = True

        self.hazards['RAW'] = False
        for register in self.instruction.srcRegs:
            if (REGISTER_FLAG[register] == OCCUPIED):
                self.hazards['RAW'] = True

        self.hazards['WAW'] = False
        if ((self.instruction.destReg != '') and
            (REGISTER_FLAG[self.instruction.destReg] == OCCUPIED)):
            self.hazards['WAW'] = True


    def check_hazard(self, exec_functional_unit):
        """
        Check is there is a hazardous situation.
        """
        for register in self.instruction.srcRegs:
            if (REGISTER_FLAG[register] == OCCUPIED):
                return True

        if ((self.instruction.destReg != '') and
            (REGISTER_FLAG[self.instruction.destReg] == OCCUPIED)):
            return True

        if ((exec_functional_unit != 'NO_UNIT') and
            (STAGE_FLAG[exec_functional_unit] == OCCUPIED)):
            return True

        return False


    def perform_branch_instruction(self):
        """
        Update the program counter from the branch instruction.
        """
        if (self.instruction.name == 'j'):
            REGISTERS['PC'] = self.instruction.imm / WORD_SIZE
            REGISTERS['CLEAN'] = True
            return

        if ((self.instruction.name == 'beq') and
            (REGISTERS[self.instruction.srcRegs[0]] == REGISTERS[self.instruction.srcRegs[1]])):
            REGISTERS['PC'] = self.instruction.imm / WORD_SIZE
            REGISTERS['CLEAN'] = True
            return    

        if ((self.instruction.name == 'bne') and
            (REGISTERS[self.instruction.srcRegs[0]] != REGISTERS[self.instruction.srcRegs[1]])):
            REGISTERS['PC'] = self.instruction.imm / WORD_SIZE
            REGISTERS['CLEAN'] = True


    def select_execution_stage(self, exec_functional_unit):
        """
        Select the instruction execution stage.
        """
        if (exec_functional_unit == 'FP_ADD'):
            return FP_Adder_Stage(self.instruction)

        elif (exec_functional_unit == 'FP_MUL'):
            return FP_Multiplier_Stage(self.instruction)

        elif (exec_functional_unit == 'FP_DIV'):
            return FP_Divider_Stage(self.instruction)

        else:
            return Execute_Stage(self.instruction)


