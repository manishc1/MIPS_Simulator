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

        if ((self.clock_cycles > 0) and
            (not self.isHit) and
            (STAGE_FLAG['DBUS'] == AVAILABLE)):
            STAGE_FLAG['IBUS'] = OCCUPIED

        if ((Memory_Stage.bus_access_flag) and
            (not self.isHit)):
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

        if ((exec_functional_unit == 'NO_UNIT') and (not self.check_hazard(exec_functional_unit))):
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
        if ((exec_functional_unit != 'NO_UNIT') and (STAGE_FLAG[exec_functional_unit] == OCCUPIED)):
            self.hazards['Struct'] = True

        self.hazards['RAW'] = False
        for register in self.instruction.srcRegs:
            if (REGISTER_FLAG[register] == OCCUPIED):
                self.hazards['RAW'] = True

        self.hazards['WAW'] = False
        if ((self.instruction.destReg != '') and (REGISTER_FLAG[self.instruction.destReg] == OCCUPIED)):
            self.hazards['WAW'] = True


    def check_hazard(self, exec_functional_unit):
        """
        Check is there is a hazardous situation.
        """
        for register in self.instruction.srcRegs:
            if (REGISTER_FLAG[register] == OCCUPIED):
                return True

        if ((self.instruction.destReg != '') and (REGISTER_FLAG[self.instruction.destReg] == OCCUPIED)):
            return True

        if ((exec_functional_unit != 'NO_UNIT') and (STAGE_FLAG[exec_functional_unit] == OCCUPIED)):
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
            REGISTER['PC'] = self.instruction.imm / WORD_SIZE
            REGISTER['CLEAN'] = True
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


class Execute_Stage(Pipeline_Stage):
    """
    Class for Integer execution stage.
    """

    def __init__(self, instruction):
        """
        Initialize the integer pipeline stage.
        """
        Pipeline_Stage.__init__(self, instruction)
        self.name = 'EX'


    def execute(self, instruction):
        """
        Execute the interger unit stage.
        """
        if (STAGE_FLAG['IU'] == AVAILABLE):
            self.occupy_dest_register()
            self.operate()

        STAGE_FLAG['IU'] = OCCUPIED


    def proceed(self):
        """
        Proceed in the integer unit stage.
        """
        if (STAGE_FLAG['MEM'] == AVAILABLE):
            STAGE_FLAG['IU'] = AVAILABLE
            return Memory_Stage(self.instruction)

        self.hazards['Struct'] = True
        return self


    def occupy_dest_register(self):
        """
        Occupy the destination register.
        """
        if (self.instruction.destReg != ''):
            REGISTER_FLAG[self.instruction.destReg] = OCCUPIED


    def operate(self):
        """
        Perform the integer operation.
        """
        if (self.instruction.name == 'dadd'):
            REGISTERS[self.instruction.destReg] = REGISTERS[self.instruction.srcRegs[0]] + REGISTERS[self.instruction.srcRegs[1]]

        elif (self.instruction.name == 'daddi'):
            REGISTERS[self.instruction.destReg] = REGISTERS[self.instruction.srcRegs[0]] + int(self.instruction.imm)

        elif (self.instruction.name == 'dsub'):
            REGISTERS[self.instruction.destReg] = REGISTERS[self.instruction.srcRegs[0]] - REGISTERS[self.instruction.srcRegs[1]]

        elif (self.instruction.name == 'dsubi'):
            REGISTERS[self.instruction.destReg] = REGISTERS[self.instruction.srcRegs[0]] - int(self.instruction.imm)

        elif (self.instruction.name == 'and'):
            REGISTERS[self.instruction.destReg] = REGISTERS[self.instruction.srcRegs[0]] & REGISTERS[self.instruction.srcRegs[1]]

        elif (self.instruction.name == 'andi'):
            REGISTERS[self.instruction.destReg] = REGISTERS[self.instruction.srcRegs[0]] & int(self.instruction.imm)

        elif (self.instruction.name == 'or'):
            REGISTERS[self.instruction.destReg] = REGISTERS[self.instruction.srcRegs[0]] | REGISTERS[self.instruction.srcRegs[1]]

        elif (self.instruction.name == 'ori'):
            REGISTERS[self.instruction.destReg] = REGISTERS[self.instruction.srcRegs[0]] | int(self.instruction.imm)


