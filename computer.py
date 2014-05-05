"""
Defines the world of the computer hat is simulating.
"""

from config import *

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



# Some computer constants
WORD_SIZE = 4
DATA_MEMORY_BASE_ADDRESS = 100



# Cache constants
CACHE_BLOCK_SIZE = 4



# State of the computer and program
DATA = {}
INSTRUCTIONS = []
LABEL = {}
REGISTERS = {'PC': 0, 'FLUSH': False}
REGISTER_FLAG = {}



# Some macro definitions
AVAILABLE = False
BUSY = True
