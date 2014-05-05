from computer import *
from instruction import *
from utils import *

class Scanner():
    """
    Class for scanning the files
    """

    def scan_instructions(self, fileName):
        """
        Method to scan the instructions from file.
        """
        lines = readLines(fileName)

        for line in lines:
            line = line.lower().strip()
            instr = line.split(':')
            if (len(instr) == 1):
                # No label present
                instr = instr[0].strip().split(' ')
            elif (len(instr) == 2):
                # 1 label present                
                LABEL[instr[0].strip()] = Instruction.counter * WORD_SIZE
                instr = instr[1].strip().split(' ')
            else:
                raise Exception('Invalid number of labels!')

            # INSTRUCTIONS += Instruction(instr_name, operands)
            INSTRUCTIONS.append(Instruction(instr[0], filter(None, ''.join(instr[1:]).split(','))))

        for instr in INSTRUCTIONS:
            if (instr.imm in LABEL.keys()):
                instr.update_imm(LABEL[instr.imm])
            elif (instr.getType() == 'BRANCH'):
                raise Exception('Label expected!')