class Memory_Stage(Execute_Stage):
    """
    Class for memory stage of pipepline.
    """

    bus_access_flag = False

    def __init__(self, instruction):
        """
        Initialize the pipeline memory stage.
        """
        Execute_Stage.__init__(self, instruction)
        self.wait_for_ibus = False
        self.word_hit = [True, True]
        self.word_cycles = self.calculate_required_memory_cycles()


    def execute(self, instruction):
        """
        Execute the memory stage.
        """
        if (not self.wait_for_ibus):
            if (not self.word_hit[0]):
                Memory_Stage.bus_access_flag = True
                self.wait_for_ibus = True
            if ((not self.word_hit[1]) and (self.word_cycles[0] == 0)):
                Memory_Stage.bus_access_flag = True
                self.wait_for_ibus = True
        else:
            Memory_Stage.bus_access_flag = False

        if ((Memory_Stage.bus_access_flag) and (STAGE_FLAG['IBUS'] == OCCUPIED)):
            if (not self.word_hit[0]):
                self.word_cycles[0] -= 1
            elif (not self.word_hit[1]):
                self.word_cycles[1] -= 1

        if (self.word_cycles[0] == 0):
            if ((not self.word_hit[1]) and (STAGE_FLAG['IBUS'] == AVAILABLE)):
                STAGE_FLAG['DBUS'] = OCCUPIED
            if ((self.word_hit[1]) or (STAGE_FLAG['DBUS'] == OCCUPIED)):
                self.word_cycles[1] -= 1

        STAGE_FLAG['MEM'] = OCCUPIED

        if ((not self.word_hit[0]) and (STAGE_FLAG['IBUS'] == AVAILABLE) and (self.word_cycles[0] > 0)):
            STAGE_FLAG['DBUS'] = OCCUPIED

        if (((self.word_hit[0]) or (STAGE_FLAG['DBUS'] == OCCUPIED)) and (self.word_cycles[0] > 0)):
            self.word_cycles[0] -= 1


    def proceed(self):
        """
        Proceed in the memory stage.
        """
        if ((not self.word_hit[0]) and (self.word_cycles[0] == 0) and (self.word_hit[1])):
            STAGE_FLAG['DBUS'] = AVAILABLE

        if ((not self.word_hit[1]) and (self.word_cycles[1] == 0)):
            STAGE_FLAG['DBUS'] = AVAILABLE

        if (self.word_cycles[1] < 0):
            self.hazards['Struct'] = True

        if (((self.word_cycles[0] + self.word_cycles[1]) <= 0) and (STAGE_FLAG['WB'] == AVAILABLE)):
            STAGE_FLAG['MEM'] = AVAILABLE
            return WriteBack_Stage(self.instruction)

        return self


    def calculate_required_memory_cycles(self):
        """
        Calculate the address and the memory cycles required
        """
        if (self.instruction.name == 'lw'):
            location = int(self.instruction.offset) + REGISTERS[self.instruction.srcRegs[0]]
            self.word_hit[0], REGISTERS[self.instruction.destReg], cycles = Data_Cache.read(location)
            return [cycles, 0]

        elif (self.instruction.name == 'l.d'):
            time_to_read = [0, 0]
            location = int(self.instruction.offset) + REGISTERS[self.instruction.srcRegs[0]]
            self.word_hit[0], word, time_to_read[0] = Data_Cache.read(location)
            self.word_hit[1], word, time_to_read[1] = Data_Cache.read(location + WORD_SIZE)
            return time_to_read

        elif (self.instruction.name == 'sw'):
            location = int(self.instruction.offset) + REGISTERS[self.instruction.srcRegs[1]]
            self.word_hit[0], cycles = Data_Cache.write(location, REGISTERS[self.instruction.srcRegs[0]])
            return [cycles, 0]

        elif (self.instruction.name == 's.d'):
            time_to_write = [0, 0]
            location = int(self.instruction.offset) + REGISTERS[self.instruction.srcRegs[1]]
            self.word_hit[0], time_to_write[0] = Data_Cache.write(location, 0, False)
            self.word_hit[1], time_to_write[1] = Data_Cache.write(location + WORD_SIZE, 0, False)
            return time_to_write

        return [1, 0]


