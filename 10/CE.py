from xmlrpc.client import Boolean
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
        assert type(tokenizer) == JackTokenizer
        # 'class'
        tokenizer.advance()
        # className
        self.className = tokenizer.advance().string
        # {
        tokenizer.advance()
        # TODO ? is it by order (= *classVarDec and then *subroutineDec) or not (like right now right now) ?
        self.classVarDecs = []
        while tokenizer.peekNextToken().string in ClassVarDec.triggers:
            self.classVarDecs.append(ClassVarDec(tokenizer))
        
        self.subroutineDecs = []
        while tokenizer.peekNextToken().string in SubroutineDec.triggers:
            self.subroutineDecs.append(SubroutineDec(tokenizer))
        # }
        tokenizer.advance()
class ClassVarDec:
    triggers = ['static', 'field']
    def __init__(self, tokenizer) -> None:
        # in ['static', 'field']
        self.keyword = tokenizer.advance().string
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
        self.keyword = tokenizer.advance().string
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
            self.varDecs.append(VarDec(tokenizer))
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
        # TODO: make it simpler to read (easy)
        options = [LetStatment, IfStatment, WhileStatment, DoStatment, ReturnStatment]
        self.statements = []
        while tokenizer.peekNextToken().string in self.triggers:
            # print(tokenizer.peekNextToken().string)
            statement = ( options[ self.triggers.index(tokenizer.peekNextToken().string) ] )(tokenizer)
            self.statements.append(statement)
class LetStatment:
    def __init__(self, tokenizer) -> None:
        # 'let'
        tokenizer.advance()
        # varName
        self.varName = tokenizer.advance().string
        self.arrExpression = None
        # ? [
        if tokenizer.peekNextToken().string == '[':
            tokenizer.advance()
            # expression
            self.arrExpression = Expression(tokenizer)
            # ]
            tokenizer.advance()
        # =
        tokenizer.advance()
        # expression
        self.expression = Expression(tokenizer)
        # ;
        tokenizer.advance()
class IfStatment:
    def __init__(self, tokenizer) -> None:
        # 'if'
        tokenizer.advance()
        # (
        tokenizer.advance()
        # expression
        self.expression = Expression(tokenizer)
        # )
        tokenizer.advance()
        # {
        tokenizer.advance()
        # statements
        self.ifStatements = Statments(tokenizer)
        # }
        tokenizer.advance()
        # ?
        self.elseStatements = None
        if tokenizer.peekNextToken().string == 'else':
            # 'else'
            tokenizer.advance()
            # {
            tokenizer.advance()
            # statememts
            self.elseStatements = Statments(tokenizer)
            # }
            tokenizer.advance()
class WhileStatment:
    def __init__(self, tokenizer) -> None:
        # 'while'
        tokenizer.advance()
        # (
        tokenizer.advance()
        # expression
        self.expression = Expression(tokenizer)
        # )
        tokenizer.advance()
        # {
        tokenizer.advance()
        # statements
        self.statements = Statments(tokenizer)
        # }
        tokenizer.advance()
class DoStatment:
    def __init__(self, tokenizer) -> None:
        # 'do'
        tokenizer.advance()
        # ... (subroutineCall)
        self.subroutineCall = SubroutineCall(tokenizer)
        # ;
        tokenizer.advance()
class ReturnStatment:
    def __init__(self, tokenizer) -> None:
        # 'return'
        tokenizer.advance()
        # ? ! ';'
        self.expression = None
        if tokenizer.peekNextToken().string != ';':
            # expression
            self.expression = Expression(tokenizer)
        # ;
        tokenizer.advance()
class Expression:
    def __init__(self, tokenizer) -> None:
        self.terms = [Term(tokenizer)]
        self.ops = []
        while tokenizer.peekNextToken().string in Op.triggers:
            self.ops.append(Op(tokenizer))
            self.terms.append(Term(tokenizer))
class Term:
    def __init__(self, tokenizer) -> None:
        # uniquely in this method, the tokenizer eats the token imediately. to allow to simply get the token byond this
        # ( in future, might want to make new Tokenizer.peekNextNextToken() )
        token = tokenizer.advance()
        self.mainVal, self.expression, self.subroutineCall, self.unaryOp = (None,) * 4

        isIntergerConstant = (token.kind == Token.kinds['integerConstant'])
        isStringConstant = (token.kind == Token.kinds['stringConstant'])
        isKeywordConstant = (token.string in KeywordConstant.triggers)
        isSubroutineCall = (token.kind == Token.kinds['identifier'] and tokenizer.peekNextToken().string in SubroutineCall.nextTriggers)
        isVarName = (token.kind == Token.kinds['identifier'] and not isSubroutineCall)
        isAnotherExpression = (token.string == '(')
        isUnaryOp = (token.string in UnaryOp.triggers)
        
        if isIntergerConstant or isStringConstant or isKeywordConstant:
            self.mainVal = tokenizer.getToken()
        elif isVarName:
            self.mainVal = tokenizer.getToken()
            if tokenizer.peekNextToken().string == '[':
                # [
                tokenizer.advance()
                self.expression = Expression(tokenizer)
                # ]
                tokenizer.advance()
        elif isSubroutineCall:
            self.subroutineCall = SubroutineCall(tokenizer, token)
        elif isAnotherExpression:
            # (
            tokenizer.getToken()
            self.expression = Expression(tokenizer)
            # )
            tokenizer.advance()
        elif isUnaryOp:
            self.unaryOp = UnaryOp(tokenizer, token)
            self.expression = Expression(tokenizer)
        else: print("./10/CE.py @Term: no match found")
class SubroutineCall:
    nextTriggers = ["(", "."]
    def __init__(self, tokenizer, currentToken=None) -> None:
        # className | varName
        if currentToken == None: self.mainName = tokenizer.advance().string
        else: self.mainName = tokenizer.getToken().string
        # ?
        self.subroutineName = None
        if tokenizer.peekNextToken().string == '.':
            # .
            tokenizer.advance()
            # subroutineName
            self.subroutineName = tokenizer.advance().string
        # (
        tokenizer.advance()
        # expressionList
        self.expressionList = ExpressionList(tokenizer)
        # )
        tokenizer.advance()

class ExpressionList:
    def __init__(self, tokenizer) -> None:
        self.expressions = []
        # expression
        if tokenizer.peekNextToken().string != ')':
            self.expressions.append(Expression(tokenizer))
        while tokenizer.peekNextToken().string == ',':
            # ,
            tokenizer.advance()
            # expression
            self.expressions.append(Expression(tokenizer))
class Op:
    triggers = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
    def __init__(self, tokenizer) -> None:
        self.op = tokenizer.advance()
class UnaryOp:
    triggers = ['-', '~']
    def __init__(self, tokenizer, currentToken) -> None:
        self.unaryOp = currentToken
class KeywordConstant:
    triggers = ['true', 'false', 'null', 'this']
    def __init__(self, tokenizer, currentToken) -> None:
        self.keywordConstant = currentToken