#! /usr/bin/python

from collections import deque

import re
import sys

DATA_BASE_ADDRESS = 100
INST_BASE_ADDRESS = 0
INSTRUCTION_SEGMENT_BASE = 0
INTEGER_EXEC_CYCLES = 1
REG_FILE_SIZE = 32
WORD_SIZE = 4

# Utility Funtions
def readLines(fileName):
    f = open(fileName, 'r')
    lines = [line for line in f]
    f.close()
    return lines

def bitsToVal(bits):
    val = 0
    pos = 2**31
    for i in range(len(bits)):
        if bits[i] == '1':
            val += pos
        pos /= 2
    return val
# -----

class InstructionMemory():
    def __init__(self, instFile, baseAddress):
        self.baseAddress = baseAddress
        self.instructionSize = WORD_SIZE
        self.instructions = {}
        self.labels = {}
        self.parseInstructions(instFile)

    def __repr__(self):
        instructions = ""
        for counter in sorted(self.instructions.keys()):
            instructions = instructions + str(counter) + " : " + str(self.instructions[counter]) + "\n"
        labels = ""
        for label in self.labels.keys():
            labels = labels + label + " : " + str(self.labels[label]) + "\n"
        return "\n* InstructionMemory *\nBase Address: %s\nInstructions:\n%sLabels:\n%s" % (self.baseAddress, instructions, self.labels)

    def parseInstructions(self, instFile):
        counter = self.baseAddress
        lines = readLines(instFile)
        for line in lines:
            pattern = re.compile('[,\s\n]+')
            instruction = pattern.split(line.strip())
            if (instruction[0][-1] == ':'):
                # This is a label instruction
                self.labels[instruction[0][0:-1].lower()] = counter                
            for i in range(len(instruction)):
                instruction[i] = instruction[i].lower()
            self.instructions[counter] = instruction
            counter += self.instructionSize

    def readInstAt(self, addr):
        if (self.instructions.has_key(addr)):
            return self.instructions[addr]
        return None

class DataMemory():
    def __init__(self, dataFile, baseAddress):
        self.baseAddress = baseAddress
        self.dataSize = WORD_SIZE
        self.data = {}
        self.parseData(dataFile)

    def __repr__(self):
        data = ""
        for counter in sorted(self.data.keys()):
            data = data + str(counter) + " : " + str(self.data[counter]) + "\n"
        return "\n* DataMemory *\nBase Address: %s\nData: \n%s" % (self.baseAddress, data)

    def parseData(self, dataFile):
        counter = self.baseAddress
        lines = readLines(dataFile)
        for line in lines:
            self.data[counter] = bitsToVal(line)
            counter += self.dataSize

class Memory():
    def __init__(self, instFile, dataFile):
        self.instMem = InstructionMemory(instFile, INST_BASE_ADDRESS)
        self.dataMem = DataMemory(dataFile, DATA_BASE_ADDRESS)

    def __repr__(self):
        return "\n* Memory *\n%s\n%s" % (self.instMem, self.dataMem)

    def readInstAt(self, addr):
        return self.instMem.readInstAt(addr)

