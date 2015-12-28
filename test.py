from SICXE import Assembler
import unittest


class TestAssembler(unittest.TestCase):
    def setUp(self):
        self.asm = Assembler("SICXE.txt")

    """
    def test_read_source(self):
        self.assertIsNotNone(self.asm.source, "Can't read file")
    """

    def test_load_operators(self):
        load_op = self.asm.load_operators('Operators.dat')
        self.assertIsNotNone(load_op)
        print(load_op)

    def test_append_operator(self):
        add_op = self.asm.append_operator('ADD', '0x18', 3)
        self.assertIsNotNone(add_op)
        print(add_op)

if __name__ == "__main__":
    unittest.main()
