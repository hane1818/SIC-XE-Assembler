from SICXE import Assembler
import unittest

class TestAssembler(unittest.TestCase):
    def setUp(self):
        self.asm = Assembler("SICXE.txt")

    def test_read_source(self):
        self.assertIsNotNone(self.asm.source, "Can't read file")


if __name__=="__main__":
    unittest.main()