class FP_Adder_Stage(Execute_Stage):
    """
    Class for FP Adder stage.
    """

    def __init__(self, instruction):
        """
        Initialize FP Adder stage.
        """
        Execute_Stage.__init__(self, instruction)
        self.clock_cycles = FP_CONFIG['FP_ADD']['CYCLES']


    def execute(self, instruction):
        """
        Execute the FP Adder stage.
        """
        if (self.clock_cycles == FP_CONFIG['FP_ADD']['CYCLES']):
            self.occupy_dest_register()
            STAGE_FLAG['FP_ADD'] = OCCUPIED

        self.clock_cycles -= 1


    def proceed(self):
        """
        Proceed in the FP Adder stage execution.
        """
        if (self.clock_cycles < 0):
            self.hazards['Struct'] = True

        if FP_CONFIG['FP_ADD']['PIPELINED']:
            STAGE_FLAG['FP_ADD'] = AVAILABLE

        if ((self.clock_cycles <= 0) and (STAGE_FLAG['WB'] == AVAILABLE)):
            STAGE_FLAG['FP_ADD'] = AVAILABLE
            return WriteBack_Stage(self.instruction)

        return self


class FP_Multiplier_Stage(Execute_Stage):
    """
    Class for FP Multiplier stage.
    """

    def __init__(self, instruction):
        """
        Initialize FP Multiplier stage.
        """
        Execute_Stage.__init__(self, instruction)
        self.clock_cycles = FP_CONFIG['FP_MUL']['CYCLES']


    def execute(self, instruction):
        """
        Execute FP Multiplier stage.
        """
        if (self.clock_cycles == FP_CONFIG['FP_MUL']['CYCLES']):
            self.occupy_dest_register()
            STAGE_FLAG['FP_MUL'] = OCCUPIED

        self.clock_cycles -= 1


    def proceed(self):
        """
        Proceed in the FP Multiplier stage execution.
        """
        if (self.clock_cycles < 0):
            self.hazards['Struct'] = True

        if (FP_CONFIG['FP_MUL']['PIPELINED']):
            STAGE_FLAG['FP_MUL'] = AVAILABLE

        if ((self.clock_cycles <= 0) and (STAGE_FLAG['WB'] == AVAILABLE)):
            STAGE_FLAG['FP_MUL'] = AVAILABLE
            return WriteBack_Stage(self.instruction)

        return self


class FP_Divider_Stage(Execute_Stage):
    """
    Class for FP Divider stage.
    """

    def __init__(self, instruction):
        """
        Initialize FP Divider stage.
        """
        ExecuteStage.__init__(self, instruction)
        self.clock_cycles = FP_CONFIG['FP_DIV']['CYCLES']


    def execute(self, instruction):
        """
        Execute FP Divider stage.
        """
        if (self.clock_cycles == FP_CONFIG['FP_DIV']['CYCLES']):
            self.occupy_dest_register()
            STAGE_FLAG['FP_DIV'] = OCCUPIED

        self.clock_cycles -= 1


    def proceed(self):
        """
        Proceed in FP Divider stage execution.
        """
        if (self.clock_cycles < 0):
            self.hazards['Struct'] = True

        if (FP_CONFIG['FP_DIV']['PIPELINED']):
            STAGE_FLAG['FP_DIV'] = AVAILABLE

        if ((self.clock_cycles <= 0) and (STAGE_FLAG['WB'] == AVAILABLE)):
            STAGE_FLAG['FP_DIV'] = AVAILABLE
            return WriteBack_Stage(self.instruction)

        return self


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
