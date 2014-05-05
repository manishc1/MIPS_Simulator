from computer import *

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
        return self.name  + ' ' + ', '.join(self.operands)
        
    def getType(self):
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
            raise Exception('Unknown instruction encountered')

    def split_operands(self):
        """
        Split operands into registers and immediates.
        """
        operands = []
        if (len(self.operands) > 1) and ('(' in self.operands[1]):
            operands.append(self.operands[0])
            operands.append(self.operands[1].split('(')[0])
            operands.append(self.operands[1].split('(')[0].split(')')[0])
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

        if (self.name in DESTFUL_INSTRUCTIONS):
            # Instructions that have destination.
            self.destReg = operands[0]

        if (self.name in LOAD_INSTRUCTIONS):
            self.offset = operands[1]
            self.src_reg = [operands[2]]
        elif (self.name in STORE_INSTRUCTIONS):
            self.offset = operands[1]
            self.srcRegs = [operands[0], operands[2]]
        elif (self.name in IMMEDIATE_ALU_INSTRUCTIONS):
            self.srcRegs = [operands[1]]
            self.imm = operands[2]
        elif (self.name in CONDITIONAL_BRANCH_INSTRUCTIONS):
            self.srcRegs = operands[:2]
            self.imm = operands[2]
        elif self.name in UNCONDITIONAL_BRANCH_INSTRUCTIONS:
            self.imm = operands[0]
        else:
            self.srcRegs = operands[1:]

    def update_imm(self, address):
        """
        Update the immediate value.
        """
        self.imm = address
