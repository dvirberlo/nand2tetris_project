import os
import sys
# TODO: readable
class JCompiler:
    ext = '.jack'
    # extP = '.vm'
    extP = 'T.vm.xml'
    version = '0.1'
    name = 'JCompiler'

    stringS = '"'
    symbols = '{[]}().,;+-*/&!|<>='
    keywords = 'class, constructor, function, method, field, static, var, int, char, boolean, void, true, false, null, this, let, do, if, else, while, return'.split(', ')
      
    def __init__(self):
        self.insideComment = False
        self.indentCounter = 0

    def parse(self, filepath, writeCallback):
        filename = os.path.basename(filepath).replace(self.ext, '')
        with open(filepath) as file:
          writeCallback('<tokens>\n')
          for line in file:
              lineCode = self._parseMeaningless(line)
              if line != '':
                  # lineCode = self._parseSyntax( self._parseSyntax(lineCode))
                  lineCode = self._parseTokens(lineCode)
                  writeCallback(lineCode)
          writeCallback('</tokens>\n')

    def _parseMeaningless(self, line):
      multyLineS = '/*'
      multyLineE = '*/'
      singleLineS = '//'
      line = line.replace('\n', '').replace('\t', '')
      if self.insideComment:
        if multyLineE not in line:
          line = ''
        else:
          line = line[line.index(multyLineE)+len(multyLineE):]
      while multyLineS in line:
        if multyLineE in line:
          self.insideComment = False
          line = line[:line.index(multyLineS)] + line[line.index(multyLineE)+len(multyLineE):]
        else:
          self.insideComment = True
          line = line[:line.index(multyLineS)]
      if singleLineS in line: line = line[:line.index('//')]
      while line != '' and line[0] == ' ':
        line = line[1:]
      return line
    
    def _parseTokens(self, line):
      arr = []
      while line != '':
        if line[0] == ' ':
          line = line[1:]
        elif line[0] in self.symbols:
          arr.append(['symbol', line[0]])
          line = line[1:]
        elif line[0] == self.stringS:
          string = line.split(self.stringS)[1]
          arr.append(['stringConstant', string])
          line = line[len(string)+2:]
        else:
          nextword = line.split(' ')[0][:self._firstSymbolIndex(line.split(' ')[0])]
          if nextword.isdigit():
            arr.append(['integerConstant', nextword])
            line = line[len(nextword):]
          elif nextword in self.keywords:
            arr.append(['keyword', nextword])
            line = line[len(nextword):]
          else:
            arr.append(['identifier', nextword])
            line = line[len(nextword):]
      xml = ''
      for ele in arr:
        xml += '<'+ele[0]+'> '+ele[1].replace('<', '&lt;').replace('>', '&gt;')+' </'+ele[0]+'>\n'
      return xml
    def _firstSymbolIndex(self, string):
      index = len(string)
      for symbol in self.symbols:
        if symbol in string and string.index(symbol) < index:
          index = string.index(symbol)
      return index

    def _parseTree(self, arr):
      # TODO
      pass
    



def main(argv):
    trClass = JCompiler
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
