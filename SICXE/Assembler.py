import sys
import re


class Assembler:
    def __init__(self, filename):
        fin = open(filename, 'r', encoding="utf-8-sig")
        if fin:
            self.__source = fin.read().split('\n')
            for i in self.__source:
                if re.match('^\s*$', i):
                    self.__source.remove(i)
        fin.close()

    __REGISTERS = {
        'A': 0, 'X': 1, 'L': 2, 'PC': 8, 'SW': 9,
        'B': 3, 'S': 4, 'T': 5, 'F': 6,
    }

    __DIRECTIVES = [
        "START", "END", "BYTE", "WORD", "RESB", "RESW", "BASE"
    ]

    __OPERATORS = {
        "CLEAR": {'opcode': '0xb4', 'format': 2},
        "COMP": {'opcode': '0x28', 'format': 3},
        "COMPR": {'opcode': '0xa0', 'format': 2},
        "J": {'opcode': '0x3c', 'format': 3},
        "JEQ": {'opcode': '0x30', 'format': 3},
        "JLT": {'opcode': '0x38', 'format': 3},
        "JSUB": {'opcode': '0x48', 'format': 3},
        "LDA": {'opcode': '0x00', 'format': 3},
        "LDB": {'opcode': '0x68', 'format': 3},
        "LDCH": {'opcode': '0x50', 'format': 3},
        "LDT": {'opcode': '0x74', 'format': 3},
        "RD": {'opcode': '0xd8', 'format': 3},
        "RSUB": {'opcode': '0x4c', 'format': 3},
        "STA": {'opcode': '0x0c', 'format': 3},
        "STCH": {'opcode': '0x54', 'format': 3},
        "STL": {'opcode': '0x14', 'format': 3},
        "STX": {'opcode': '0x10', 'format': 3},
        "TD": {'opcode': '0xe0', 'format': 3},
        "TIXR": {'opcode': '0xb8', 'format': 2},
        "WD": {'opcode': '0xdc', 'format': 3}
    }

    def load_operators(self, filename):
        fin = open(filename, 'r', encoding='utf-8-sig')
        op_table = fin.read()
        fin.close()
        op_table = op_table.split('|')
        pattern = re.compile('^\s*((?P<opname>\w+?)\s*)?,\s*((?P<opcode>.+?)\s*)?,\s*((?P<format>\d+?)\s*)?$')
        operators = dict()
        for op in op_table:
            match = pattern.match(op)
            if match:
                if match.group('opname') in operators.keys():
                    raise Exception("Error: Repetitive operator definition.")
                operators[match.group('opname')] = {'opcode': match.group('opcode'), 'format': match.group('format')}
            op_table.remove(op)

        self.__OPERATORS = operators

    def __parse(self, line):
        pass


sys.modules[__name__] = Assembler
