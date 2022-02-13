from JackTokenizer import JackTokenizer
from JackTokenizer import Token
from CompilationEngine import CompilationEngine
import os
import sys

class JackAnalyzer:
    ext = '.jack'
    extP = '.vm'
    version = '1.0'
    name = 'JackAnalyzer'
    
    def __init__(self) -> None:
        self.tokenizer = JackTokenizer(None) # just for vscode to know it's a JackTokenizer TODO: remove
        self.compiler = CompilationEngine(None, self.tokenizer) # just for vscode to know it's a CompilationEngine TODO: remove
    
    def parse(self, filepath, destPath) -> None:
        try:
            file = open(filepath)
            destfile = open(destPath, 'w')
            self.tokenizer = JackTokenizer(file)
            self.compiler = CompilationEngine(destfile, self.tokenizer)
            self.compiler.start()
        except IOError as err:
            print('file IO error')
            raise err


def main(argv) -> None:
    trClass = JackAnalyzer
    help = 'Usage:\n' + '  python3 ' + trClass.name + '.py [ ...files| ...dirs] [ -r| --recursive]'
    version = trClass.name + ' v' + trClass.version + ' for ' + trClass.ext +' files (nand2tetris.org)\n' + 'written by @dvirberlo'
    recursiveWarn = 'WARNING: recursive mode is on.'
    removableArgs = { '-r': recursiveWarn, '--recursive':recursiveWarn }
    args = argv[1:]
    if len(args) == 0 or '-h' in args or '--help' in args:
        print(help)
    elif '-v' in args or '--version' in args:
        print(version)
    else:
        paths = args
        recursive = '-r' in args or '--recursive' in args
        for rmArg in removableArgs:
            if rmArg in paths and removableArgs[rmArg]:
                print(removableArgs[rmArg])
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
                    else:
                        for filename in extFilenames:
                            filePath = os.path.join(dirPath, filename)
                            singleParse(trClass, filePath)
def singleParse(trClass, filepath) -> None:
    destPath = filepath.replace(trClass.ext, trClass.extP)
    print(trClass.name + ' single-mode parse: ' + filepath + ' started... ', end='', flush=True)
    trClass().parse(filepath, destPath)
    print('done')
if __name__ == '__main__': main(sys.argv)
