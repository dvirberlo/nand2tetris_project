from JackTokenizer import JackTokenizer
from JackTokenizer import Token
from CompilationEngine import CompilationEngine
import os
import sys

# TODO: check about statements and expressions (future look into vm code...)
class JackAnalyzer:
    ext = '.jack'
    # extP = '.vm'
    extP = '.vm.xml'
    version = '0.2'
    name = 'JackAnalyzer'
    
    def __init__(self) -> None:
        self.tokenizer = JackTokenizer(None)
        self.compiler = CompilationEngine(None)
    
    def parse(self, filepath, destPath) -> None:
        try:
            file = open(filepath)
            destfile = open(destPath, 'w')
            self.tokenizer = JackTokenizer(file)
            self.compiler = CompilationEngine(destfile)
            self.analyzeTokensUntil()
        except IOError as err:
            print('file IO error')
            raise err
    
    def analyzeTokensUntil(self, quit= lambda: False) -> None:
        while not quit() and self.tokenizer.hasMoreTokens():
            token = self.tokenizer.advance()
            if token.keyWord == 'class':
                self.analyzeClass()
            elif token.keyWord in ['static', 'field']:
                self.analyzeClassVarDec()
            # elif token.keyWord in ['constructor', 'function', 'method']:
            #     self.analyzeSubroutineDec()
            elif token.keyWord == 'var':
                self.analyzeVarDec()
            # elif token.keyWord in ['let', 'if', 'while', 'do', 'return']:
            #     self.analyzeStatementsTypes(token.keyWord)
            # TODO ...
            else:
                print('unsupported token. string: ' + token.string)
                self.compiler.writeTokenXml(self.tokenizer.getToken())
    
    # program structure:
    def analyzeClass(self) -> None:
        # 'class'
        self.tokenizer.getToken()
        # className
        className = self.tokenizer.advance().string
        # {
        self.tokenizer.advance()
        self.compiler.Class(className, False)
        # ...
        # TODO ? is it by order (= *classVarDev and then *subroutineDec) or not (= right now) ?
        self.analyzeTokensUntil(lambda: not self.tokenizer.peekNextToken().string != '}')
        # }
        self.tokenizer.advance()
        self.compiler.Class(className, True)
    def analyzeClassVarDec(self) -> None:
        # in ['static', 'field']
        keyword = self.tokenizer.getToken().string
        # type
        varType = self.tokenizer.advance().string
        # varName + *(, varName)
        varNames = [self.tokenizer.advance().string]
        while self.tokenizer.peekNextToken().string != ';':
            # ,
            self.tokenizer.advance()
            # varName
            varNames.append(self.tokenizer.advance().string)
        # ;
        self.tokenizer.advance()
        self.compiler.classVarDec(keyword, varType, varNames)
    def analyzeSubroutineDec(self) -> None:
        # in ['constructor', 'function', 'method']
        keyword = self.tokenizer.getToken().string
        # 'void' | type
        typeName = self.tokenizer.advance().string
        # subroutineName
        subroutineName = self.tokenizer.advance().string
        # '('
        self.tokenizer.advance()
        # parameterList
        parameters = []
        if self.tokenizer.peekNextToken().string != ')':
            # parameterType + parameterName
            parameters.append([self.tokenizer.advance().string, self.tokenizer.advance().string])
        while self.tokenizer.peekNextToken().string != ')':
            # ,
            self.tokenizer.advance()
            # parameterType + parameterName
            parameters.append([self.tokenizer.advance().string, self.tokenizer.advance().string])
        # ')'
        self.tokenizer.advance()
        self.compiler.SubroutineDec(keyword, typeName, subroutineName, parameters, False)
        # {
        self.tokenizer.advance()
        self.analyzeTokensUntil(lambda: self.tokenizer.peekNextToken().string != 'var')
        # statements
        self.analyzeStatements()
        # }
        self.tokenizer.advance()
        self.compiler.SubroutineDec(keyword, typeName, subroutineName, parameters, True)
    def analyzeVarDec(self) -> None:
        # 'var'
        self.tokenizer.getToken()
        # type
        varType = self.tokenizer.advance().string
        # varName + *(, varName)
        varNames = [self.tokenizer.advance().string]
        while self.tokenizer.peekNextToken().string != ';':
            # ,
            self.tokenizer.advance()
            # varName
            varNames.append(self.tokenizer.advance().string)
        # ;
        self.tokenizer.advance()
        self.compiler.VarDec(varType, varNames)
    
    # statements:
    def analyzeStatements(self) -> None:
        self.compiler.Statements(False)
        self.analyzeTokensUntil(lambda: self.tokenizer.peekNextToken().string not in ['let', 'if', 'while', 'do', 'return'])
        self.compiler.Statements(True)
    def analyzeLetStatement(self) -> None:
        # 'let'
        # varName
        # ? [
            # expression
            # ]
        # =
        # expression
        # ;
        pass
    def analyzeIfStatement(self) -> None:
        # 'if'
        # (
        # expression
        # )
        # {
        # statements
        # }
        # ? 'else'
            # {
            # statememts
            # }
        pass
    def analyzeWhileStatement(self) -> None:
        # 'while'
        # (
        # expression
        # )
        # {
        # statements
        # }
        pass
    def analyzeDoStatement(self) -> None:
        # 'do'
        # ... (subroutineCall)
        # ;
        pass
    def analyzeReturnStatement(self) -> None:
        # 'return'
        # ? ! ';'
            # expression
        # ;
        pass

    # expressions:




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
