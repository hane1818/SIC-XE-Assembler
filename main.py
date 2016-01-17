import sys
from SICXE import Assembler

if __name__ == '__main__':
    try:
        file = sys.argv[1]
    except IndexError:
        file = input("Please input a full file name...>")

    while not file:
        print("You don't input a file.")
        file = input("Please input again...>")

    asm = Assembler().load_file(file)
    print("\n=======OPTAB========\n")
    for i, val in asm.OPTAB.items():
        print(" {:6}\t{:2}\t{:02X}".format(i, val['format'], int(val['opcode'], 16)))

    asm.pass_one()
    print("\n======SYMTAB======\n")
    print("{:^8}\t{:^5}".format('"symbol"', '"val"'))
    for i, val in asm.SYMTAB.items():
        print(" {:8}\t{:04X}".format(i, val))
    if asm.LITERAL:
        print("\n=======LITERALS========\n")
        for i, val in asm.LITERAL.items():
            print(" {:7}\t{:04X}".format(i, val))

    asm.pass_two()
    print("\n======Object Program=====\n")
    print(asm.object_program)
