import sys
import re


class Assembler:
    def __init__(self, filename):
        fin = open(filename, 'r', encoding="utf-8-sig")
        if fin:
            self.__source = fin.read().split('\n')
            self.__source = [self.__parse(i) for i in self.__source]
            self.__source = [uppercase(i) for i in self.__source]
            while True:
                try:
                    self.__source.remove(None)
                except ValueError:
                    break
        fin.close()
        self.__Symbols = {}
        self.__Literals = {}
        self.__begin_loc = 0
        self.__title = None
        self.__base = None
        self.__program = self.Record()

    __REGISTERS = {
        'A': 0, 'X': 1, 'L': 2, 'PC': 8, 'SW': 9,
        'B': 3, 'S': 4, 'T': 5, 'F': 6,
    }

    __DIRECTIVES = [
        "START", "END", "BYTE", "WORD", "RESB", "RESW", "BASE",
        "LTORG", "EQU", "ORG",
        "USE", "EXTDEF", "EXTREF", "CSECT"
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

    @property
    def object_program(self):
        return self.__program

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
            undef_literals = []

            if self.__source[0]['operator'] == 'START':
                self.__begin_loc = int(self.__source[0]['operand'])
                if self.__begin_loc is None:
                    raise TypeError("START takes exactly one argument (0 given)")
                loc_ctr = self.__begin_loc

            for line in self.__source:
                symbol, operator, operand = line['symbol'], line['operator'], line['operand']
                if symbol and symbol != '*':
                    if symbol in self.__Symbols:
                        raise KeyError("Duplicate symbol {}".format(symbol))
                    self.__Symbols[symbol] = loc_ctr
                line['loc'] = loc_ctr

                if operand and re.match('^=\S+$', operand):
                    undef_literals.append(operand)

                if operator in self.__DIRECTIVES:
                    if operator == 'WORD':
                        loc_ctr += 3
                    elif operator == 'RESW':
                        loc_ctr += int(line['operand']) * 3
                    elif operator == 'RESB':
                        loc_ctr += int(line['operand'])
                    elif operator == 'BYTE':
                        loc_ctr += len(constant(line['operand'])) // 2
                    elif operator == 'EQU':
                        if operand == '*':
                            self.__Symbols[symbol] = loc_ctr
                        elif re.match('^\d+$', operand):
                            self.__Symbols[symbol] = int(operand)
                        elif operand in self.__Symbols:
                            self.__Symbols[symbol] = self.__Symbols[operand]
                        elif re.match('\S+\s*-\s*\S+', operand):
                            label1, label2 = re.split('\s*-\s*', operand)
                            if label1 in self.__Symbols and label2 in self.__Symbols and self.__Symbols[label1]-self.__Symbols[label2] >= 0:
                                self.__Symbols[symbol] = self.__Symbols[label1]-self.__Symbols[label2]
                            else:
                                raise TypeError("undefined symbol: {}, {}".format(label1, label2))
                        else:
                            self.__Symbols[symbol] = None
                            raise TypeError("invalid value for EQU: {}".format(operand))
                    elif operator == 'ORG':
                        if re.match('^\d+$', operand):
                            loc_ctr = int(operand)
                        elif operand in self.__Symbols:
                            loc_ctr = self.__Symbols[operand]
                        elif re.match('\S+\s*\+\s*\S', operand):
                            operand1, operand2 = re.split('\s*\+\s*')
                            if operand1 in self.__Symbols:
                                if re.match('^\d+$', operand2):
                                    loc_ctr = self.__Symbols[operand1] + int(operand2)
                                elif operand2 in self.__Symbols:
                                    loc_ctr = self.__Symbols[operand1] + self.__Symbols[operand2]
                                else:
                                    raise TypeError("undefined symbol: {}".format(operand2))
                            else:
                                raise TypeError("undefined symbol: {}".format(operand1))
                        else:
                            raise TypeError("invalid value for ORG: {}".format(operand))
                    elif operator == 'LTORG' or operator == 'END':
                        index = self.__source.index(line)
                        for i, literal in enumerate(undef_literals):
                            self.__source.insert(index+i+1, {'symbol': '*', 'operator': literal, 'operand': None})
                        undef_literals.clear()
                    else:
                        pass
                elif operator in self.__OPERATORS:
                    loc_ctr += int(self.__OPERATORS[operator]['format'])
                elif operator[0] == '+' and operator[1:] in self.__OPERATORS:
                    if self.__OPERATORS[operator[1:]]['format'] == 3:
                        loc_ctr += 4
                    else:
                        raise SyntaxError("invalid operator format from {} to 4".format(self.__OPERATORS[operator[1:]]))
                elif re.match('^=\S+$', operator):
                    self.__Literals[operator] = loc_ctr
                    loc_ctr += len(constant(operator[1:])) // 2

        def pass_2():
            self.__title = self.__source[0]['symbol'] if self.__source[0]['operator'] == 'START' else None
            self.__program.add_header(self.__title, self.__begin_loc)   # write header record

            for line in self.__source:
                operator, operand, location = line['operator'], line['operand'], line['loc']
                flag_ni = '11'          # default n=1, i=1
                flag__xbpe = '0000'     # default x, b, p, e = 0, 0 , 0, 0
                opcode = ""
                opvalue = ""
                if operator in self.__OPERATORS:
                    operand_pair = re.compile("(?P<operand1>\w+)\s*,?\s*(?P<operand2>\w+)?")
                    if self.__OPERATORS[operator]['format'] == 2:
                        flag_ni = '00'
                        operands = operand_pair.match(operand).groups()
                        r1 = operands[0]
                        r2 = operands[1] if len(operands) > 1 else None
                        if r1 in self.__REGISTERS:
                            r1 = "{:X}".format(self.__REGISTERS[r1])
                            r2 = "{:X}".format(self.__REGISTERS[r2]) if r2 in self.__REGISTERS else "0"
                            opvalue = r1 + r2
                        else:
                            raise SyntaxError("no register {}".format(r1))
                    elif operand and (operand in self.__Symbols or (operand[0] == '@' and operand[1:] in self.__Symbols) or operand[0] == '#'):
                        if operand[0] == '@':
                            flag_ni = '10'
                            operand = operand[1:]
                        elif operand[0] == '#':
                            flag_ni = '01'
                            operand = operand[1:]
                        if re.match("^\d+$", operand):
                            opvalue = "{:04X}".format(int(operand))
                        elif -2048 <= self.__Symbols[operand]-location-self.__OPERATORS[operator]['format'] < 2048:
                            flag__xbpe = "0010"
                            opvalue = "{:04X}".format(self.__Symbols[operand]-location-self.__OPERATORS[operator]['format'] & int('ffff', 16))
                            opvalue = "{:X}".format(int(flag__xbpe, 2)) + opvalue[1:]
                        elif self.__base and 0 <= self.__Symbols[operand]-self.__base < 4096:
                            flag__xbpe = "0100"
                            opvalue = "{:04X}".format(self.__Symbols[operand]-self.__base)
                            opvalue = "{:X}".format(int(flag__xbpe, 2)) + opvalue[1:]
                        else:
                            raise SyntaxError("need to transform to format 4")
                    elif operand and operand_pair.match(operand):
                        operand, reg = operand_pair.match(operand).groups()
                        if reg in self.__REGISTERS and reg == 'X':
                            if -2048 <= self.__Symbols[operand]-location-self.__OPERATORS[operator]['format'] < 2048:
                                flag__xbpe = "1010"
                                opvalue = "{:04X}".format(self.__Symbols[operand]-location-self.__OPERATORS[operator]['format'] & int('ffff', 16))
                                opvalue = "{:X}".format(int(flag__xbpe, 2)) + opvalue[1:]
                            elif self.__base and 0 <= self.__Symbols[operand]-self.__base < 4096:
                                flag__xbpe = "1100"
                                opvalue = "{:04X}".format(self.__Symbols[operand]-self.__base)
                                opvalue = "{:X}".format(int(flag__xbpe, 2)) + opvalue[1:]
                            else:
                                raise SyntaxError("need to transform to format 4")
                    else:
                        opvalue = "0000"
                    opcode = int(self.__OPERATORS[operator]['opcode'], 16) + int(flag_ni, 2)    # set flag n i
                    opcode = "{:02X}".format(opcode)                                            # transform to hex
                elif operator in self.__DIRECTIVES:
                    if operator == 'BASE':
                        self.__base = self.__Symbols[operand]
                    elif operator == 'BYTE':
                        opvalue = constant(operand)
                    elif operator == 'END':
                        self.__program.add_end(location)    # write end record
                        break
                    else:
                        pass
                elif operator[0]=='+' and operator[1:] in self.__OPERATORS:
                    flag__xbpe="0001"
                    operator = operator[1:]
                    if operand[0] == '#':
                        flag_ni = "01"
                        operand = operand[1:]
                    opcode = int(self.__OPERATORS[operator]['opcode'], 16) + int(flag_ni, 2)    # set flag n i
                    opcode = "{:02X}".format(opcode)                                            # transform to hex
                    if re.match('^\d+$', operand):
                        opvalue = "{:05X}".format(int(operand))
                    elif operand in self.__Symbols:
                        opvalue = "{:05X}".format(self.__Symbols[operand])
                        self.__program.add_modification(location)
                    else:
                        opvalue = "00000"
                    opvalue = "{:X}".format(int(flag__xbpe, 2)) + opvalue
                if opcode or opvalue:
                    self.__program.add_text(opcode, opvalue, location)    # write text record opcode, opvalue, location

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
            operand = '(\s+(?P<operand>(\S+(\s*\S\s*\S+)?)))?\s*$'
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

    class Record:
        def __init__(self):
            self.header = ""
            self.end = ""
            self.text = []
            self.modification = []
            self.start_loc = None
            self.now_loc = None

        def add_header(self, title, start_loc):
            if not title:
                title = "NONE"
            self.start_loc = start_loc
            self.header = "H{:<6}{:06X}".format(title, start_loc)

        def add_end(self, loc):
            self.end = "E{:06X}".format(self.start_loc)
            self.header += "{:06X}".format(loc-self.start_loc)

        def add_modification(self, loc):
            self.modification.append("M{:06X}05".format(loc+1))

        def add_text(self, opcode, opvalue, loc):
            opcode = "" if not opcode else opcode
            opvalue = "" if not opvalue else opvalue
            object_code = opcode + opvalue
            if not self.text or not self.text[-1] or loc != self.now_loc or len(self.text[-1]) + len(object_code) > 70:
                self.now_loc = loc
                self.text.append("T{:06X}00".format(self.now_loc))

            if object_code != "":
                text_len = int(self.text[-1][7:9], 16) + len(object_code) // 2
                self.text[-1] = self.text[-1][:7] + "{:02X}".format(text_len) + self.text[-1][9:]
                self.text[-1] += object_code
                self.now_loc += len(object_code) // 2

        def __str__(self):
            string = [self.header] + self.text + self.modification + [self.end]
            return '\n'.join(string)


# Helper function (not to be exported)
def constant(value):
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


def uppercase(line):
    if line:
        if line['symbol']:
            line['symbol'] = line['symbol'].upper()
        if line['operator']:
            line['operator'] = line['operator'].upper()
        if line['operand']:
            line['operand'] = line['operand'].upper()
    return line


sys.modules[__name__] = Assembler
