from typing import List
import re
from collections import OrderedDict


# 運算函數區塊
class Error(Exception):
    pass


class operatorNotDefind(Error):
    def __init__(self):
        print("operator not defined")


class symbolNotDefind(Error):
    def __init__(self):
        print("symbol not defined")


operatorList = ["+", "-", "*", "/"]


def two_op_eval(operand1: float, operator: str, operand2: float) -> float:
    value = 0
    if operator == '+':
        value = operand1 + operand2
    elif operator == '-':
        value = operand1 - operand2
    elif operator == '*':
        value = operand1 * operand2
    elif operator == '/':
        value = operand1 / operand2
    else:
        raise operatorNotDefind
    return value


def find_operator(exp: str, curPos: int):
    for ch in exp[curPos:]:
        if ch in operatorList:
            return curPos
        curPos += 1
    return -1


def get_exp_tokens(exp: str, symtab: dict) -> List[str]:
    exp = exp.replace(" ", "")
    tokens = []
    pos = 0
    lastPos = 0
    while pos != -1:
        pos = find_operator(exp, lastPos + 1)
        if pos != -1:
            tokens.append(exp[lastPos:pos])
            tokens.append(exp[pos:pos + 1])
            lastPos = pos + 1
    tokens.append(exp[lastPos:])
    index = 0
    for token in tokens:
        if token in symtab:
            tokens[index] = symtab[token]
        elif token.isalpha():
            raise symbolNotDefind
        index += 1
    return tokens


def expression_eval(expression: str, symtab: dict) -> float:
    tokens = get_exp_tokens(expression, symtab)
    operandStk = []
    operatorStk = []
    operandStk.append(tokens[0])
    tokens = tokens[1:]
    while len(tokens) > 0:
        curToken = tokens[0]
        tokens = tokens[1:]
        if curToken == "*" or curToken == "/":
            rightOperand = tokens[0]
            tokens = tokens[1:]
            leftOperand = operandStk.pop()
            operandStk.append(two_op_eval(float(leftOperand), curToken, float(rightOperand)))
        elif curToken == "+" or curToken == "-":
            if len(operatorStk) > 0:
                if operatorStk[len(operatorStk) - 1] == '+' or operatorStk[len(operatorStk) - 1] == '-':
                    operator = operatorStk.pop()
                    rightOperand = operandStk.pop()
                    leftOperand = operandStk.pop()
                    operandStk.append(two_op_eval(float(leftOperand), operator, float(rightOperand)))
            operatorStk.append(curToken)
        else:
            operandStk.append(curToken)
    while len(operatorStk) > 0:
        rightOperand = operandStk.pop()
        leftOperand = operandStk.pop()
        operator = operatorStk.pop()
        operandStk.append(two_op_eval(float(leftOperand), operator, float(rightOperand)))
    return int(operandStk.pop())


# 組譯器函數區塊

def trimEndSpace(str):
    resultStr = str
    while resultStr.endswith(" "):
        resultStr = resultStr[:-1]
    return resultStr


def hexToDecimal(numStr):
    return int(numStr, base=16)


def isFormat1(opStr):
    list = ["FIX", "FLOAT", "HIO", "NORM", "SIO", "TIO"]
    for item in list:
        if item == opStr:
            return True
    return False


def isFormat2(opStr):
    list = ["ADDR", "CLEAR", "COMPR", "DIVR", "MULR", "RMO", "SHIFTL", "SHIFTR", "SUBR", "SVC", "TIXR"]
    for item in list:
        if item == opStr:
            return True
    return False


def trimOprandPrefix(str) -> str:
    if str[0] == '#' or str[0] == '@':
        return str[1:]
    return str


def trimOpPrefix(str):
    if str[0] == "+":
        return str[1:]
    return str


def extractLiteral(s: str):
    """ return literal type and literal content"""
    regex = r"=([CX])'(\w+)'"
    matches = re.match(regex, s)
    if matches:
        return (matches.group(1), matches.group(2))
    else:
        raise ("literal error")