class Instruction(object):
    def __init__(self, name):
        self.name = name
        self.raw = False
        self.war = False
        self.waw = False
        self.struct = False
        self.entryCycle = [0]*4
        self.exitCycle = [0]*4
        self.currentUnit = 'No'
        self.currentSubUnit = -1
        self.hasRead = False

    def __repr__(self):
        raw = "N"
        war = "N"
        waw = "N"
        struct = "N"
        if (self.raw == True):
            raw = "Y"
        if (self.war == True):
            war = "Y"
        if (self.waw == True):
            waw = "Y"
        if (self.struct == True):
            struct = "Y"
        #return "\t\t%s %s %s %s %s %s %s %s" % (self.exitCycle[0], self.exitCycle[1], self.exitCycle[2], self.exitCycle[3], raw, war, waw, struct)
        return "\t\t[%s-%s]\t\t%s,%s  %s,%s  %s,%s  %s,%s  %s  %s  %s  %s" % (self.currentUnit, self.currentSubUnit, self.entryCycle[0],self.exitCycle[0], self.entryCycle[1],self.exitCycle[1], self.entryCycle[2],self.exitCycle[2], self.entryCycle[3],self.exitCycle[3], raw, war, waw, struct)

    def enterFetch(self, clock, cpu):
        self.currentUnit = 'Fet'
        self.currentSubUnit = 1
        self.entryCycle[0] = clock
        cpu.fetch.isBusy = True

    def exitFetch(self, clock, cpu):
        self.exitCycle[0] = clock - 1
        cpu.fetch.isBusy = False

    def enterIU(self, clock, cpu):
        self.currentUnit = 'IU'
        self.currentSubUnit = 1
        self.entryCycle[2] = clock
        cpu.alu.intUnit.isBusy = True

    def exitIU(self, clock, cpu):
        cpu.alu.intUnit.isBusy = False

    def enterMem(self, clock, cpu):
        self.currentUnit = 'Mem'
        self.currentSubUnit = 1
        cpu.alu.memUnit.isBusy = True

    def exitMem(self, clock, cpu):
        self.exitCycle[2] = clock - 1
        cpu.alu.memUnit.isBusy = False

    def enterWB(self, clock, cpu):
        self.currentUnit = 'WB'
        self.currentSubUnit = 1
        self.entryCycle[3] = clock
        cpu.writeback.isBusy = True        

    def update(self, clock, cpu):
        if (self.currentUnit == 'No'):
            if (cpu.fetch.isBusy):
                self.struct |= True
            else:
                self.enterFetch(clock, cpu)
            return False
        if (self.currentUnit == 'Fet'):
            if (self.currentSubUnit == cpu.fetch.execCycles):
                if (cpu.decode.isBusy):
                    self.struct |= True
                else:
                    self.exitFetch(clock, cpu)
                    self.enterDecode(clock, cpu)
            else:
                self.currentSubUnit += 1
            return False
        if (self.currentUnit == 'Dec'):
            if (not self.hasRead):
                if (not self.tryRead(cpu)):
                    return False
            if (self.currentSubUnit == cpu.decode.execCycles):
                if (cpu.alu.intUnit.isBusy):
                    self.struct |= True
                else:
                    self.exitDecode(clock, cpu)
                    self.enterIU(clock, cpu)
            else:
                self.currentSubUnit += 1
            return False
        if (self.currentUnit == 'IU'):
            if (self.currentSubUnit == cpu.alu.intUnit.execCycles):
                if (cpu.alu.memUnit.isBusy):
                    self.struct |= True
                else:
                    self.exitIU(clock, cpu)
                    self.enterMem(clock, cpu)
            else:
                self.currentSubUnit += 1
            return False
        if (self.currentUnit == 'Mem'):
            if (self.currentSubUnit == cpu.alu.memUnit.execCycles):
                if (cpu.writeback.isBusy):
                    self.struct |= True
                else:
                    self.exitMem(clock, cpu)
                    self.enterWB(clock, cpu)
            else:
                self.currentSubUnit += 1
            return False
        if (self.currentUnit == 'WB'):
            if (self.currentSubUnit == cpu.writeback.execCycles):
                self.exitWB(clock, cpu)
                return True
            else:
                self.currentSubUnit += 1
                return False

class DestRegInstruction(Instruction):
    def __init__(self, name, destName):
        Instruction.__init__(self, name)
        self.destName = destName
        self.destVal = 0

    def exitWB(self, clock, cpu):
        self.exitCycle[3] = clock - 1
        cpu.writeback.isBusy = False
        cpu.registerFile.registers[self.destName].isBusy = False
        #print "Marked " + self.destName + " " + str(cpu.registerFile.registers[self.destName].isBusy)

