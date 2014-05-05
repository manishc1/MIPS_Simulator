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
            

    def scan_data(self, fileName):
        """
        Method to scan the data from the file.
        """
        lines = readLines(fileName)
        
        data_count = 0
        for line in lines:
            DATA[DATA_MEMORY_BASE_ADDRESS + data_count*WORD_SIZE] = int(line, 2)
            data_count += 1


    def scan_registers(self, fileName):
        """
        Method to scan the registers from the file.
        """
        lines = readLines(fileName)

        register_count = 0
        for line in lines:
            REGISTERS['r'+str(register_count)] = int(line, 2)
            REGISTER_FLAG['r'+str(register_count)] = AVAILABLE
            REGISTER_FLAG['f'+str(register_count)] = AVAILABLE
            register_count += 1