def to_ascii_hex_str(s: str):
    r = ""
    for c in s:
        r += hex(ord(c))[2:]
    return r


def insert_literal(tempLiteralList, curLine, lines, LocationCounter, endLoc, literalPool, curProgramBlockName: str):
    """ get finalCurLine and final LocationCounter"""
    for literal in tempLiteralList:
        curLine += 1
        insertStr = "*".ljust(7)
        insertStr += literal.ljust(8)
        insertStr += "".ljust(8)
        lines.insert(curLine, insertStr)
        literalPool[literal] = (LocationCounter, curProgramBlockName)
        (literlType, content) = extractLiteral(literal)
        if literlType == 'X':
            LocationCounter += int(len(content) / 2)
        else:
            LocationCounter += len(content)
            endLoc.append(LocationCounter)
    tempLiteralList.clear()
    return curLine, LocationCounter


def parseLine(lineStr):
    lineStr = trimEndSpace(lineStr)
    if (lineStr.find('.') != -1):
        return ('', '', '')
    leftCol = ""
    middleCol = ""
    rightCol = ""
    if lineStr[0] != ' ':
        leftCol = str(lineStr[0:lineStr.find(' ', 0)])
    if len(lineStr) < 8:
        return (leftCol, middleCol, rightCol)
    if lineStr[8] != ' ':
        nextSpace = lineStr.find(' ', 8)
        if lineStr[7] != ' ':
            middleCol += lineStr[7]
        if nextSpace != -1:
            middleCol += str(lineStr[8:nextSpace])
        else:
            middleCol += str(lineStr[8:len(lineStr)])
    if len(lineStr) < 16:
        return (leftCol, middleCol, rightCol)
    if lineStr[16] != ' ':
        if lineStr[15] != ' ':
            rightCol += lineStr[15]
        rightCol += str(lineStr[16:len(lineStr)])
    return (leftCol, middleCol, rightCol)


# 得到此指令是哪一種類型的，有三大類型Simple、Indirect(@)、Immediate(#)的定址，細分有18種，回傳是第幾個
def getInstructionNum(op: str, operand: str, symbolTable: dict, curPC: int, literalPool: dict):
    if operand[0] == '#':  # immediate addressing
        trimOperand = operand[1:]
        if op[0] == '+':  # 為format 4
            return 15
        if trimOperand.isnumeric():
            if 0 <= int(trimOperand) <= 4095:
                return 14
        if trimOperand in symbolTable:
            address = symbolTable[trimOperand]
        elif trimOperand in literalPool:
            address = literalPool[trimOperand]
        else:
            raise ("operand not define")
        disp = address - curPC
        # -2048 <= disp <= 2047-> 可以pc-relative
        if -2048 <= disp <= 2047:
            return 16
        else:  # 用base addressing
            return 17
    elif operand[0] == '@':  # indirect addressing
        trimOperand = operand[1:]
        if op[0] == '+':
            return 11
        if trimOperand.isnumeric():
            if 0 <= int(trimOperand) <= 4095:
                return 10
            else:
                raise ("超過範圍")
        if trimOperand in symbolTable:
            address = symbolTable[trimOperand]
        elif trimOperand in literalPool:
            address = literalPool[trimOperand]
        else:
            raise ("operand not define")
        disp = address - curPC
        if -2048 <= disp <= 2047:
            return 12
        else:
            return 13
    else:  # simple addressing
        commaPos = operand.find(',', 0)
        XPos = operand.find('X', commaPos)
        trimOperand = operand[:commaPos]
        if commaPos != -1 and XPos != -1:  # indexed addressing
            if op[0] == '+':
                return 5
            if trimOperand.isnumeric():
                if 0 <= int(trimOperand) <= 4095:
                    return 4
            if trimOperand in symbolTable:
                address = symbolTable[trimOperand]
            elif trimOperand in literalPool:
                address = literalPool[trimOperand]
            else:
                raise ("operand not define")
            disp = address - curPC
            if -2048 <= disp <= 2047:
                return 6
            else:
                return 7
        else:
            if operand.isnumeric():
                return 0
            elif op[0] == '+':
                return 1
            if operand in symbolTable:
                address = symbolTable[operand]
            elif operand in literalPool:
                address = literalPool[operand]
            else:
                raise ("operand not define")
            disp = address - curPC
            if -2048 <= disp <= 2047:
                return 2
            else:
                return 3


