import os
import sys
# TODO: remove 'D=A\n' in pops, readable
class VMtranslator:
    def __init__(self):
        self.falseLine, self.trueLine = '2', '8'
        self.trueFalseAsm = '@14\n0;JMP\n'
        self.trueFalseAsm += '@SP\n'+'A=M-1\n'+'M=0\n'+'@R13\n'+'A=M\n'+'0;JMP\n'
        self.trueFalseAsm += '@SP\n'+'A=M-1\n'+'M=-1\n'+'@R13\n'+'A=M\n'+'0;JMP\n'
        self.staringLine = 13

    def parse(self, filepath):
        # .vm -> .asm
        filename = os.path.basename(filepath).replace('.vm', '')
        destFile = filepath.replace('.vm', '.asm')
        with open(filepath) as file:
            with open(destFile, 'w') as destFile:   
                destFile.write(self.trueFalseAsm)
                lineNum = self.staringLine
                for line in file:
                    line = self._parseMeaningless(line)
                    lineArr = line.split(' ')
                    asm = ''
                    if len(lineArr) == 1:
                        asm = self._parseAction(line, lineNum)
                    elif lineArr[0] == 'push' or lineArr[0] == 'pop':
                        asm = self._parsePushPop(lineArr, filename)
                    lineNum += asm.count('\n')
                    if line != '':
                        asm = '//          ' + line + '\n' + asm
                        destFile.write(asm)

    def _parseMeaningless(self, line):
        if '//' in line: line = line[:line.index('//')]
        return line.replace('\n', '')

    def _parsePushPop(self, lineArr, filename):
        [segmentEnd, stack] = {
            'push': [
                'D=M\n',
                '@SP\n'+'AM=M+1\n'+'A=A-1\n'+'M=D\n',
            ],'pop':[
                'D=A\n'+'@R13\n'+'M=D\n',
                '@SP\n'+'AM=M-1\n'+'D=M\n'+'@R13\n'+'A=M\n'+'M=D\n',
            ],
        }[lineArr[0]]
        asm = ''
        segment = lineArr[1]
        counter = lineArr[2]
        # push:       get D, move & SP++ # pop: SP-- & get D, move,
        if segment == 'constant': # (push only)
            asm += '@'+counter+'\n' + 'D=A\n'
        elif segment in ['local', 'argument', 'this', 'that']:
            asm += '@' + {
                'local':    'LCL',
                'argument': 'ARG',
                'this':     'THIS',
                'that':     'THAT'
            }[segment] + '\n' + 'A=M\n'
            if counter == '1':
                asm += 'A=A+1\n'
            elif counter != '0':
                asm += 'D=A\n' + '@'+counter+'\n' + 'A=A+D\n' 
            asm += segmentEnd
        elif segment == 'static':
            asm += '@' + filename + '.' + counter + '\n' + segmentEnd
        elif segment == 'temp':
            asm += '@'+ str(int(counter)+5) + '\n' + segmentEnd
        elif segment == 'pointer':
            asm += '@'+ ['THIS','THAT'][int(counter)] + '\n' + segmentEnd
        return asm + stack

    def _parseAction(self, action, lineNum):
        oneFromStack = '@SP\n'+'A=M-1\n'
        twoFromStack = '@SP\n'+'AM=M-1\n' + 'D=M\n'+'A=A-1\n'
        asm = ''
        if action == 'add':
            asm += twoFromStack + 'M=M+D\n'
        elif action == 'sub':
            asm += twoFromStack + 'M=M-D\n'
        elif action == 'neg':
            asm += oneFromStack + 'M=-M\n'
        elif action in ['eq', 'lt', 'gt']:
            opLines = 14
            jump = 'J' + action.upper()
            asm += '@'+str(lineNum+opLines)+'\nD=A\n'+'@R13\n'+'M=D\n' + twoFromStack
            asm += 'D=M-D\n' + '@'+self.trueLine+'\nD;'+jump+'\n@'+self.falseLine+'\n0;JMP\n'
        elif action == 'and':
            asm += twoFromStack + 'M=M&D\n'
        elif action == 'or':
            asm += twoFromStack + 'M=M|D\n'
        elif action == 'not':
            asm += oneFromStack + 'M=!M\n'
        return asm


def main(argv):
    ext = '.vm'
    help = 'Usage:\n' + '  python3 VMtranslator.py ...files\n' + '  python3 VMtranslator.py [ --dir| --dir-r]'
    version = 'VMtranslator v0.2 for VM language (nand2tetris.org)\n' + 'written by @dvirberlo'
    if len(argv) < 2:
        print(help)
    elif argv[1] == '-h' or argv[1] == '--help':
        print(help)
    elif argv[1] == '-v' or argv[1] == '--version':
        print(version)
    elif argv[1] == '--dir' or argv[1] == '--dir-r':
        recursive = argv[1] == '--dir-r'
        filepaths = []
        for (dirpath, dirnames, filenames) in os.walk('.'):
            for file in filenames:
                if ext in file:
                    filepaths.append(os.path.join(dirpath, file))
            if not recursive:
                break
        mainLoop(filepaths)
    else:
        mainLoop(argv[1:])

def mainLoop(filepaths):
    vmt = VMtranslator()
    for filepath in filepaths:
        print('VMtranslator parse: ' + filepath + ' started... ', end='', flush=True)
        vmt.parse(filepath)
        print('done')

if __name__ == '__main__': main(sys.argv)
