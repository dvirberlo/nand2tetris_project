import os
import sys
# TODO: remove 'D=A\n' in pops, readable
class VMtranslator:
    ext = '.vm'
    extP = '.asm'
    version = '0.3'
    name = 'VMtranslator'
    boot = '@256\nD=A\n@SP\nM=D\n'

    def __init__(self):
        self.VMcounter = '1'
        self.func = 'boot'
        self.retCouter = 1
        self.boot += self._parseFunc('call Sys.init 0'.split(' '))

    def parse(self, filepath, asmCallback):
        filename = os.path.basename(filepath).replace(self.ext, '')
        with open(filepath) as file:
            for line in file:
                line = self._parseMeaningless(line)
                lineArr = line.split(' ')
                if line != '':
                    asm = ''
                    if lineArr[0] == 'push' or lineArr[0] == 'pop':
                        asm = self._parsePushPop(lineArr, filename)
                    elif lineArr[0] in ['add', 'sub', 'neg', 'eq', 'lt', 'gt', 'and', 'or', 'not']:
                        asm = self._parseAction(line, self.VMcounter)
                    elif lineArr[0] in ['label', 'goto', 'if-goto']:
                        asm = self._parseBranch(lineArr)
                    elif lineArr[0] in ['function', 'return', 'call']:
                        asm = self._parseFunc(lineArr)
                    self.VMcounter = str(int(self.VMcounter) + 1)
                    asm = '//          ' + line + '\n' + asm
                    asmCallback(asm)

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

    def _parseAction(self, action, VMcounter):
        action = action.replace(' ', '')
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
            jump = 'J' + action.upper()
            asm += twoFromStack + 'D=M-D\n' + '@true.'+VMcounter+'\nD;'+jump+'\n@SP\nA=M-1\nM=0\n@false.'+VMcounter+'\n0;JMP\n'
            asm += '(true.'+VMcounter+')\n@SP\nA=M-1\nM=-1\n' + '(false.'+VMcounter+')\n'
        elif action == 'and':
            asm += twoFromStack + 'M=M&D\n'
        elif action == 'or':
            asm += twoFromStack + 'M=M|D\n'
        elif action == 'not':
            asm += oneFromStack + 'M=!M\n'
        return asm

    def _parseBranch(self, lineArr):
        asm = ''
        labelName = self.func + '$' + lineArr[1]
        if lineArr[0] == 'label':
            asm += '(' + labelName + ')\n'
        elif lineArr[0] == 'goto':
            asm += '@' + labelName + '\n' + '0;JMP\n'
        elif lineArr[0] == 'if-goto':
            asm += '@SP\n'+'AM=M-1\n'+'D=M\n@' + labelName + '\n' + 'D;JNE\n'
        return asm

    def _parseFunc(self, lineArr):
        asm = ''
        if lineArr[0] == 'call':
            nArgs = lineArr[2]
            funcName = lineArr[1]
            retName = self.func + '$ret.' + str(self.retCouter)
            self.retCouter += 1
            asm += '@'+retName+'\n'+'D=A\n'+'@SP\n'+'AM=M+1\n'+'A=A-1\n'+'M=D\n'
            for segment in ['LCL', 'ARG', 'THIS', 'THAT']:
                asm += '@'+segment+'\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n'
            asm += '@SP\nD=M\n@LCL\nM=D\n' + '@'+str(5 + int(nArgs))+'\nD=A\n@SP\nD=M-D\n@ARG\nM=D\n' + '@'+funcName+'\n0;JMP\n' + '('+retName+')\n'
        elif lineArr[0] == 'function':
            nLocals = lineArr[2]
            funcName = lineArr[1]
            # asm += '('+funcName+')\n@'+nLocals + '\nD=A\n'+'@SP\n'+'M=M+D\n'
            asm += '('+funcName+')\n' + '@SP\nAM=M+1\nA=A-1\nM=0\n' * int(nLocals)
            self.func = funcName
            self.retCouter = 1
        elif lineArr[0] == 'return':
            asm += '@LCL\nD=M\n@endF\nM=D\n@5\nA=D-A\nD=M\n@retA\nM=D\n@SP\nAM=M-1\nD=M\n@ARG\nA=M\nM=D\n@ARG\nD=M\n@SP\nM=D+1\n'
            for segment in ['THAT', 'THIS', 'ARG', 'LCL']:
                asm += '@endF\nAM=M-1\nD=M\n@'+segment+'\nM=D\n'
            asm += '@retA\nA=M\n0;JMP\n'
        return asm


