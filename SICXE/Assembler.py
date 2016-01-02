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
        self.__base = None
        self.__program = self.Record()

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

    @property
    def SYMTAB(self):
        return self.__Symbols

    @property
    def OPTAB(self):
        return self.__OPERATORS

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
                self.__begin_loc = int(self.__source[0]['operand'])
                if self.__begin_loc is None:
                    raise TypeError("START takes exactly one argument (0 given)")
                loc_ctr = self.__begin_loc

            for line in self.__source:
                if line['symbol']:
                    symbol = line['symbol']
                    if symbol in self.__Symbols:
                        raise KeyError("Duplicate symbol {}".format(symbol))
                    self.__Symbols[symbol] = loc_ctr
                line['loc'] = loc_ctr

                operator = line['operator']
                if operator in self.__DIRECTIVES:
                    if operator == 'WORD':
                        loc_ctr += 3
                    elif operator == 'RESW':
                        loc_ctr += int(line['operand']) * 3
                    elif operator == 'RESB':
                        loc_ctr += int(line['operand'])
                    elif operator == 'BYTE':
                        loc_ctr += len(self.__constant(line['operand'])) // 2
                    else:
                        pass
                elif operator in self.__OPERATORS:
                    loc_ctr += int(self.__OPERATORS[operator]['format'])
                elif operator[0] == '+' and operator[1:] in self.__OPERATORS:
                    if self.__OPERATORS[operator[1:]]['format'] == 3:
                        loc_ctr += 4
                    else:
                        raise SyntaxError("invalid operator format from {} to 4".format(self.__OPERATORS[operator[1:]]))

        def pass_2():
            self.__title = self.__source[0]['symbol'] if self.__source[0]['operator'] == 'START' else None
            # write header record

            for line in self.__source:
                operator, operand, location = line['operator'], line['operand'], line['loc']
                flag_ni = '11'          # default n=1, i=1
                flag__xbpe = '0000'     # default x, b, p, e = 0, 0 , 0, 0
                if operator in self.__OPERATORS:
                    operand_pair = re.compile("(?P<operand1>\w+)\s*,?\s*(?P<operand2>\w+)?")
                    if self.__OPERATORS[operator]['format'] == 2:
                        operands = operand_pair.match(operand).groups()
                        r1 = operands[0]
                        r2 = operands[1] if len(operands) > 1 else None
                        if r1 in self.__REGISTERS:
                            r1 = "{:X}".format(self.__REGISTERS[r1])
                            r2 = "{:X}".format(self.__REGISTERS[r2]) if r2 in self.__REGISTERS else "0"
                            opvalue = r1 + r2
                        else:
                            raise SyntaxError("no register {}".format(r1))
                    if operand in self.__Symbols or (operand[0]=='@' and operand[1:] in self.__Symbols) or operand[0]=='#':
                        if operand[0] = '@':
                            flag_ni = '10'
                            operand = operand[1:]
                        elif operand[0] = '#':
                            flag_ni = '01'
                            operand = operand[1:]
                        opcode = int(self.__OPERATORS[operator]['opcode'], 16) + int(flag_ni, 2)    # set flag n i
                        opcode = "{:02X}".format(opcode)                                            # transform to hex
                        if re.match("^\d+$", operand):
                            opvalue = "{:04X}".format(int(operand))
                        elif -2048 <= self.__Symbols[operand]-location-self.__OPERATORS[operator]['format'] < 2048:
                            flag__xbpe = "0010"
                            opvalue = "{:04X}".format(self.__Symbols[operand])
                            opvalue[0] = "{:X}".format(int(flag__xbpe, 2))
                        elif self.__base and 0 <= self.__Symbols[operand]-self.__base < 4096:
                            flag__xbpe = "0100"
                            opvalue = "{:04X}".format(self.__Symbols[operand])
                            opvalue[0] = "{:X}".format(int(flag__xbpe, 2))
                        else:
                            raise SyntaxError("need to transform to format 4")

                elif operator in self.__DIRECTIVES:
                    if operator == 'BASE':
                        self.__base = self.__Symbols[operand]
                    elif operator == 'BYTE':
                        opvalue = self.__constant(operand)
                    elif operator == 'END':
                        # write end record
                        pass
                    else:
                        pass
                elif operand[0]=='+' and operator[1:] in self.__Symbols:
                    pass

        pass_1()
        pass_2()

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
            result = rule.match(line)
            if result:
                return result.groupdict()
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
            const = pattern.match(value).groupdict()
        else:
            raise TypeError("invalid format for constant: {}".format(value))
        result = ""
        if const['type'].upper() == 'C':
            for c in const['val']:
                result += "{:02X}".format(ord(c))
        else:
            if len(const['val']) % 2 != 0:
                raise ValueError("invalid constant value length")
            else:
                try:
                    int(const['val'], 16)
                except ValueError:
                    raise ValueError("invalid constant value with base 16: {}".format(const['val']))
                result = const['val'].upper()
        return result

    class Record:
        def __init__(self):
            self.header = ""
            self.end = ""
            self.text = []
            self.modify = []

sys.modules[__name__] = Assembler
