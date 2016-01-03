from SICXE import Assembler
import unittest


class TestAssembler(unittest.TestCase):
    def setUp(self):
        self.asm = Assembler("SICXE.txt")

    def test_read_source(self):
        self.assertIsNotNone(self.asm.source, "Can't read file")
        print("=====Source code=====")
        for i in self.asm.source:
            print("{1}\t{0}\t{2}".format(i['operator'],
                                         i['symbol'] if i['symbol'] else "\t",
                                         i['operand'] if i['operand'] else "\t"))

    def test_load_operators(self):
        load_op = self.asm.load_operators('Operators.dat')
        self.assertIsNotNone(load_op)
        print(load_op)

    def test_append_operator(self):
        add_op = self.asm.append_operator('ADD', '0x18', 3)
        self.assertIsNotNone(add_op)
        print(add_op)

    def test_operator_table(self):
        print("=======OPTAB========")
        for i, val in self.asm.OPTAB.items():
            print(" {:6}\t{:2}\t{:02X}".format(i, val['format'], int(val['opcode'], 16)))

    def test_symbol_table(self):
        self.asm.two_pass()
        print("======SYMTAB======")
        print("{:^8}\t{:^5}".format('"symbol"', '"val"'))
        for i, val in self.asm.SYMTAB.items():
            print(" {:8}\t{:04X}".format(i, val))

if __name__ == "__main__":
    unittest.main()
