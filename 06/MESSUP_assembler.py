# import sys


# class SymbolTable:
#     def __init__(self):
#         self.table = {
#             'R0':0,
#             'R1':1,
#             'R2':2,
#             'R3':3,
#             'R4':4,
#             'R5':5,
#             'R6':6,
#             'R7':7,
#             'R8':8,
#             'R9':9,
#             'R10':10,
#             'R11':11,
#             'R12':12,
#             'R13':13,
#             'R14':14,
#             'R15':15,
#             'SCREEN':16384,
#             'KBD':24576,
#         }
    
#     def parse(self, lines):
#         self.line = 0
#         self.nextEmpty = 16
#         lines = [SymbolTable._lineToTable(self, line) for line in lines]
#         self.line = 0
#         lines = [SymbolTable._lineFromTable(self, line) for line in lines]
#         return lines
#     def _lineToTable(self, line):
#         line = line.replace(' ', '').replace('\r', '')
#         if '//' in line: line = line[:line.index('//')]
#         if '(' in line:
#             self.table.update({ line.replace('(', '').replace(')', ''): self.line })
#             return None
#         if '@' in line and line[1:] not in '0123456789':
#             self.table.update({ line[1:]: self.nextEmpty })
#             self.nextEmpty += 1
#         self.line += 1
#         return line
#     def _lineFromTable(self, line):
#         return line

# class Assembler:
#     def __init__(self, filename):
#         with open(filename) as file:
#             lines = file.readlines()
#             lines = [line.rstrip() for line in lines]
#             tabler = SymbolTable()
#             tabler.parse(lines)
#             print(tabler.table)
#             # print(lines)

#             # if len(line) and line[0] in '@AMD':


# def main(argv):
#     Assembler(argv[1])
# if __name__ == '__main__': main(sys.argv)
