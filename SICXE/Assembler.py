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

    __REGISTERS = {
        'A': 0, 'X': 1, 'L': 2, 'PC': 8, 'SW': 9
        'B': 3, 'S': 4, 'T': 5, 'F': 6,
    }

    def __parse(self, line):
        pass


sys.modules[__name__] = Assembler