# for instruction format 3 and format 4
def calculateDispOrAddr(instructionNum: int, operand: str, curPC: int, curBase: int, symbolTable: dict,
                        literalPool: dict, curProgramBlockName: str, programBlockStart: dict) -> str:
    """  回傳指令object Code最後一個欄位的hex值，已補0湊齊位數  """
    trimPrefixOperand = trimOprandPrefix(operand)
    commaPos = trimPrefixOperand.find(',', 0)
    if commaPos != -1:
        trimOperand = trimPrefixOperand[:commaPos]
    else:
        trimOperand = trimPrefixOperand
    if trimOperand.isnumeric():
        operandValue = int(trimOperand)
    else:
        if trimOperand in symbolTable:
            operandValue = symbolTable[trimOperand]
        elif operand in literalPool:
            operandValue = literalPool[operand]
        else:
            raise ("operand not define")
    operandHex = hex(int(operandValue))
    if instructionNum in (0, 4, 10, 14):  # 單純的format 3，disp欄位佔12bit
        return operandHex[2:].zfill(3)  # 1個hex number -> 4bit => 至少要有三個hex數字不夠補0
    elif instructionNum in (1, 5, 11, 15):  # format 4，address欄位佔20bit
        return operandHex[2:].zfill(5)  # 1個hex number -> 4bit => 至少要有五個hex數字不夠補0
    elif instructionNum in (2, 6, 12, 16):  # 需要計算地址的指令，是pc-relative定址
        targetAddress = int(operandValue)
        disp = targetAddress - (curPC + programBlockStart[curProgramBlockName])
        if disp < 0:
            rDisp = hex((disp & 0xfff))[2:].zfill(3)
        else:
            rDisp = hex(disp)[2:].zfill(3)
        return rDisp
    elif instructionNum in (3, 7, 13, 17):  # 需要計算地址的指令，是base定址
        targetAddress = int(operandValue)
        disp = targetAddress - curBase
        rDisp = hex(disp)[2:].zfill(3)
        return rDisp


