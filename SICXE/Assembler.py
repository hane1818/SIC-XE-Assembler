import sys
import re


# noinspection PyMethodMayBeStatic
class Assembler:
    def __init__(self, filename):
        fin = open(filename, 'r', encoding="utf-8-sig")
        if fin:
            self.__source = fin.read().split('\n')
            self.__source = [self.__parse(i) for i in self.__source]
            self.__source = [self.__uppercase(i) for i in self.__source]
            while True:
                try:
                    self.__source.remove(None)
                except ValueError:
                    break
        fin.close()
        self.__Symbols = {}
        self.__begin_loc = 0
        self.__title = None

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

    @property
    def source(self):
        return self.__source

    def append_operator(self, opname, opcode, opformat):
        if opname not in self.__OPERATORS:
            self.__OPERATORS[opname] = {'opcode': opcode, 'format': opformat}
            return {opname: self.__OPERATORS[opname]}
        return dict()

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
                operators[match.group('opname')] = {'opcode': hex(int(match.group('opcode'), 16)),
                                                    'format': int(match.group('format'))}
            op_table.remove(op)

        self.__OPERATORS = operators
        return operators

    def two_pass(self):
        def pass_1():
            loc_ctr = 0

            if self.__source[0]['operator'] == 'START':
                self.__begin_loc = self.__source[0]['operand']
                if not self.__begin_loc:
                    raise TypeError("START takes exactly one argument (0 given)")
                loc_ctr = self.__begin_loc

            for line in self.__source:
                if line['symbol']:
                    symbol = line['symbol']
                    if symbol in self.__Symbols:
                        raise KeyError("Duplicate symbol {}".format(symbol))
                    self.__Symbols[symbol] = loc_ctr

                operator = line['operator']
                if operator in self.__DIRECTIVES:
                    if operator == 'WORD':
                        loc_ctr += 3
                    elif operator == 'RESW':
                        loc_ctr += int(line['operand']) * 3
                    elif operator == 'RESB':
                        loc_ctr += int(line['operand'])
                    elif operator == 'BYTE':
                        pass

    def __parse(self, line):
        def is_comment():
            if re.match('^\s*\..*', line):
                return True
            return False

        def is_code():
            symbol = '^\s*((?P<symbol>\w+)\s+)?'
            operator = '|'.join(list(self.__OPERATORS.keys()) + self.__DIRECTIVES)
            operator = '(?P<operator>\+?({}))'.format(operator)
            operand = '(\s+(?P<operand>(\S+(\s*,\s*\S+)?)))?\s*$'
            rule = re.compile(symbol+operator+operand)
            if rule.match(line):
                return {'symbol': rule.match(line).group('symbol'),
                        'operator': rule.match(line).group('operator'),
                        'operand': rule.match(line).group('operand')}
            return False

        def is_space():
            if re.match('^\s*$', line):
                return True
            return False

        if not is_comment() and is_code() and not is_space():
            return is_code()
        return None

    def __uppercase(self, line):
        if line:
            if line['symbol']:
                line['symbol'] = line['symbol'].upper()
            if line['operator']:
                line['operator'] = line['operator'].upper()
            if line['operand']:
                line['operand'] = line['operand'].upper()
        return line

    def __constant(self, value):
        pattern = re.compile("(?P<type>(C|c|X|x))\s*\'(?P<val>.+)\'")
        if pattern.match(value):
            value = pattern.match(value).groupdict()

sys.modules[__name__] = Assembler