class ThreeRegInstruction(DestRegInstruction):
    def __init__(self, name, destName, src1Name, src2Name):
        DestRegInstruction.__init__(self, name, destName)
        self.src1Name = src1Name
        self.src2Name = src2Name
        self.src1Val = 0
        self.src2Val = 0

    def __repr__(self):
        return "%s %s, %s, %s %s" % (self.name, self.destName, self.src1Name, self.src2Name, Instruction.__repr__(self))

    def tryRead(self, cpu):
        print self.destName, cpu.registerFile.registers[self.destName].isBusy, self.src1Name, cpu.registerFile.registers[self.src1Name].isBusy, self.src2Name, cpu.registerFile.registers[self.src2Name].isBusy, "hasread", self.hasRead
        if (self.hasRead):
            return True
        if (not (cpu.registerFile.registers[self.destName].isBusy) and
            not (cpu.registerFile.registers[self.src1Name].isBusy) and
            not (cpu.registerFile.registers[self.src2Name].isBusy)):
            cpu.registerFile.registers[self.destName].isBusy = True
            self.src1Val = cpu.registerFile.registers[self.src1Name].val
            self.src2Val = cpu.registerFile.registers[self.src2Name].val
            self.hasRead = True
            print "in if"
        else:
            print "in else"
            self.raw += True
        return not self.hasRead

    def enterDecode(self, clock, cpu):        
        self.currentUnit = 'Dec'
        self.currentSubUnit = 1
        self.entryCycle[1] = clock
        cpu.decode.isBusy = True
        ret = self.tryRead(cpu)

    def exitDecode(self, clock, cpu):
        self.exitCycle[1] = clock - 1
        cpu.decode.isBusy = False

class DADD(ThreeRegInstruction):
    def __init__(self, name, destName, src1Name, src2Name):
        ThreeRegInstruction.__init__(self, name, destName, src1Name, src2Name)

    def executeInst(self):
        self.destVal = self.src1Val + self.src2Val

class DSUB(ThreeRegInstruction):
    def __init__(self, name, destName, src1Name, src2Name):
        ThreeRegInstruction.__init__(self, name, destName, src1Name, src2Name)

    def executeInst(self):
        self.destVal = self.src1Val - self.src2Val

class ADDD(ThreeRegInstruction):
    def __init__(self, name, destName, src1Name, src2Name):
        ThreeRegInstruction.__init__(self, name, destName, src1Name, src2Name)

    def executeInst(self):
        self.destVal = self.src1Val + self.src2Val

class SUBD(ThreeRegInstruction):
    def __init__(self, name, destName, src1Name, src2Name):
        ThreeRegInstruction.__init__(self, name, destName, src1Name, src2Name)

    def executeInst(self):
        self.destVal = self.src1Val - self.src2Val

class MULD(ThreeRegInstruction):
    def __init__(self, name, destName, src1Name, src2Name):
        ThreeRegInstruction.__init__(self, name, destName, src1Name, src2Name)

    def executeInst(self):
        self.destVal = self.src1Val * self.src2Val

class DIVD(ThreeRegInstruction):
    def __init__(self, name, destName, src1Name, src2Name):
        ThreeRegInstruction.__init__(self, name, destName, src1Name, src2Name)

    def executeInst(self):
        self.destVal = self.src1Val / self.src2Val

class AND(ThreeRegInstruction):
    def __init__(self, name, destName, src1Name, src2Name):
        ThreeRegInstruction.__init__(self, name, destName, src1Name, src2Name)

    def executeInst(self):
        self.destVal = self.src1Val and self.src2Val

class OR(ThreeRegInstruction):
    def __init__(self, name, destName, src1Name, src2Name):
        ThreeRegInstruction.__init__(self, name, destName, src1Name, src2Name)

    def executeInst(self):
        self.destVal = self.src1Val or self.src2Val

class TwoRegOneImmInstruction(DestRegInstruction):
    def __init__(self, name, destName, srcName, imm):
        DestRegInstruction.__init__(self, name, destName)
        self.srcName = srcName
        self.srcVal = 0
        self.imm = imm

    def __repr__(self):
        return "%s %s, %s, %s %s" % (self.name, self.destName, self.srcName, self.imm, Instruction.__repr__(self))
        
    def tryRead(self, cpu):
        print self.destName, cpu.registerFile.registers[self.destName].isBusy, self.srcName, cpu.registerFile.registers[self.srcName].isBusy
        if (self.hasRead):
            return True
        if (not (cpu.registerFile.registers[self.destName].isBusy) and
            not (cpu.registerFile.registers[self.srcName].isBusy)):
            cpu.registerFile.registers[self.destName].isBusy = True
            self.srcVal = cpu.registerFile.registers[self.srcName].val
            self.hasRead = True
        else:
            self.raw += True
        return not self.hasRead

    def enterDecode(self, clock, cpu):        
        self.currentUnit = 'Dec'
        self.currentSubUnit = 1
        self.entryCycle[1] = clock
        cpu.decode.isBusy = True
        ret = self.tryRead(cpu)

    def exitDecode(self, clock, cpu):
        self.exitCycle[1] = clock - 1
        cpu.decode.isBusy = False

