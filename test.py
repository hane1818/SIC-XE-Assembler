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
        self.assertIsNotNone(self.asm.load_operators('Operators.dat'))
        print(self.asm.load_operators('Operators.dat'))

if __name__ == "__main__":
    unittest.main()
