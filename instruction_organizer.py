"""
Organizes the Active Instruction Container Queue.
"""

from collections import deque
from computer import *
from instruction_container import *

import operator


class Instruction_Organizer():
    """
    Class to organize the instruction container queue.
    """


    @classmethod
    def organize(self, old_instruction_containers):
        """
        Organize instructions in WB - EX - ID - IF manner.
        """
        new_instruction_containers = deque([])

        for i in range(len(old_instruction_containers)):
            ic = old_instruction_containers.pop()
            if ic.current_pipeline_stage.name == 'WB':
                new_instruction_containers.appendleft(ic)
            else:
                old_instruction_containers.appendleft(ic)

        exe_instruction_containers = deque([])
        for i in range(len(old_instruction_containers)):
            ic = old_instruction_containers.pop()
            if ic.current_pipeline_stage.name == 'EX':
                exe_instruction_containers.appendleft(ic)
            else:
                old_instruction_containers.appendleft(ic)

        new_instruction_containers = self.write_back_organize(new_instruction_containers, exe_instruction_containers)

        for i in range(len(old_instruction_containers)):
            ic = old_instruction_containers.pop()
            if ic.current_pipeline_stage.name == 'ID':
                new_instruction_containers.appendleft(ic)
            else:
                old_instruction_containers.appendleft(ic)

        for i in range(len(old_instruction_containers)):
            ic = old_instruction_containers.pop()
            if ic.current_pipeline_stage.name == 'IF':
                new_instruction_containers.appendleft(ic)
            else:
                old_instruction_containers.appendleft(ic)

        return new_instruction_containers


    @classmethod
    def write_back_organize(self, new_instruction_containers, exe_instruction_containers):
        """
        Organize the instruction containers in execution stage.
        """
        exec_priority = {}
        counter = LIMIT

        for i in range(len(exe_instruction_containers)):
            exec_ic = exe_instruction_containers.pop()

            functional_unit = exec_ic.instruction.determine_exec_functional_unit()

            is_fp_flag = False
            for fu in FP_UNITS:
                if (functional_unit == fu):
                    if (FP_CONFIG[fu]['PIPELINED']):
                        exec_priority[exec_ic] = counter + FP_CONFIG[fu]['CYCLES']
                    else:
                        exec_priority[exec_ic] = counter + FP_CONFIG[fu]['CYCLES'] + LIMIT
                    is_fp_flag = True
                    break
            if (not is_fp_flag):
                exec_priority[exec_ic] = counter

            counter -= 1

        sorted_ic = sorted(exec_priority.iteritems(), key=operator.itemgetter(1), reverse=True)
        for ic in sorted_ic:
            new_instruction_containers.appendleft(ic[0])

        return new_instruction_containers
