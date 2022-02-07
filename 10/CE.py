from JackTokenizer import Token
from JackTokenizer import JackTokenizer

class XMLWriter:
    indentStr = '  '

    def __init__(self, file) -> None:
        self.file = file
        self.indentCounter = 0
    def write(self, string) -> None:
        assert type(string) == str, 'writes to file strings only'
        self.file.write(string)
    
    # xml functions:
    def indentI(self, n= 1) -> None:
        self.indentCounter += n

    def writeTokenXml(self, token, icnIndent= 0) -> Token:
        assert type(token) == Token, 'token is not a Token'
        self.write(self.indentCounter * self.indentStr + '<'+token.kind+'> ' +self._xmlLang(token.string) +' </'+token.kind+'>\n')
        self.indentI(icnIndent)
        return token
    
    def writeNonTerminal(self, element, close= False, icnIndent= 1) -> str:
        assert type(element) == str, 'element parameter should be str'
        if close: self.indentI(icnIndent * -1)
        self.write(self.indentCounter * self.indentStr + ('</' if close else '<') + element + '>\n')
        if not close: self.indentI(icnIndent)
        return element

    def _xmlLang(self, string) -> str:
        assert type(string) == str, 'string parameter should be str'
        return string.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\'', '&apos;').replace('"', '&quot;')

# I m lazy, so i just throw this writer as global var
writer = XMLWriter(None) # just for vscode to know it's a XMLWriter TODO: remove

class CompilationEngine:
    def __init__(self, file, tokenizer) -> None:
        assert type(tokenizer) is JackTokenizer
        self.tokenizer = JackTokenizer(None) # just for vscode to know it's a JackTokenizer TODO: remove
        self.tokenizer = tokenizer
        global writer
        writer = XMLWriter(file)

    def start(self):
        while self.tokenizer.hasMoreTokens():
            if self.tokenizer.peekNextToken().string != 'class':
                return print('ERROR!!!!! non-class root token ['+self.tokenizer.getToken().string+'->'+self.tokenizer.peekNextToken().string+']')
            Class(self.tokenizer)


# TODO: think if for example self.classVarDecs(@48) is required
class Class:
    triggers = ['class']
    def __init__(self, tokenizer) -> None:
        assert type(tokenizer) == JackTokenizer
        # 'class'
        writer.writeNonTerminal('class')
        writer.writeTokenXml(tokenizer.advance())
        # className
        self.className = writer.writeTokenXml(tokenizer.advance()).string
        # {
        writer.writeTokenXml(tokenizer.advance())
        # TODO ? is it by order (= *classVarDec and then *subroutineDec) or not (like right now right now) ?
        self.classVarDecs = []
        while tokenizer.peekNextToken().string in ClassVarDec.triggers:
            self.classVarDecs.append(ClassVarDec(tokenizer))
        
        self.subroutineDecs = []
        while tokenizer.peekNextToken().string in SubroutineDec.triggers:
            self.subroutineDecs.append(SubroutineDec(tokenizer))
        # }
        writer.writeTokenXml(tokenizer.advance())
        writer.writeNonTerminal('class', True)
class ClassVarDec:
    triggers = ['static', 'field']
    def __init__(self, tokenizer) -> None:
        writer.writeNonTerminal('classVarDec')
        # in ['static', 'field']
        self.keyword = writer.writeTokenXml(tokenizer.advance()).string
        # type
        self.varType = writer.writeTokenXml(tokenizer.advance()).string
        # varName + *(, varName)
        self.varNames = [writer.writeTokenXml(tokenizer.advance()).string]
        while tokenizer.peekNextToken().string != ';':
            # ,
            writer.writeTokenXml(tokenizer.advance())
            # varName
            self.varNames.append(writer.writeTokenXml(tokenizer.advance()).string)
        # ;
        writer.writeTokenXml(tokenizer.advance())
        writer.writeNonTerminal('classVarDec', True)
class SubroutineDec:
    triggers = ['constructor', 'function', 'method']
    def __init__(self, tokenizer) -> None:
        writer.writeNonTerminal('subroutineDec')
        # in ['constructor', 'function', 'method']
        self.keyword = writer.writeTokenXml(tokenizer.advance()).string
        # 'void' | type
        self.typeName = writer.writeTokenXml(tokenizer.advance()).string
        # subroutineName
        self.subroutineName = writer.writeTokenXml(tokenizer.advance()).string
        # parameterList
        self.parameterList = ParameterList(tokenizer)
        # subroutineBody
        self.subroutineBody = SubRoutineBody(tokenizer)
        writer.writeNonTerminal('subroutineDec', True)