def assemble_pass1(lines: List[str]) -> (dict, int, List, int, dict):
    """return symbol table ,  programLeng, endLoc, startAddress, literalPool"""
    tempLiteralList = []
    literalPool = {}
    symbolTable = {}
    programBlockLoc = OrderedDict()
    curProgramBlockName = "default"
    programBlockLoc[curProgramBlockName] = 0
    endLoc = []
    startAddress = hexToDecimal(parseLine(lines[0])[2])
    LocationCounter = startAddress
    curLine = -1
    for line in lines[1:]:
        curLine += 1
        colTuple = parseLine(trimEndSpace(line))
        labelStr = colTuple[0]
        opStr = colTuple[1]
        operandStr = colTuple[2]
        if colTuple == ('', '', '') or opStr == 'BASE' or opStr == 'NOBASE' or opStr == 'EQU': continue
        if opStr == 'END':
            (curLine, LocationCounter) = insert_literal(tempLiteralList, curLine - 1, lines, LocationCounter, endLoc,
                                                        literalPool, curProgramBlockName)
            programBlockLoc[curProgramBlockName] = LocationCounter
            break
        if opStr == 'LTORG':
            curLine += 1
            (curLine, LocationCounter) = insert_literal(tempLiteralList, curLine, lines, LocationCounter, endLoc,
                                                        literalPool, curProgramBlockName)
            continue
        elif opStr == "USE":
            # TODO:  need to complete pass1 handle program block change
            print("haha", LocationCounter)
            programBlockLoc[curProgramBlockName] = LocationCounter
            if operandStr not in programBlockLoc and operandStr != "":
                programBlockLoc[operandStr] = 0
            if operandStr == "":
                curProgramBlockName = "default"
            else:
                curProgramBlockName = operandStr
            LocationCounter = programBlockLoc[curProgramBlockName]
            print("haha", LocationCounter)
            continue
        if (operandStr != ""):
            if (operandStr[0] == '='):
                if tempLiteralList.count(operandStr) == 0:
                    tempLiteralList.append(operandStr)
        if labelStr != '':
            if (labelStr in symbolTable):
                raise ("重複的標籤")
            symbolTable[labelStr] = (LocationCounter, curProgramBlockName)
        if opStr == 'BYTE':
            if operandStr[0] == 'C':
                LocationCounter += len(operandStr[2:-1])
            elif operandStr[0] == 'X':
                LocationCounter += int(len(operandStr[2:-1]) / 2)
        elif opStr == 'WORD':
            LocationCounter += 3
        elif opStr == 'RESB':
            LocationCounter += int(operandStr)
        elif opStr == 'RESW':
            LocationCounter += int(operandStr) * 3
        else:  # 是format多少就是占多少byte , format 2 佔 2 bytes
            if opStr[0] == '+':  # format 4
                LocationCounter += 4
            elif isFormat1(opStr):
                LocationCounter += 1
            elif isFormat2(opStr):
                LocationCounter += 2
            else:  # format 3
                LocationCounter += 3
        endLoc.append(LocationCounter)
    programLeng = LocationCounter
    print(programBlockLoc, "haha")
    programBlockStart = {}
    sum = 0
    for key, value in programBlockLoc.items():
        programBlockStart[key] = sum
        sum += value
    for key, value in symbolTable.items():
        relativePos = value[0]
        block = value[1]
        symbolTable[key] = relativePos + programBlockStart[block]
    for key, value in literalPool.items():
        relativePos = value[0]
        block = value[1]
        literalPool[key] = relativePos + programBlockStart[block]
    return symbolTable, programLeng, endLoc, startAddress, literalPool, programBlockStart


MnemonicOpcodeDic = \
    {"ADD": 0x18,
     "ADDF": 0x58,
     "ADDR": 0x90,
     "AND": 0x40,
     "CLEAR": 0xB4,
     "COMP": 0x28,
     "COMPF": 0x88,
     "COMPR": 0xA0,
     "DIV": 0x24,
     "DIVF": 0x64,
     "DIVR": 0x9C,
     "FIX": 0xC4,
     "FLOAT": 0xC0,
     "HIO": 0xF4,
     "J": 0x3C,
     "JEQ": 0x30,
     "JGT": 0x34,
     "JLT": 0x38,
     "JSUB": 0x48,
     "LDA": 0,
     "LDB": 0x68,
     "LDCH": 0x50,
     "LDF": 0x70,
     "LDL": 0x8,
     "LDS": 0x6C,
     "LDT": 0x74,
     "LDX": 0x4,
     "LPS": 0xD0,
     "MUL": 0x20,
     "MULF": 0x60,
     "MULR": 0x98,
     "NORM": 0xC8,
     "OR": 0x44,
     "RD": 0xD8,
     "RMO": 0xAC,
     "RSUB": 0x4C,
     "SHIFTL": 0xA4,
     "SHIFTR": 0xA8,
     "SIO": 0xF0,
     "SSK": 0xEC,
     "STA": 0x0C,
     "STB": 0x78,
     "STCH": 0x54,
     "STF": 0x80,
     "STI": 0xD4,
     "STL": 0x14,
     "STS": 0x7C,
     "STSW": 0xE8,
     "STT": 0x84,
     "STX": 0x10,
     "SUB": 0x1C,
     "SUBF": 0x5C,
     "SUBR": 0x94,
     "SVC": 0xB0,
     "TD": 0xE0,
     "TIO": 0xF8,
     "TIX": 0x2C,
     "TIXR": 0xB8,
     "WD": 0xDC
     }

