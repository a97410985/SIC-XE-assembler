from toolkit import *
import filecmp

readFileName = "sic_xe_fig2_9"
f = open(readFileName + ".txt", "r")
fileContent = f.read()
lines = fileContent.split('\n')
f.close()

# pass 1
(symbolTable, programLeng, endLoc, startAddress, literalPool, programBlockStart) = assemble_pass1(lines)
for line in lines:
    print(line)
print(literalPool,"literal")
# pass 2
(objectCodes, modifiedLoc) = assemble_pass2(lines, symbolTable, endLoc, literalPool,programBlockStart)
print("==============")
print(symbolTable)

saveFile = open(readFileName + "_object_code.txt", 'w')

i = 0
for line in lines[1:]:
    colTuple = parseLine(line)
    opStr = colTuple[1]
    saveFile.write(line)
    if opStr == 'END' :
        saveFile.write("\n")
        break
    if opStr == 'BASE' or opStr == 'RESW' or opStr == 'RESB' or opStr == 'EQU' or opStr == "USE":
        saveFile.write("\n")
        continue
    if colTuple == ('', '', '') or opStr == 'LTORG':
        saveFile.write("\n")
        continue
    lineLeng = len(line)
    appendSpaceNum = 30 - lineLeng
    saveFile.write(" " * appendSpaceNum)
    saveFile.write(objectCodes[i] + "\n")
    i += 1
saveFile.close()



saveObjFile = open(readFileName + "_object_program.txt", 'w')
FirstcolTuple = parseLine(lines[0])
programName = FirstcolTuple[0]
saveObjFile.write("H" + programName + " " * (6 - len(programName)))
saveObjFile.write("000000")
saveObjFile.write(hex(programLeng)[2:].zfill(6) + "\n")
startLoc = endLoc.copy()
startLoc.insert(0, startAddress)
nextRecordStart = startAddress
recordContent = ""
curLocCounter = -1
curObjCounter = 0
for line in lines[1:]:
    colTuple = parseLine(line)
    opStr = colTuple[1]
    if colTuple[1] == 'END':
        break
    if colTuple == ('', '', '') or opStr == 'BASE' or opStr == 'NOBASE' or opStr == 'EQU' or opStr == 'LTORG':
        continue
    if colTuple[0].find(".") == 0: continue

    curLocCounter += 1
    if colTuple[1] == 'RESW' or colTuple[1] == 'RESB':  # 結束現在的text record
        if recordContent == "": continue
        saveObjFile.write("T" + hex(nextRecordStart)[2:].zfill(6) + "#")
        saveObjFile.write(hex((int)(len(recordContent) / 2))[2:].zfill(2) + "#")
        saveObjFile.write(recordContent + "\n")
        recordContent = ""
        continue
    if (len(recordContent) + len(objectCodes[curObjCounter])) > 58:
        saveObjFile.write("T" + hex(nextRecordStart)[2:].zfill(6) + "#")
        saveObjFile.write(hex((int)(len(recordContent) / 2))[2:].zfill(2) + "#")
        saveObjFile.write(recordContent + "\n")
        recordContent = ""
    if len(recordContent) == 0:
        nextRecordStart = startLoc[curLocCounter]
    recordContent += objectCodes[curObjCounter]
    curObjCounter += 1
saveObjFile.write("T" + hex(nextRecordStart)[2:].zfill(6) + "#")
saveObjFile.write(hex((int)(len(recordContent) / 2))[2:].zfill(2) + "#")
saveObjFile.write(recordContent + "\n")
# modified record
for m in modifiedLoc:
    saveObjFile.write("M" + hex(m)[2:].zfill(6) + "05" + "\n")
saveObjFile.write("E000000")
saveObjFile.close()