class ParameterList:
    triggers = ['(']
    def __init__(self, tokenizer) -> None:
        self.parameters = []
        # '('
        writer.writeTokenXml(tokenizer.advance())
        writer.writeNonTerminal('parameterList')
        if tokenizer.peekNextToken().string != ')':
            # parameterType + parameterName
            self.parameters.append([writer.writeTokenXml(tokenizer.advance()).string, writer.writeTokenXml(tokenizer.advance()).string])
        while tokenizer.peekNextToken().string != ')':
            # ,
            writer.writeTokenXml(tokenizer.advance())
            # parameterType + parameterName
            self.parameters.append([writer.writeTokenXml(tokenizer.advance()).string, writer.writeTokenXml(tokenizer.advance()).string])
        writer.writeNonTerminal('parameterList', True)
        # ')'
        writer.writeTokenXml(tokenizer.advance())
class SubRoutineBody:
    triggers = ['{']
    def __init__(self, tokenizer) -> None:
        writer.writeNonTerminal('subroutineBody')
         # {
        writer.writeTokenXml(tokenizer.advance())
        # varDecs
        self.varDecs = []
        while tokenizer.peekNextToken().string in VarDec.triggers:
            self.varDecs.append(VarDec(tokenizer))
        # statements
        self.statements = Statements(tokenizer)
        # }
        writer.writeTokenXml(tokenizer.advance())
        writer.writeNonTerminal('subroutineBody', True)
class VarDec:
    triggers = ['var']
    def __init__(self, tokenizer) -> None:
        writer.writeNonTerminal('varDec')
        # 'var'
        writer.writeTokenXml(tokenizer.advance())
        # type
        self.varType = writer.writeTokenXml(tokenizer.advance()).string
        # varName + *(, varName)
        self.varNames = [writer.writeTokenXml(tokenizer.advance()).string]
        while tokenizer.peekNextToken().string != ';':
            # ,
            writer.writeTokenXml(tokenizer.advance())
            # varName
            self.varNames.append(writer.writeTokenXml(tokenizer.advance()).string)
        # ;
        writer.writeTokenXml(tokenizer.advance())
        writer.writeNonTerminal('varDec', True)

class Statements:
    triggers = ['let', 'if', 'while', 'do', 'return']
    def __init__(self, tokenizer) -> None:
        writer.writeNonTerminal('statements')
        # TODO: make it simpler to read (easy)
        options = [LetStatement, IfStatement, WhileStatement, DoStatement, ReturnStatement]
        self.statements = []
        while tokenizer.peekNextToken().string in self.triggers:
            # print(tokenizer.peekNextToken().string)
            statement = ( options[ self.triggers.index(tokenizer.peekNextToken().string) ] )(tokenizer)
            self.statements.append(statement)
        writer.writeNonTerminal('statements', True)
class LetStatement:
    def __init__(self, tokenizer) -> None:
        writer.writeNonTerminal('letStatement')
        # 'let'
        writer.writeTokenXml(tokenizer.advance())
        # varName
        self.varName = writer.writeTokenXml(tokenizer.advance()).string
        self.arrExpression = None
        # ? [
        if tokenizer.peekNextToken().string == '[':
            writer.writeTokenXml(tokenizer.advance())
            # expression
            self.arrExpression = Expression(tokenizer)
            # ]
            writer.writeTokenXml(tokenizer.advance())
        # =
        writer.writeTokenXml(tokenizer.advance())
        # expression
        self.expression = Expression(tokenizer)
        # ;
        writer.writeTokenXml(tokenizer.advance())
        writer.writeNonTerminal('letStatement', True)
