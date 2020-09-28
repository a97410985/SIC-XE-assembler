from toolkit import *
import unittest


class TestToolkit(unittest.TestCase):
    def test_trim_end_space(self):
        self.assertEqual(trimEndSpace("test    "), "test")
        self.assertEqual(trimEndSpace(" asfd "), " asfd")
        self.assertEqual(trimEndSpace("       aasdf  "), "       aasdf")

    def test_hexToDecimal(self):
        self.assertEqual(hexToDecimal('1a'), 26)
        self.assertEqual(hexToDecimal('B51'), 2897)

    def test_format1(self):
        self.assertTrue(isFormat1("TIO"))
        self.assertTrue(isFormat1("SIO"))
        self.assertTrue(isFormat1("NORM"))
        self.assertFalse(isFormat1("JEQ"))
        self.assertFalse(isFormat1("JGT"))

    def test_format2(self):
        self.assertTrue(isFormat2("ADDR"))
        self.assertTrue(isFormat2("SHIFTL"))
        self.assertTrue(isFormat2("SUBR"))
        self.assertFalse(isFormat2("RSUB"))
        self.assertFalse(isFormat2("STCH"))

    def test_parse_line(self):
        self.assertEqual(parseLine("COPY    START   0"), ("COPY", "START", "0"))
        self.assertEqual(parseLine("        LDB    #LENGTH"), ("", "LDB", "#LENGTH"))
        self.assertEqual(parseLine("        RSUB"), ("", "RSUB", ""))
        self.assertEqual(parseLine("       +LDT    #4096"), ("", "+LDT", "#4096"))
        self.assertEqual(parseLine("        J      @RETADR"), ("", "J", "@RETADR"))
        self.assertEqual(parseLine("        COMPR   A,S"), ("", "COMPR", "A,S"))

    def test_extractLiteral(self):
        self.assertEqual(extractLiteral("=C'FOO'"), ("C", "FOO"))
        self.assertEqual(extractLiteral("=X'123456'"), ("X", "123456"))
        self.assertEqual(extractLiteral("=X'ABCDEF'"), ("X", "ABCDEF"))

    def test_pass1(self):
        self.lines = ['COPY    START   0', 'FIRST   STL     RETADR', '        LDB    #LENGTH', '        BASE    LENGTH',
                      'CLOOP  +JSUB    RDREC', '        LDA     LENGTH', '        COMP   #0', '        JEQ     ENDFIL',
                      '       +JSUB    WRREC', '        J       CLOOP', 'ENDFIL  LDA     EOF', '        STA     BUFFER',
                      '        LDA     #3', '        STA     LENGTH', '       +JSUB    WRREC', '        J      @RETADR',
                      "EOF     BYTE    C'EOF'", 'RETADR  RESW    1', 'LENGTH  RESW    1', 'BUFFER  RESB    4096', '.',
                      '.       Subroutine to read record into buffer', '.', 'RDREC   CLEAR   X', '        CLEAR   A',
                      '        CLEAR   S', '       +LDT    #4096', 'RLOOP   TD      INPUT', '        JEQ     RLOOP',
                      '        RD      INPUT', '        COMPR   A,S', '        JEQ     EXIT',
                      '        STCH    BUFFER,X', '        TIXR    T', '        JLT     RLOOP',
                      'EXIT    STX     LENGTH', '        RSUB', "INPUT   BYTE    X'F1'", '.',
                      '.       Subroutine to write record from buffer', '.', 'WRREC   CLEAR   X',
                      '        LDT     LENGTH', 'WLOOP   TD      OUTPUT', '        JEQ     WLOOP',
                      '        LDCH    BUFFER,X', '        WD      OUTPUT', '        TIXR    T',
                      '        JLT     WLOOP', '        RSUB', "OUTPUT  BYTE    X'05'", '        END     FIRST']
        self.expectSymbolTable = {'FIRST': 0, 'CLOOP': 6, 'ENDFIL': 26, 'EOF': 45, 'RETADR': 48, 'LENGTH': 51,
                                  'BUFFER': 54, 'RDREC': 4150, 'RLOOP': 4160, 'EXIT': 4182, 'INPUT': 4188,
                                  'WRREC': 4189, 'WLOOP': 4194, 'OUTPUT': 4214}
        self.expectEndLoc = [3, 6, 10, 13, 16, 19, 23, 26, 29, 32, 35, 38, 42, 45, 48, 51, 54, 4150, 4152, 4154, 4156,
                             4160, 4163, 4166, 4169, 4171, 4174, 4177, 4179, 4182, 4185, 4188, 4189, 4191, 4194, 4197,
                             4200, 4203, 4206, 4208, 4211, 4214, 4215]
        self.expectProgramLeng = 4215
        self.expectStartAddress = 0
        self.expectedLiteralPool = {}
        (self.symbolTable, self.programLeng, self.endLoc, self.startAddress, self.literalPool,
         self.programBlockStart) = assemble_pass1(
            self.lines)
        self.assertDictEqual(self.symbolTable, self.expectSymbolTable)
        self.assertEqual(self.programLeng, self.expectProgramLeng)
        self.assertListEqual(self.endLoc, self.expectEndLoc)
        self.assertEqual(self.startAddress, self.expectStartAddress)
        self.assertDictEqual(self.literalPool, self.expectedLiteralPool)

    def test_pass2(self):
        lines = ['COPY    START   0', 'FIRST   STL     RETADR', '        LDB    #LENGTH', '        BASE    LENGTH',
                 'CLOOP  +JSUB    RDREC', '        LDA     LENGTH', '        COMP   #0', '        JEQ     ENDFIL',
                 '       +JSUB    WRREC', '        J       CLOOP', 'ENDFIL  LDA     EOF', '        STA     BUFFER',
                 '        LDA     #3', '        STA     LENGTH', '       +JSUB    WRREC', '        J      @RETADR',
                 "EOF     BYTE    C'EOF'", 'RETADR  RESW    1', 'LENGTH  RESW    1', 'BUFFER  RESB    4096', '.',
                 '.       Subroutine to read record into buffer', '.', 'RDREC   CLEAR   X', '        CLEAR   A',
                 '        CLEAR   S', '       +LDT    #4096', 'RLOOP   TD      INPUT', '        JEQ     RLOOP',
                 '        RD      INPUT', '        COMPR   A,S', '        JEQ     EXIT',
                 '        STCH    BUFFER,X', '        TIXR    T', '        JLT     RLOOP',
                 'EXIT    STX     LENGTH', '        RSUB', "INPUT   BYTE    X'F1'", '.',
                 '.       Subroutine to write record from buffer', '.', 'WRREC   CLEAR   X',
                 '        LDT     LENGTH', 'WLOOP   TD      OUTPUT', '        JEQ     WLOOP',
                 '        LDCH    BUFFER,X', '        WD      OUTPUT', '        TIXR    T',
                 '        JLT     WLOOP', '        RSUB', "OUTPUT  BYTE    X'05'", '        END     FIRST']
        symbolTable = {'FIRST': 0, 'CLOOP': 6, 'ENDFIL': 26, 'EOF': 45, 'RETADR': 48, 'LENGTH': 51,
                       'BUFFER': 54, 'RDREC': 4150, 'RLOOP': 4160, 'EXIT': 4182, 'INPUT': 4188,
                       'WRREC': 4189, 'WLOOP': 4194, 'OUTPUT': 4214}
        endLoc = [3, 6, 10, 13, 16, 19, 23, 26, 29, 32, 35, 38, 42, 45, 48, 51, 54, 4150, 4152, 4154, 4156,
                  4160, 4163, 4166, 4169, 4171, 4174, 4177, 4179, 4182, 4185, 4188, 4189, 4191, 4194, 4197,
                  4200, 4203, 4206, 4208, 4211, 4214, 4215]
        expectedObjectCodes = ['17202d', '69202d', '4b101036', '032026', '290000', '332007', '4b10105d', '3f2fec',
                               '032010', '0f2016', '010003', '0f200d', '4b10105d', '3e2003', '454f46', 'b410',
                               'b400',
                               'b440', '75101000', 'e32019', '332ffa', 'db2013', 'a004', '332008', '57c003', 'b850',
                               '3b2fea', '134000', '4f0000', 'F1', 'b410', '774000', 'e32011', '332ffa', '53c003',
                               'df2008', 'b850', '3b2fef', '4f0000', '05']
        expectedModifiedLoc = [7, 20, 39]
        expectedLiteralPool = {}
        programBlockStart = {"default":0}
        (objectCodes, modifiedLoc) = assemble_pass2(lines, symbolTable, endLoc, expectedLiteralPool, programBlockStart)
        self.assertListEqual(objectCodes, expectedObjectCodes)
        self.assertListEqual(modifiedLoc, expectedModifiedLoc)

    # literal test

    def test_pure_literal_pass1(self):
        lines = ['main    START   0', "first   LDA    =C'FOO'", "        LDS    =C'BAR'", "        LDL    =C'FOO'",
                 '        LDA    #100', '        J       next1', '        LTORG', "next1   LDB    =X'123456'",
                 "        LDS    =X'ABCDEF'", "        LDT    =X'123456'", '        LDA    #200', '        LTORG',
                 '        END']
        (self.symbolTable, self.programLeng, self.endLoc, self.startAddress, self.literalPool,self.programBlockStart) = assemble_pass1(
            lines)
        expectedSymbolTable = {'first': 0, 'next1': 21}
        expectedProgramLeng = 39
        expectedEndLoc = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33]
        expectedLiteralPool = {"=C'FOO'": 15, "=C'BAR'": 18, "=X'123456'": 33, "=X'ABCDEF'": 36}
        expectedStartAddress = 0
        self.assertDictEqual(self.symbolTable, expectedSymbolTable)
        self.assertEqual(self.programLeng, expectedProgramLeng)
        self.assertListEqual(self.endLoc, expectedEndLoc)
        self.assertDictEqual(self.literalPool, expectedLiteralPool)

    def test_pure_literal_pass2(self):
        lines = ['main    START   0', "first   LDA    =C'FOO'", "        LDS    =C'BAR'", "        LDL    =C'FOO'",
                 '        LDA    #100', '        J       next1', '        LTORG', "*      =C'FOO'         ",
                 "*      =C'BAR'         ", "next1   LDB    =X'123456'", "        LDS    =X'ABCDEF'",
                 "        LDT    =X'123456'", '        LDA    #200', "*      =X'123456'        ",
                 "*      =X'ABCDEF'        ", '        END']
        symbolTable = {'first': 0, 'next1': 21}
        endLoc = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33]
        literalPool = {"=C'FOO'": 15, "=C'BAR'": 18, "=X'123456'": 33, "=X'ABCDEF'": 36}
        expectedObjectCodes = ['03200c', '6f200c', '0b2006', '010064', '3f2006', '464f4f', '424152', '6b200c', '6f200c',
                               '772006', '0100c8', '123456', 'ABCDEF']
        expectedModifiedLoc = []
        programBlockStart = {"default":0}
        (objectCodes, modifiedLoc) = assemble_pass2(lines, symbolTable, endLoc, literalPool,programBlockStart)
        self.assertEqual(objectCodes, expectedObjectCodes)
        self.assertEqual(modifiedLoc, expectedModifiedLoc)


if __name__ == '__main__':
    unittest.main()