class DADDI(TwoRegOneImmInstruction):
    def __init__(self, name, destName, srcName, imm):
        TwoRegOneImmInstruction.__init__(self, name, destName, srcName, imm)

    def executeInst(self):
        self.destVal = self.srcVal + self.immVal

class DSUBI(TwoRegOneImmInstruction):
    def __init__(self, name, destName, srcName, imm):
        TwoRegOneImmInstruction.__init__(self, name, destName, srcName, imm)

    def executeInst(self):
        self.destVal = self.srcVal - self.immVal

class ANDI(TwoRegOneImmInstruction):
    def __init__(self, name, destName, srcName, imm):
        TwoRegOneImmInstruction.__init__(self, name, destName, srcName, imm)

    def executeInst(self):
        self.destVal = self.srcVal and self.immVal

class ORI(TwoRegOneImmInstruction):
    def __init__(self, name, destName, srcName, imm):
        TwoRegOneImmInstruction.__init__(self, name, destName, srcName, imm)

    def executeInst(self):
        self.destVal = self.srcVal or self.immVal

class LW(TwoRegOneImmInstruction):
    def __init__(self, name, destName, srcName, imm):
        TwoRegOneImmInstruction.__init__(self, name, destName, srcName, imm)

    def __repr__(self):
        return "%s %s, %s(%s) %s" % (self.name, self.destName, self.imm, self.srcName, Instruction.__repr__(self))

class LD(TwoRegOneImmInstruction):
    def __init__(self, name, destName, srcName, imm):
        TwoRegOneImmInstruction.__init__(self, name, destName, srcName, imm)

    def __repr__(self):
        return "%s %s, %s(%s) %s" % (self.name, self.destName, self.imm, self.srcName, Instruction.__repr__(self))

class SW(TwoRegOneImmInstruction):
    def __init__(self, name, destName, srcName, imm):
        TwoRegOneImmInstruction.__init__(self, name, destName, srcName, imm)

    def execute(self):
        #self.destVal = Mem[self.immVal + self.srcVal]
        pass

class SD(TwoRegOneImmInstruction):
    def __init__(self, name, destName, srcName, imm):
        TwoRegOneImmInstruction.__init__(self, name, destName, srcName, imm)

    def execute(self):
        #self.destVal = Mem[self.immVal + self.srcVal]
        pass

class Branch(Instruction):
    def __init__(self, name, label):
        Instruction.__init__(self, name)
        self.label = label

class J(Branch):
    def __init__(self, name, label):
        Branch.__init__(self, name, label)

    def __repr__(self):
        return "%s %s %s" % (self.name, self.label, Instruction.__repr__(self))

    def execute(self):
        #update pc to label
        pass

class ConditionalBranch(Branch):
    def __init__(self, name, src1Name, src2Name, label):
        Branch.__init__(self, name, label)
        self.src1Name = src1Name
        self.src2Name = src2Name
        self.src1 = 0
        self.src2 = 0

    def __repr__(self):
        return "%s %s, %s, %s %s" % (self.name, self.src1Name, self.src2Name, self.label, Instruction.__repr__(self))

class BEQ(ConditionalBranch):
    def __init__(self, name, src1Name, src2Name, label):
        ConditionalBranch.__init__(self, name, src1Name, src2Name, label)

    def executeInst(self):
        # update pc is eq
        pass

class BNE(ConditionalBranch):
    def __init__(self, name, src1Name, src2Name, label):
        ConditionalBranch.__init__(self, name, src1Name, src2Name, label)

    def executeInst(self):
        # update pc is ne
        pass

class HLT(Instruction):
    def __init__(self, name):
        Instruction.__init__(self, name)

    def __repr__(self):
        return "%s %s" % (self.name, Instruction.__repr__(self))

    def execute(self):
        pass

