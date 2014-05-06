"""
Class that provides functionality to scan the files.
"""

from computer import *
from instruction import *
from utils import *

class Scanner():
    """
    Class for scanning the files
    """

    @classmethod
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
            elif (instr.get_instruction_type() == 'BRANCH'):
                raise Exception('Label expected!')
            

    @classmethod
    def scan_data(self, fileName):
        """
        Method to scan the data from the file.
        """
        lines = readLines(fileName)
        
        data_count = 0
        for line in lines:
            try:
                DATA[DATA_MEMORY_BASE_ADDRESS + data_count*WORD_SIZE] = int(line, 2)
            except:
                raise Exception('Invalid data value, check data file!')
            data_count += 1


    @classmethod
    def scan_registers(self, fileName):
        """
        Method to scan the registers from the file.
        """
        lines = readLines(fileName)

        register_count = 0
        for line in lines:
            try:
                REGISTERS['r'+str(register_count)] = int(line, 2)
            except:
                raise Exception('Invalid register value, check register file!')
            REGISTER_FLAG['r'+str(register_count)] = AVAILABLE
            REGISTER_FLAG['f'+str(register_count)] = AVAILABLE
            register_count += 1


    @classmethod
    def fill_FP_configuration(self, FP_UNIT, configs):
        """
        Populate the FU_CONFIG.
        """
        configs = [conf.strip() for conf in configs.split(',')]
        if ((len(configs) !=2) or (int(configs[0]) < 1) or (configs[1] not in ['yes', 'no'])):
            raise Exception('Invald config for ' + FP_UNIT + '!')
        isPipelined = True
        if (configs[1] == 'no'):
            isPipelined = False
        FP_CONFIG[FP_UNIT] = {'CYCLES': int(configs[0]), 'PIPELINED': isPipelined}


    @classmethod
    def scan_configuration(self, fileName):
        """
        Method to scan the configuration from the file.
        """
        lines = readLines(fileName)

        try:
            for line in lines:
                line = line.lower().strip()
                config_line = line.split(':')
                if ('fp' in config_line[0]):
                    if ('adder' in config_line[0]):
                        self.fill_FP_configuration('FP_ADD', config_line[1])
                    elif ('multiplier' in config_line[0]):
                        self.fill_FP_configuration('FP_MUL', config_line[1])
                    elif ('divider' in config_line[0]):
                        self.fill_FP_configuration('FP_DIV', config_line[1])
                    else:
                        raise Exception('Invalid FP Unit in config!')
                else:
                    if (int(config_line[1].strip()) < 1):
                        raise Exception('Invalid access time!')
                    if ('main' in config_line[0] and 'memory' in config_line[0]):
                        ACCESS_TIME['MEMORY'] = int(config_line[1].strip())
                    elif ('i-cache' in config_line[0]):
                        ACCESS_TIME['ICACHE'] = int(config_line[1].strip())
                    elif ('d-cache' in config_line[0]):
                        ACCESS_TIME['DCACHE'] = int(config_line[1].strip())
                    else:
                        raise Exception('Invalid Unit in config!')
        except:
            raise Exception('Invalid config file!')