def main(argv):
    trClass = VMtranslator
    help = 'Usage:\n' + '  python3 ' + trClass.name + '.py [ ...files| ...dirs] [ -r| --recursive]'
    version = trClass.name + ' v' + trClass.version + ' for ' + trClass.ext +' files (nand2tetris.org)\n' + 'written by @dvirberlo'

    recursiveWarn = 'WARNING: recursive mode is on.'
    forceWarn = 'WARNING: force mode is on.'
    removableArgs = {
        '-r': recursiveWarn, '--recursive':recursiveWarn,
        '-fsm': forceWarn, '--force-single-mode': forceWarn,
        '-fmm': forceWarn, '--force-multy-mode': forceWarn,
    }
    args = argv[1:]
    if len(args) == 0:
        print(help + '\n\n' + version)
    elif '-h' in args or '--help' in args:
        print(help)
    elif '-v' in args or '--version' in args:
        print(version)
    else:
        paths = args
        recursive = '-r' in args or '--recursive' in args
        forceSingleMode = '-fsm' in args or '--force-single-mode' in args
        forceMultyMode = '-fmm' in args or '--force-multy-mode' in args
        for rmArg in removableArgs:
            if rmArg in paths:
                if removableArgs[rmArg]: print(removableArgs[rmArg])
                paths.remove(rmArg)
            while rmArg in paths:
                paths.remove(rmArg)
        
        if recursive and len(paths) == 0:
            paths = ['.']

        for path in paths:
            if os.path.isfile(path):
                singleParse(trClass, path)
            else:
                for (dirPath, dirnames, filenames) in os.walk(path):
                    extFilenames = [filename for filename in filenames if trClass.ext in filename]
                    if len(extFilenames) == 0:
                        print(trClass.name + ' skipped: ' + dirPath , flush=True)
                    elif not forceMultyMode and (forceSingleMode or len(extFilenames) < 2):
                        for filename in extFilenames:
                            filePath = os.path.join(dirPath, filename)
                            singleParse(trClass, filePath)
                    else:
                        multyParse(trClass, dirPath, extFilenames)

def singleParse(trClass, filepath):
    asmPath = filepath.replace(trClass.ext, trClass.extP)
    with open(asmPath, 'w') as asmFile:
        def singleParseCallback(asm):
            asmFile.write(asm)
        print(trClass.name + ' single-mode parse: ' + filepath + ' started... ', end='', flush=True)
        trClass().parse(filepath, singleParseCallback)
        print('done')

def multyParse(trClass, dirPath, filenames):
    asmPath = os.path.join(dirPath, os.path.basename(os.path.normpath(dirPath)) + trClass.extP)
    with open(asmPath, 'w') as asmFile:
        translator = trClass()
        asmFile.write(translator.boot)
        def multyParseCallback(asm):
            asmFile.write(asm)
        print(trClass.name + ' multy-mode parse: ' + dirPath + ' started... ', flush=True)
        for filename in filenames:
            filePath = os.path.join(dirPath, filename)
            print('+  ' + filename + ' started... ', end='', flush=True)
            translator.parse(filePath, multyParseCallback)
            print('done', flush=True)
        print('done', flush=True)

if __name__ == '__main__': main(sys.argv)