class IfStatement:
    def __init__(self, tokenizer) -> None:
        writer.writeNonTerminal('ifStatement')
        # 'if'
        writer.writeTokenXml(tokenizer.advance())
        # (
        writer.writeTokenXml(tokenizer.advance())
        # expression
        self.expression = Expression(tokenizer)
        # )
        writer.writeTokenXml(tokenizer.advance())
        # {
        writer.writeTokenXml(tokenizer.advance())
        # statements
        self.ifStatements = Statements(tokenizer)
        # }
        writer.writeTokenXml(tokenizer.advance())
        # ?
        self.elseStatements = None
        if tokenizer.peekNextToken().string == 'else':
            # 'else'
            writer.writeTokenXml(tokenizer.advance())
            # {
            writer.writeTokenXml(tokenizer.advance())
            # statememts
            self.elseStatements = Statements(tokenizer)
            # }
            writer.writeTokenXml(tokenizer.advance())
        writer.writeNonTerminal('ifStatement', True)
class WhileStatement:
    def __init__(self, tokenizer) -> None:
        writer.writeNonTerminal('whileStatement')
        # 'while'
        writer.writeTokenXml(tokenizer.advance())
        # (
        writer.writeTokenXml(tokenizer.advance())
        # expression
        self.expression = Expression(tokenizer)
        # )
        writer.writeTokenXml(tokenizer.advance())
        # {
        writer.writeTokenXml(tokenizer.advance())
        # statements
        self.statements = Statements(tokenizer)
        # }
        writer.writeTokenXml(tokenizer.advance())
        writer.writeNonTerminal('whileStatement', True)
class DoStatement:
    def __init__(self, tokenizer) -> None:
        writer.writeNonTerminal('doStatement')
        # 'do'
        writer.writeTokenXml(tokenizer.advance())
        # ... (subroutineCall)
        self.subroutineCall = SubroutineCall(tokenizer)
        # ;
        writer.writeTokenXml(tokenizer.advance())
        writer.writeNonTerminal('doStatement', True)
class ReturnStatement:
    def __init__(self, tokenizer) -> None:
        writer.writeNonTerminal('returnStatement')
        # 'return'
        writer.writeTokenXml(tokenizer.advance())
        # ? ! ';'
        self.expression = None
        if tokenizer.peekNextToken().string != ';':
            # expression
            self.expression = Expression(tokenizer)
        # ;
        writer.writeTokenXml(tokenizer.advance())
        writer.writeNonTerminal('returnStatement', True)
class Expression:
    def __init__(self, tokenizer) -> None:
        writer.writeNonTerminal('expression')
        self.terms = [Term(tokenizer)]
        self.ops = []
        while tokenizer.peekNextToken().string in Op.triggers:
            self.ops.append(Op(tokenizer))
            self.terms.append(Term(tokenizer))
        writer.writeNonTerminal('expression', True)
class Term:
    def __init__(self, tokenizer) -> None:
        writer.writeNonTerminal('term')
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
            self.mainVal = writer.writeTokenXml(tokenizer.getToken())
        elif isVarName:
            self.mainVal = writer.writeTokenXml(tokenizer.getToken())
            if tokenizer.peekNextToken().string == '[':
                # [
                writer.writeTokenXml(tokenizer.advance())
                self.expression = Expression(tokenizer)
                # ]
                writer.writeTokenXml(tokenizer.advance())
        elif isSubroutineCall:
            self.subroutineCall = SubroutineCall(tokenizer, token)
        elif isAnotherExpression:
            # (
            writer.writeTokenXml(tokenizer.getToken())
            self.expression = Expression(tokenizer)
            # )
            writer.writeTokenXml(tokenizer.advance())
        elif isUnaryOp:
            self.unaryOp = UnaryOp(tokenizer, token)
            self.expression = Expression(tokenizer)
        else: print("./10/CE.py @Term: no match found")
        writer.writeNonTerminal('term', True)
class SubroutineCall:
    nextTriggers = ["(", "."]
    def __init__(self, tokenizer, currentToken=None) -> None:
        writer.writeNonTerminal('subroutineCall')
        # className | varName
        if currentToken == None: self.mainName = writer.writeTokenXml(tokenizer.advance()).string
        else: self.mainName = writer.writeTokenXml(tokenizer.getToken()).string
        # ?
        self.subroutineName = None
        if tokenizer.peekNextToken().string == '.':
            # .
            writer.writeTokenXml(tokenizer.advance())
            # subroutineName
            self.subroutineName = writer.writeTokenXml(tokenizer.advance()).string
        # (
        writer.writeTokenXml(tokenizer.advance())
        # expressionList
        self.expressionList = ExpressionList(tokenizer)
        # )
        writer.writeTokenXml(tokenizer.advance())
        writer.writeNonTerminal('subroutineCall', True)

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