class Register():
    def __init__(self, val, isBusy):
        self.val = val
        self.isBusy = isBusy

    def __repr__(self):
        return "\nValue: %s\nBusy: %s" % (self.val, self. isBusy)

class RegisterFile():
    def __init__(self, regFile):
        self.regFileSize = REG_FILE_SIZE
        self.registers = {}
        self.parseRegisters(regFile)

    def __repr__(self):
        registers = ""
        for regName, reg in self.registers.items():
            registers = registers + "Name: " + regName + "\n" + str(reg) + "\n"
        return "\n* RegisterFile *\n%s" % (registers)    

    def parseRegisters(self, regFile):
        lines = readLines(regFile)
        count = 0
        for line in lines:
            self.registers['r'+str(count)] = Register(bitsToVal(line), False)
            self.registers['f'+str(count)] = Register(0, False)
            count += 1

class Unit():
    def __init__(self, name, cycles, isPipelined, unitId):
        self.name = name
        self.execCycles = int(cycles)        
        self.pipelineSize = 1
        if (isPipelined):
            self.pipelineSize = self.execCycles
        self.isBusy = False
        self.isPipelined = isPipelined
        self.instQ = deque([Instruction("noop")]*self.pipelineSize)
        self.unitId = unitId

    def __repr__(self):
        return "\n* %s *\nCycles: %s\nPipeLine Size: %s\nPipelined: %s" % (self.name, self.execCycles, self.pipelineSize, self.isPipelined)

    def execute(self, instruction, cycle):
        instruction.entryCycle[self.unitId] = cycle
        self.isBusy = True
        if not (self.isPipelined):
            instruction.exitCycle[self.unitId] = cycle + self.execCycles - 1
            self.isBusy = False
        
# May need to seperate IntegerUnit and FPUnits
class ALU():
    def __init__(self, configFile):
        lines = readLines(configFile)
        self.intUnit = Unit("IntegerUnit", INTEGER_EXEC_CYCLES, False, 2)
        for line in lines:
            pattern = re.compile('[\s:,\n]+')
            vals = pattern.split(line.strip())
            if (vals[0].lower() == "fp"):
                isPipe = True
                if (vals[3].lower().replace('\n','') != "yes"):
                    isPipe = False
                if (vals[1].replace(':','').lower() == "adder"):
                    self.floatAddUnit = Unit("FPAdder", vals[2].replace(',',''), isPipe, 2)
                if (vals[1].replace(':','').lower() == "multiplier"):
                    self.floatMulUnit = Unit("FPMultiplier", vals[2].replace(',',''), isPipe, 2)
                if (vals[1].replace(':','').lower() == "divider"):
                    self.floatDivUnit = Unit("FPDivider", vals[2].replace(',',''), isPipe, 2)
            if (vals[0].lower() == "main"):
                self.memUnit = Unit("MemoryUnit", vals[2].replace('\n',''), False, 2)

    def __repr__(self):
        return "\n* ALU *\n%s\n%s\n%s\n%s\n%s" % (self.intUnit, self.memUnit, self.floatAddUnit, self.floatMulUnit, self.floatDivUnit)

class CPU():
    def __init__(self, regFile, configFile):
        self.registerFile = RegisterFile(regFile)
        self.fetch = Unit("Fetch", 1, False, 0)
        self.decode = Unit("Decode", 1, False, 1)
        self.alu = ALU(configFile)
        self.writeback = Unit("WriteBack", 1, False, 3)
        
    def __repr__(self):
        return "\n* CPU *\n%s%s" % (self.registerFile, self.alu)

    def execute(self, instruction, clock):
        self.fetch.execute(instruction, clock)

