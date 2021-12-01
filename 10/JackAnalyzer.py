from JackTokenizer import JackTokenizer
from JackTokenizer import Token
from CompilationEngine import CompilationEngine
import os
import sys

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
        self.tokenizer.advance()
        # varName
        varName = self.tokenizer.advance()
        arrIndex = self.tokenizer.peekNextToken().string == '['
        arrExpression = None
        # ? [
        if arrIndex:
            self.tokenizer.advance()
            # expression
            arrExpression = self.analyzeExpression()
            # ]
            self.tokenizer.advance()
        # =
        self.tokenizer.advance()
        # expression
        expression = self.analyzeExpression()
        # ;
        self.tokenizer.advance()
        self.compiler.LetStatement(varName, arrIndex, arrExpression, expression)
    def analyzeIfStatement(self) -> None:
        self.compiler.IfStatement(False)
        # 'if'
        self.tokenizer.advance()
        # (
        self.tokenizer.advance()
        # expression
        self.analyzeExpression()
        # )
        self.tokenizer.advance()
        # {
        self.tokenizer.advance()
        # statements
        self.analyzeStatements()
        # }
        self.tokenizer.advance()
        # ? 'else'
        if self.tokenizer.peekNextToken().string == 'else':
            # {
            self.tokenizer.advance()
            # statememts
            self.analyzeStatements()
            # }
            self.tokenizer.advance()
        self.compiler.IfStatement(True)
    def analyzeWhileStatement(self) -> None:
        self.compiler.WhileStatement(False)
        # 'while'
        self.tokenizer.advance()
        # (
        self.tokenizer.advance()
        # expression
        self.analyzeExpression()
        # )
        self.tokenizer.advance()
        # {
        self.tokenizer.advance()
        # statements
        self.analyzeStatements()
        # }
        self.tokenizer.advance()
        self.compiler.WhileStatement(True)
    def analyzeDoStatement(self) -> None:
        self.compiler.DoStatement(False)
        # 'do'
        self.tokenizer.advance()
        # ... (subroutineCall)
        self.analyzeTokensUntil(lambda: self.tokenizer.peekNextToken().string != ';')
        # ;
        self.tokenizer.advance()
        self.compiler.DoStatement(True)
    def analyzeReturnStatement(self) -> None:
        self.compiler.ReturnStatement(False)
        # 'return'
        self.tokenizer.advance()
        # ? ! ';'
        if self.tokenizer.peekNextToken().string != ';':
            # expression
            self.analyzeExpression()
        # ;
        self.tokenizer.advance()
        self.compiler.ReturnStatement(True)

    # expressions:
    def analyzeExpression(self) -> None:
        # TODO
        pass
class Class:
    def __init__(self, className, classVarDecs, subroutineDecs) -> None:
        self.className = className
        self.classVarDecs = classVarDecs
        self.subroutineDecs = subroutineDecs
class ClassVarDec:
    def __init__(self, keyWord, varType, varNames) -> None:
        self.keyWord = keyWord
        self.varType = varType
        self.varNames = varNames
class SubroutineDec:
    def __init__(self, keyWord, routineType, routineName, parameterList, varDecs, statments) -> None:
        self.keyWord = keyWord
        self.routineType = routineType
        self.routineName = routineName
        self.parameterList = parameterList
        self.varDecs = varDecs
        self.statments = statments
class ParameterList:
    def __init__(self, varTypeNames) -> None:
        self.varTypeNames = varTypeNames
class VarDec:
    def __init__(self, varType, varNames) -> None:
        self.varType = varType
        self.varNames = varNames

class Statments:
    def __init__(self, statments) -> None:
        self.statments = statments
class LetStatment:
    def __init__(self, varName, arrIndex, arrExpression, expression) -> None:
        assert type(expression) == Expression
        self.varName = varName
        self.arrIndex = arrIndex
        self.arrExpression = arrExpression
        self.expression = expression
class IfStatment:
    def __init__(self, expression, statments, isElse, elseStatments) -> None:
        assert type(expression) == Expression and type(statments) == Statments
        self.expression = expression
        self.statments = statments
        self.isElse = isElse
        self.elseStatments = elseStatments
class WhileStatment:
    def __init__(self, expression, statments) -> None:
        assert type(expression) == Expression and type(statments) == Statments
        self.expression = expression
        self.statments = statments
class DoStatment:
    def __init__(self, subroutineCall) -> None:
        self.subroutineCall = subroutineCall
class ReturnStatment:
    def __init__(self, isExpression, expression) -> None:
        self.isExpression = isExpression
        self.expression = expression

class Expression:
    def __init__(self, opTerms) -> None:
        self.opTerms = opTerms
class Term:
    def __init__(self, name, kind, bracket, expression, subroutineCall, unaryOp) -> None:
        assert kind in [] or (bracket in [] and type(expression) == Expression) or (type(subroutineCall) == SubroutineCall) or (type(unaryOp) == UnaryOp)
        self.name = name
        self.kind = kind
        self.bracket = bracket
        self.expression = expression
        self.subroutineCall = subroutineCall
        self.unaryOp = unaryOp
class SubroutineCall:
    def __init__(self, name, isDot, subName, parameterList) -> None:
        assert type(parameterList) == ParameterList
        self.name = name
        self.isDot = isDot
        self.subName = subName
        self.parameterList = parameterList
class Op:
    def __init__(self, string) -> None:
        assert string in '+-*/&|<>='
        self.string = string
class UnaryOp:
    def __init__(self, string) -> None:
        assert string in '-~'
        self.string = string



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
