import sys
# TODO: uppercase?, efficient, readable, pong.asm?
class Assembler:
    def __init__(self):
        pass

    def parse(self, filename):
        # .asm -> .hack
        destFile = filename.replace('.asm', '.hack')
        with open(filename) as file:
            lines = self._parseMeaningless(file)
            self._parseSymbols(lines)
            self._parseLang(lines)
            with open(destFile, 'w') as destFile:
                for line in lines:
                    destFile.write(line + '\n')

    def _parseMeaningless(self, file):
        lines = []
        for line in file:
            line = line.replace(' ', '').replace('\t', '').replace('\r', '').replace('\n', '')
            if '//' in line: line = line[:line.index('//')]
            if line != '': lines.append(line)
        return lines
    
    def _parseSymbols(self, lines):
        table = self._symbolTable(lines)
        for i in range(len(lines)):
            if lines[i][0] == '@':
                for name in table:
                    if name == lines[i][1:]: lines[i] = lines[i].replace(name, str(table[name]))
    def _symbolTable(self, lines):
        table = {
            'SP': '0',
            'LCL': '1',
            'ARG': '2',
            'THIS': '3',
            'THAT': '4',

            'R0':0,
            'R1':1,
            'R2':2,
            'R3':3,
            'R4':4,
            'R5':5,
            'R6':6,
            'R7':7,
            'R8':8,
            'R9':9,
            'R10':10,
            'R11':11,
            'R12':12,
            'R13':13,
            'R14':14,
            'R15':15,

            'SCREEN':16384,
            'KBD':24576,
        }
        nextEmpty = 16
        toRemove = []
        lineNum = 0
        # label
        for i in range(len(lines)):
            if lines[i][0] == '(':
                table.update({ lines[i].replace('(', '').replace(')', ''): lineNum })
                toRemove.append(lines[i])
                lineNum -= 1
            lineNum += 1
        for i in toRemove: lines.remove(i)
        # variable
        for i in range(len(lines)):
            if lines[i][0] == '@' and not lines[i][1:].isdigit():
                name = lines[i][1:]
                if name not in table:
                    table.update({ name: nextEmpty })
                    nextEmpty += 1
        return table

    def _parseLang(self, lines):
        for i in range(len(lines)):
            if lines[i][0] == '@':
                # A instruction
                aReg = self._toBinary(int(lines[i][1:]))
                lines[i] = '0' + '0' * (15-len(aReg)) + aReg
            else:
                # C instruction
                dest = ''
                comp = lines[i]
                jump = ''
                if '=' in comp:
                    dest = comp[:comp.index('=')]
                    comp = comp[comp.index('=')+1:]
                if ';' in comp:
                    jump = comp[comp.index(';')+1:]
                    comp = comp[:comp.index(';')]
                lines[i] = '111' + self._langComp(comp) + self._langDest(dest) + self._langJump(jump)
    def _langDest(self, dest):
        destArr = ['A' in dest, 'D' in dest, 'M' in dest]
        return ''.join([self._toBinary(bit) for bit in destArr])
    def _langComp(self, comp):
        aBit = self._toBinary('M' in comp)
        comps = comp.replace('M','A')
        return aBit + {
            '0':   '101010',
            '1':   '111111',
            '+1':  '111111',
            '-1':  '111010',

            'D':   '001100',
            'A':   '110000',

            '!D':  '001101',
            '!A':  '110001',

            '-D':  '001111',
            '-A':  '110011',

            'D+1': '011111',
            '1+D': '011111',
            'A+1': '110111',
            '1+A': '110111',

            'D-1': '001110',
            'A-1': '110010',

            'D+A': '000010',
            'A+D': '000010',

            'D-A': '010011',
            'A-D': '000111',

            'D&A': '000000',
            'A&D': '000000',

            'D|A': '010101',
            'A|D': '010101',
        }[comps]
    def _langJump(self, jump):
        # jump = ''.join[<, 0, >]
        # match jump: ... # python >= 3.10
        return {
            'JMP': '111',
            'JGE': '011',
            'JGT': '001',
            'JNE': '101',
            'JEQ': '010',
            'JLE': '110',
            'JLT': '100',
            ''   : '000',
        }[jump]

    def _toBinary(self, obj):
        return bin(obj)[2:]


def main(argv):
    help = 'Usage: python3 assembler.py ...files'
    version = 'Assember v0.1 for hack language (nand2tetris.org)\n' + 'written by @dvirberlo'
    if len(argv) < 2:
        print(help)
    elif argv[1] == '-h' or argv[1] == '--help':
        print(help)
    elif argv[1] == '-v' or argv[1] == '--version':
        print(version)
    else:
        asm = Assembler()
        for filename in argv[1:]:
            print('Assembler parse: ' + filename + ' started... ', end='', flush=True)
            asm.parse(filename)
            print('done')
if __name__ == '__main__': main(sys.argv)