MnemonicRegisterDic = {
    "A": 0,
    "X": 1,
    "L": 2,
    "B": 3,
    "S": 4,
    "T": 5,
    "F": 6
}

flagBitsDict = {
    0: "110000",
    1: "110001",
    2: "110010",
    3: "110100",
    4: "111000",
    5: "111001",
    6: "111010",
    7: "111100",
    8: "000",
    9: "001",
    10: "100000",
    11: "100001",
    12: "100010",
    13: "100100",
    14: "010000",
    15: "010001",
    16: "010010",
    17: "010100"
}


def assemble_pass2(lines: List[str], symbolTable: dict, endLoc: List[int], literalPool: dict,
                   programBlockStart: dict) -> (List[int], List[str]):
    """return objectCodes, modifiedLoc"""
    curLoc = 0
    curBase = 0
    objectCodes = []
    modifiedLoc = []
    curProgramBlockName = "default"
    for line in lines[1:]:
        colTuple = parseLine(line)
        labelStr = colTuple[0]
        opStr = colTuple[1]
        operandStr = colTuple[2]
        if colTuple == ('', '', '') or opStr == "USE":
            if operandStr == "":
                curProgramBlockName = "default"
            else:
                curProgramBlockName = operandStr
            continue
        if opStr == 'END':
            break
        elif opStr == 'BASE':
            curBase = int(symbolTable[operandStr])
            print("curbase", hex(curBase))
            continue
        elif opStr == 'RESW' or opStr == 'RESB':
            curLoc += 1
            continue
        elif opStr == 'EQU':
            if operandStr == '*':
                symbolTable[labelStr] = endLoc[curLoc - 1] + programBlockStart[curProgramBlockName]
            else:
                print(symbolTable)
                symbolTable[labelStr] = int(expression_eval(operandStr, symbolTable))
            continue
        elif opStr[0] == '=':
            (literlType, content) = extractLiteral(opStr)
            if literlType == 'X':
                objectCodes.append(content)
            elif literlType == 'C':
                objectCodes.append(to_ascii_hex_str(content))
            continue
        if opStr == 'BYTE':
            if (operandStr[0] == 'C'):
                resultStr = ""
                for ch in operandStr[2:-1]:
                    resultStr += hex(ord(ch))[2:]
                objectCodes.append(resultStr)
            elif operandStr[0] == 'X':
                resultStr = operandStr[2:-1]
                objectCodes.append(resultStr)
        elif opStr == 'WORD':  # WORD 寫的數字是十進位，要轉成十六進位存
            objectCodes.append(hex(int(operandStr)))
        elif operandStr != '':
            opValue = MnemonicOpcodeDic[trimOpPrefix(opStr)]
            if isFormat2(opStr):
                opHex = hex(opValue)[2:]
                commaPos = operandStr.find(',')
                regesterHex = ""
                if commaPos != -1:  # 有兩個暫存器
                    regesterHex += str(MnemonicRegisterDic[operandStr[0]])
                    regesterHex += str(MnemonicRegisterDic[operandStr[commaPos + 1]])
                else:
                    regesterHex += str(MnemonicRegisterDic[operandStr[0]])
                    regesterHex += "0"
                objectCodes.append(opHex + regesterHex)
            else:
                binCutOp = bin(opValue)[2:-2]
                instructNum = getInstructionNum(opStr, operandStr, symbolTable, endLoc[curLoc], literalPool)
                opcodeAndFourbitsFlagHex = hex(int(binCutOp + flagBitsDict[instructNum], 2))[2:].zfill(3)
                addressOrDispHex = calculateDispOrAddr(instructNum, operandStr, endLoc[curLoc], curBase, symbolTable,
                                                       literalPool, curProgramBlockName, programBlockStart)
                objectCodes.append(opcodeAndFourbitsFlagHex + addressOrDispHex)
                if instructNum == 1 or instructNum == 5:
                    modifiedLoc.append(endLoc[curLoc - 1] + 1)
        elif opStr == 'RSUB':
            objectCodes.append("4f0000")
        curLoc += 1
    return objectCodes, modifiedLoc