class Computer():
    def __init__(self, instFile, dataFile, regFile, configFile):
        self.pc = INSTRUCTION_SEGMENT_BASE
        self.memory = Memory(instFile, dataFile)
        self.cpu = CPU(regFile, configFile)
        self.clock = 0

    def __repr__(self):
        return "* Computer *\nProgram Counter: %s\n%s%s\n" % (self.pc, self.memory, self.cpu)

    def getInstInstance(self, instruction):
        zero = 0
        if (instruction[0][-1] == ':'):
            zero = 1
        else:
            zero = 0
        if (instruction[zero] == 'lw'):
            return LW(instruction[zero], instruction[zero+1], instruction[zero+2].split('(')[1].split(')')[0], instruction[zero+2].split('(')[0])
        if (instruction[zero] == 'sw'):
            return SW(instruction[zero], instruction[zero+1], instruction[zero+2].split('(')[1].split(')')[0], instruction[zero+2].split('(')[0])
        if (instruction[zero] == 'l.d'):
            return LD(instruction[zero], instruction[zero+1], instruction[zero+2].split('(')[1].split(')')[0], instruction[zero+2].split('(')[0])
        if (instruction[zero] == 's.d'):
            return SD(instruction[zero], instruction[zero+1], instruction[zero+2].split('(')[1].split(')')[0], instruction[zero+2].split('(')[0])
        if (instruction[zero] == 'dadd'):
            return DADD(instruction[zero], instruction[zero+1], instruction[zero+2], instruction[zero+3])
        if (instruction[zero] == 'daddi'):
            return DADDI(instruction[zero], instruction[zero+1], instruction[zero+2], instruction[zero+3])
        if (instruction[zero] == 'dsub'):
            return DSUB(instruction[zero], instruction[zero+1], instruction[zero+2], instruction[zero+3])
        if (instruction[zero] == 'dsubi'):
            return DSUBI(instruction[zero], instruction[zero+1], instruction[zero+2], instruction[zero+3])
        if (instruction[zero] == 'and'):
            return AND(instruction[zero], instruction[zero+1], instruction[zero+2], instruction[zero+3])
        if (instruction[zero] == 'andi'):
            return ANDI(instruction[zero], instruction[zero+1], instruction[zero+2], instruction[zero+3])
        if (instruction[zero] == 'or'):
            return OR(instruction[zero], instruction[zero+1], instruction[zero+2], instruction[zero+3])
        if (instruction[zero] == 'ori'):
            return ORI(instruction[zero], instruction[zero+1], instruction[zero+2], instruction[zero+3])
        if (instruction[zero] == 'add.d'):
            return ADDD(instruction[zero], instruction[zero+1], instruction[zero+2], instruction[zero+3])
        if (instruction[zero] == 'sub.d'):
            return SUBD(instruction[zero], instruction[zero+1], instruction[zero+2], instruction[zero+3])
        if (instruction[zero] == 'mul.d'):
            return MULD(instruction[zero], instruction[zero+1], instruction[zero+2], instruction[zero+3])
        if (instruction[zero] == 'div.d'):
            return DIVD(instruction[zero], instruction[zero+1], instruction[zero+2], instruction[zero+3])
        if (instruction[zero] == 'j'):
            return J(instruction[zero], instruction[zero+1])
        if (instruction[zero] == 'beq'):
            return BEQ(instruction[zero], instruction[zero+1], instruction[zero+2], instruction[zero+3])
        if (instruction[zero] == 'bne'):
            return BNE(instruction[zero], instruction[zero+1], instruction[zero+2], instruction[zero+3])
        if (instruction[zero] == 'hlt'):
            return HLT(instruction[zero])

    def reorderInst(self, activeInst):
        pass

    def execute(self):
        instruction = self.getInstInstance(self.memory.readInstAt(self.pc))
        activeInst = [instruction]
        while(len(activeInst) != 0):
            self.clock += 1
            self.reorderInst(activeInst)
            toRemove = []
            for inst in activeInst:                                
                if (inst.update(self.clock, self.cpu)):
                    print inst
                    toRemove.append(inst)
                if not (self.cpu.fetch.isBusy):
                    self.pc += WORD_SIZE
                    instruction = self.memory.readInstAt(self.pc)
                    if (instruction):
                        instruction = self.getInstInstance(instruction)
                        activeInst.append(instruction)
            for inst in toRemove:
                activeInst.remove(inst)

def main(instFile, dataFile, regFile, configFile, resultFile="result.txt"):
    computer = Computer(instFile, dataFile, regFile, configFile)
    #print computer
    computer.execute()

if __name__ == "__main__":
    nArgs = len(sys.argv)
    args = sys.argv
    if (nArgs != 5):
        print "Usage: simulator inst.txt data.txt reg.txt config.txt result.txt"
        exit()
    main(args[1], args[2], args[3], args[4])
