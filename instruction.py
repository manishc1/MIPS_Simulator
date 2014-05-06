"""
Representation details of an instructions.
"""

from computer import *

import re


class Instruction():
    """
    Class to represent an Instruction.
    """

    counter = 0

    def __init__(self, name, operands):        
        """
        Initialize the Instruction.
        """
        self.name = name
        self.operands = operands
        self.extract_registers()
        self.location = Instruction.counter * WORD_SIZE        
        Instruction.counter += 1


    def __str__(self):
        """
        Convert to string representation.
        """
        return self.name  + ' ' + ','.join(self.operands)

        
    def get_instruction_type(self):
        """
        Return the type of the instruction.
        """
        if (self.name in ALU_INSTRUCTIONS):
            return 'ALU'
        elif (self.name in BRANCH_INSTRUCTIONS):
            return 'BRANCH'
        elif (self.name in DATA_INSTRUCTIONS):
            return 'DATA'
        elif (self.name in MISC_INSTRUCTIONS):
            return 'MISC'
        else:
            raise Exception('')


    def split_operands(self):
        """
        Split operands into registers and immediates.
        """
        operands = []
        if (len(self.operands) > 1) and ('(' in self.operands[1]):
            operands.append(self.operands[0])
            operands.append(self.operands[1].split('(')[0])
            operands.append(self.operands[1].split('(')[1].split(')')[0])
        else:
            operands = self.operands
        return operands


    def extract_registers(self):
        """
        Extract destination and source registers.
        """
        operands = self.split_operands()

        self.destReg = ''
        self.srcRegs = []
        self.imm = ''
        self.offset = ''

        if (self.name in MISC_INSTRUCTIONS):
            # Instructions with no operands.
            return

        if (((self.name in UNCONDITIONAL_BRANCH_INSTRUCTIONS) and
             (len(operands) > 1)) or
            ((self.name not in UNCONDITIONAL_BRANCH_INSTRUCTIONS) and
             (len(operands) > 3))):
            raise Exception(': more than expected offsets or registers mentioned')

        if (self.name in DESTFUL_INSTRUCTIONS):
            # Instructions that have destination.
            if (len(operands) > 0):
                self.destReg = operands[0]
            else:
                raise Exception(': missing destination register')

        if (self.name in LOAD_INSTRUCTIONS):
            if (len(operands) == 3):
                self.offset = operands[1]
                self.srcRegs = [operands[2]]
            else:
                raise Exception(': missing offset or source register')
        elif (self.name in STORE_INSTRUCTIONS):
            if (len(operands) == 3):
                self.offset = operands[1]
                self.srcRegs = [operands[0], operands[2]]
            else:
                raise Exception(': missing offset or source register')
        elif (self.name in IMMEDIATE_ALU_INSTRUCTIONS):
            if (len(operands) == 3):
                self.srcRegs = [operands[1]]
                self.imm = operands[2]
            else:
                raise Exception(': missing offset or source register')
        elif (self.name in CONDITIONAL_BRANCH_INSTRUCTIONS):
            if (len(operands) == 3):
                self.srcRegs = operands[:2]
                self.imm = operands[2]
            else:
                raise Exception(': missing immediate or source register')
        elif (self.name in UNCONDITIONAL_BRANCH_INSTRUCTIONS):
            if (len(operands) == 1):
                self.imm = operands[0]
            else:
                raise Exception(': missing immediate')
        elif (self.name in INTEGER_ALU_INSTRUCTIONS + FLOAT_ALU_INSTRUCTIONS):
            if (len(operands) == 3):
                self.srcRegs = operands[1:]
            else:
                raise Exception(': missing source register')
        else:
            raise Exception(': invalid instruction name <' + self.name + '>')

        register_pattern = "^[rf]\d+$"
        constant_pattern = "^\d+$"

        if (self.name in DESTFUL_INSTRUCTIONS):
            if (re.match(register_pattern, self.destReg) == None):
                raise Exception(': invalid destination register <' + self.destReg + '>')

        if (self.name in LOAD_INSTRUCTIONS + STORE_INSTRUCTIONS):
            if (re.match(constant_pattern, self.offset) == None):
                raise Exception(': invalid offset <' + self.offset + '>')

        if (self.name in IMMEDIATE_ALU_INSTRUCTIONS + BRANCH_INSTRUCTIONS):
            if (self.imm == ''):
                raise Exception(': missing label')

        for srcReg in self.srcRegs:
            if (re.match(register_pattern, srcReg) == None):
                raise Exception(': invalid source register <' + srcReg + '>')

            
    def update_imm(self, location):
        """
        Update the immediate value.
        """
        self.imm = location


    def determine_exec_functional_unit(self):
        """
        Determine the functional unit to be used in execution stage.
        """
        if (self.name in BRANCH_INSTRUCTIONS + MISC_INSTRUCTIONS):
            return 'NO_UNIT'
        elif (self.name in ['add.d', 'sub.d']):
            return 'FP_ADD'
        elif (self.name in ['mul.d']):
            return 'FP_MUL'
        elif (self.name in ['div.d']):
            return 'FP_DIV'
        else:
            return 'IU'
