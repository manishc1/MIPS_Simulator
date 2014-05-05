"""
Defines the world of the MIPS computer that is being simulating.
"""

from config import *


# Some macro definitions
AVAILABLE = False
OCCUPIED = True

HIT = True
MISS = False

MAX = 100



# ALU Instructions
INTEGER_ALU_INSTRUCTIONS = ['dadd', 'dsub', 'and', 'or']
FLOAT_ALU_INSTRUCTIONS = ['add.d', 'sub.d', 'mul.d', 'div.d']
IMMEDIATE_ALU_INSTRUCTIONS = ['daddi', 'dsubi', 'andi', 'ori']
ALU_INSTRUCTIONS = INTEGER_ALU_INSTRUCTIONS + FLOAT_ALU_INSTRUCTIONS + IMMEDIATE_ALU_INSTRUCTIONS

# Data Instructions
LOAD_INSTRUCTIONS = ['lw', 'l.d']
STORE_INSTRUCTIONS = ['sw', 's.d']
DATA_INSTRUCTIONS = LOAD_INSTRUCTIONS + STORE_INSTRUCTIONS

# Branch Instructions
CONDITIONAL_BRANCH_INSTRUCTIONS = ['beq', 'bne']
UNCONDITIONAL_BRANCH_INSTRUCTIONS = ['j']
BRANCH_INSTRUCTIONS = CONDITIONAL_BRANCH_INSTRUCTIONS + UNCONDITIONAL_BRANCH_INSTRUCTIONS

# Miscelleneous Instructions
MISC_INSTRUCTIONS = ['hlt']

# Insrtuctions with destination.
DESTFUL_INSTRUCTIONS = LOAD_INSTRUCTIONS + ALU_INSTRUCTIONS



# Hazards
HAZARDS = ['RAW', 'WAR', 'WAW', 'Struct']



# Stages
STAGES = ['ID', 'IF', 'EX', 'WB']



# Floating Point functional units
FP_UNITS = ['FP_ADD', 'FP_MUL', 'FP_DIV']



# Some computer constants
DATA_MEMORY_BASE_ADDRESS = 256
WORD_SIZE = 4



# Cache constants
CACHE_BLOCK_SIZE = 4
NUMBER_OF_CACHE_BLOCKS = 4
NUMBER_OF_CACHE_SETS = 2



# State of the computer and program
DATA = {}
INSTRUCTIONS = []
LABEL = {}
REGISTERS = {'PC': 0, 'FLUSH': False}
REGISTER_FLAG = {}
STAGE_FLAG = {
    'IF': AVAILABLE,
    'ID': AVAILABLE,
    'IU': AVAILABLE,
    'MEM': AVAILABLE,
    'FP_ADD': AVAILABLE,
    'FP_MUL': AVAILABLE,
    'FP_DIV': AVAILABLE,
    'WB': AVAILABLE,
    'IBUS': AVAILABLE,
    'DBUS': AVAILABLE
    }
