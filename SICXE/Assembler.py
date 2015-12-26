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

    def __parse(self, line):
        pass


sys.modules[__name__] = Assembler
