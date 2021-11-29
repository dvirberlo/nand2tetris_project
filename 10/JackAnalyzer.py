from JackTokenizer import JackTokenizer
from JackTokenizer import Token
from CompilationEngine import CompilationEngine
import os
import sys

class JackAnalyzer:
    ext = '.jack'
    # extP = '.vm'
    extP = 'T.vm.xml'
    version = '0.1'
    name = 'JackAnalyzer'
    boot = ''
    
    def __init__(self) -> None:
        pass
    
    def compile(self, filepath, callback) -> None:
        with open(filepath) as file:
            tokenizer = JackTokenizer(file)
            callback('<tokens>\n')
            indentC = 0
            while tokenizer.hasMoreTokens():
                token = tokenizer.advance()
                callback(self._xml(token, indentC))
            callback('</tokens>\n')
    
    def _xml(self, token, indentC):
        assert type(token) == Token
        indentS = '  '
        return indentC * indentS + '<'+token.kind+'> ' +self._xmlLang(token.string) +' </'+token.kind+'>\n'
    def _xmlLang(self, str):
        return str.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\'', '&apos;').replace('"', '&quot;')


def main(argv):
    trClass = JackAnalyzer
    help = 'Usage:\n' + '  python3 ' + trClass.name + '.py [ ...files| ...dirs] [ -r| --recursive]'
    version = trClass.name + ' v' + trClass.version + ' for ' + trClass.ext +' files (nand2tetris.org)\n' + 'written by @dvirberlo'

    recursiveWarn = 'WARNING: recursive mode is on.'
    forceWarn = 'WARNING: force mode is on.'
    removableArgs = {
        '-r': recursiveWarn, '--recursive':recursiveWarn,
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
        forceSingleMode = True
        forceMultyMode = False
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
    destPath = filepath.replace(trClass.ext, trClass.extP)
    with open(destPath, 'w') as destFile:
        def singleParseCallback(text):
            destFile.write(text)
        print(trClass.name + ' single-mode parse: ' + filepath + ' started... ', end='', flush=True)
        trClass().compile(filepath, singleParseCallback)
        print('done')
        destFile.close()

def multyParse(trClass, dirPath, filenames):
    destPath = os.path.join(dirPath, os.path.basename(os.path.normpath(dirPath)) + trClass.extP)
    with open(destPath, 'w') as destFile:
        translator = trClass()
        destFile.write(translator.boot)
        def multyParseCallback(text):
            destFile.write(text)
        print(trClass.name + ' multy-mode parse: ' + dirPath + ' started... ', flush=True)
        for filename in filenames:
            filePath = os.path.join(dirPath, filename)
            print('+  ' + filename + ' started... ', end='', flush=True)
            translator.compile(filePath, multyParseCallback)
            print('done', flush=True)
        print('done', flush=True)
        destFile.close()

if __name__ == '__main__': main(sys.argv)
