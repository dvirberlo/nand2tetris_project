from sre_parse import Tokenizer
from JackTokenizer import Token
from JackTokenizer import JackTokenizer

class CompilationEngine:
    indentS = '  '

    def __init__(self, file) -> None:
        self.file = file
        self.indentC = 0
    
    def write(self, string, indentI= 0) -> None:
        assert type(string) == str, 'writes to file strings only'
        self.file.write(string)
        self.indentI(indentI)
    
    # xml functions:
    def indentI(self, n= 1) -> None:
        self.indentC += n
    def indentD(self, n= 1) -> None:
        self.indentC -= n

    def writeTokenXml(self, token, indentI= 0) -> None:
        assert type(token) == Token, 'token is not a Token'
        self.write(self.indentC * self.indentS + '<'+token.kind+'> ' +self._xmlLang(token.string) +' </'+token.kind+'>\n', indentI)
    
    def writeNonTerminal(self, element, close= False, indentI= 0) -> None:
        assert type(element) == str, 'element parameter should be str'
        self.write(self.indentC * self.indentS + ('</' if close else '<') + element + '>\n', indentI)

    def _xmlLang(self, string) -> str:
        assert type(string) == str, 'string parameter should be str'
        return string.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\'', '&apos;').replace('"', '&quot;')
    

# TODO: think if for example self.classVarDecs(@48) is required
class Class:
    triggers = ['class']
    def __init__(self, tokenizer) -> None:
        assert type(tokenizer) == Tokenizer
        # 'class'
        tokenizer.getToken()
        # className
        self.className = tokenizer.advance().string
        # {
        tokenizer.advance()
        # TODO ? is it by order (= *classVarDec and then *subroutineDec) or not (like right now right now) ?
        self.classVarDecs = []
        while tokenizer.peekNextToken().string in ClassVarDec.triggers:
            self.classVarDecs.append(ClassVarDec())
        
        self.subroutineDecs = []
        while tokenizer.peekNextToken().string in ClassVarDec.triggers:
            self.subroutineDecs.append(SubroutineDec())
        # }
        tokenizer.advance()
class ClassVarDec:
    triggers = ['static', 'field']
    def __init__(self, tokenizer) -> None:
        # in ['static', 'field']
        self.keyword = tokenizer.getToken().string
        # type
        self.varType = tokenizer.advance().string
        # varName + *(, varName)
        self.varNames = [tokenizer.advance().string]
        while tokenizer.peekNextToken().string != ';':
            # ,
            tokenizer.advance()
            # varName
            self.varNames.append(tokenizer.advance().string)
        # ;
        tokenizer.advance()
class SubroutineDec:
    triggers = ['constructor', 'function', 'method']
    def __init__(self, tokenizer) -> None:
        # in ['constructor', 'function', 'method']
        self.keyword = tokenizer.getToken().string
        # 'void' | type
        self.typeName = tokenizer.advance().string
        # subroutineName
        self.subroutineName = tokenizer.advance().string
        # parameterList
        self.parameterList = ParameterList(tokenizer)
        # subroutineBody
        self.subroutineBody = SubRoutineBody(tokenizer)
class ParameterList:
    triggers = ['(']
    def __init__(self, tokenizer) -> None:
        self.parameters = []
        # '('
        tokenizer.advance()
        if tokenizer.peekNextToken().string != ')':
            # parameterType + parameterName
            self.parameters.append([tokenizer.advance().string, tokenizer.advance().string])
        while tokenizer.peekNextToken().string != ')':
            # ,
            tokenizer.advance()
            # parameterType + parameterName
            self.parameters.append([tokenizer.advance().string, tokenizer.advance().string])
        # ')'
        tokenizer.advance()
class SubRoutineBody:
    triggers = ['{']
    def __init__(self, tokenizer) -> None:
         # {
        tokenizer.advance()
        # varDecs
        self.varDecs = []
        while tokenizer.peekNextToken().string in VarDec.triggers:
            self.varDecs.append(VarDec())
        # statements
        self.statements = Statments(tokenizer)
        # }
        tokenizer.advance()
class VarDec:
    triggers = ['var']
    def __init__(self, tokenizer) -> None:
        # 'var'
        tokenizer.advance()
        # type
        self.varType = tokenizer.advance().string
        # varName + *(, varName)
        self.varNames = [tokenizer.advance().string]
        while tokenizer.peekNextToken().string != ';':
            # ,
            tokenizer.advance()
            # varName
            self.varNames.append(tokenizer.advance().string)
        # ;
        tokenizer.advance()

class Statments:
    triggers = ['let', 'if', 'while', 'do', 'return']
    def __init__(self, tokenizer) -> None:
        pass
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
# expression list?
class Op:
    def __init__(self, string) -> None:
        assert string in '+-*/&|<>='
        self.string = string
class UnaryOp:
    def __init__(self, string) -> None:
        assert string in '-~'
        self.string = string
