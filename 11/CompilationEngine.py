from JackTokenizer import Token
from JackTokenizer import JackTokenizer
from VMWriter import VMWriter
from VMWriter import SymbolTable

class CompilationEngine:
    def __init__(self, file, tokenizer) -> None:
        assert type(tokenizer) is JackTokenizer
        self.tokenizer = JackTokenizer(None) # just for vscode to know it's a JackTokenizer TODO: remove
        self.tokenizer = tokenizer
        self.writer = VMWriter(file)

    def start(self):
        while self.tokenizer.hasMoreTokens():
            if self.tokenizer.peekNextToken().string != 'class':
                return print('ERROR!!!!! non-class root token ['+self.tokenizer.getToken().string+'->'+self.tokenizer.peekNextToken().string+']')
            Class(self.writer, self.tokenizer)


class Class:
    triggers = ['class']
    def __init__(self, writer, tokenizer) -> None:
        assert type(tokenizer) == JackTokenizer
        writer.classScope = SymbolTable()
        # 'class'
        tokenizer.advance()
        # className
        writer.className = tokenizer.advance()
        # {
        tokenizer.advance()
        while tokenizer.peekNextToken().string in ClassVarDec.triggers:
            ClassVarDec(writer, tokenizer)
        
        while tokenizer.peekNextToken().string in SubroutineDec.triggers:
            SubroutineDec(writer, tokenizer)
        # }
        tokenizer.advance()
class ClassVarDec:
    triggers = ['static', 'field']
    def __init__(self, writer, tokenizer) -> None:
        # in ['static', 'field']
        kind = tokenizer.advance().string
        # type
        type = tokenizer.advance().string
        # varName + *(, varName)
        writer.classScope.define(tokenizer.advance().string, type, kind)
        self.varNames = [tokenizer.advance().string]
        while tokenizer.peekNextToken().string != ';':
            # ,
            tokenizer.advance()
            # varName
            writer.classScope.define(tokenizer.advance().string, type, kind)
        # ;
        tokenizer.advance()

        for name in self.varNames:
            writer.classScope.definde(name, self.varType, self.keyword)
class SubroutineDec:
    triggers = ['constructor', 'function', 'method']
    def __init__(self, writer, tokenizer) -> None:
        writer.subroutineScope = SymbolTable()
        # in ['constructor', 'function', 'method' => +1 (for 'this')]
        localsCount = 1 if tokenizer.advance().string == 'method' else 0
        # 'void' | type
        tokenizer.advance().string
        # subroutineName
        name = tokenizer.advance().string
        # parameterList
        for [type, name] in ParameterList(writer, tokenizer).parameters:
            writer.subroutineScope.definde(name, type, 'argument')
        # subroutineBody:
        # {
        tokenizer.advance()
        # varDecs
        self.varDecs = []
        while tokenizer.peekNextToken().string in VarDec.triggers:
            self.varDecs.append(VarDec(writer, tokenizer))
            localsCount += 1
        writer.writeFunction(name, localsCount)
        
        # statements
        self.statements = Statements(writer, tokenizer)
        # }
        tokenizer.advance()
class ParameterList:
    triggers = ['(']
    def __init__(self, writer, tokenizer) -> None:
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
class VarDec:
    triggers = ['var']
    def __init__(self, writer, tokenizer) -> None:
        # 'var'
        tokenizer.advance()
        # type
        type = tokenizer.advance().string
        # varName + *(, varName)
        writer.subroutineScope.definde(tokenizer.advance().string, type, 'local')
        while tokenizer.peekNextToken().string != ';':
            # ,
            tokenizer.advance()
            # varName
            writer.subroutineScope.definde(tokenizer.advance().string, type, 'local')
        # ;
        tokenizer.advance()

class Statements:
    triggers = ['let', 'if', 'while', 'do', 'return']
    def __init__(self, writer, tokenizer) -> None:
        # TODO: make it simpler to read (easy)
        options = [LetStatement, IfStatement, WhileStatement, DoStatement, ReturnStatement]
        self.statements = []
        while tokenizer.peekNextToken().string in self.triggers:
            # print(tokenizer.peekNextToken().string)
            statement = ( options[ self.triggers.index(tokenizer.peekNextToken().string) ] )(writer, tokenizer)
            self.statements.append(statement)
class LetStatement:
    def __init__(self, writer, tokenizer) -> None:
        # 'let'
        tokenizer.advance()
        # varName
        var = writer.getByName(tokenizer.advance().string)
        self.arrExpression = None
        # ? [
        if tokenizer.peekNextToken().string == '[':
            writer.writePush(var["kind"], var["index"])
            tokenizer.advance()
            # expression
            self.arrExpression = Expression(writer, tokenizer)
            # ]
            tokenizer.advance()
            writer.writeArithmetic('add')
            writer.writePop('temp', 0)
        # =
        tokenizer.advance()
        # expression
        self.expression = Expression(writer, tokenizer)
        if self.arrExpression == None:
            writer.writePop(var["kind"], var["index"])
        else:
            writer.writePush('temp', 0)
            writer.writePop('pointer', 1)
            writer.writePop('that', 0)
        # ;
        tokenizer.advance()
class IfStatement:
    def __init__(self, writer, tokenizer) -> None:
        # 'if'
        tokenizer.advance()
        # (
        tokenizer.advance()
        # expression
        Expression(writer, tokenizer)
        # )
        elseLabel = f'el{writer.getUnique()}'
        writer.writeArithmetic('neg')
        writer.writeIfGoto(elseLabel)
        tokenizer.advance()
        # {
        tokenizer.advance()
        # statements
        Statements(writer, tokenizer)
        # }
        tokenizer.advance()
        # ?
        writer.writeLabel(elseLabel)
        if tokenizer.peekNextToken().string == 'else':
            # 'else'
            tokenizer.advance()
            # {
            tokenizer.advance()
            # statememts
            Statements(writer, tokenizer)
            # }
            tokenizer.advance()
class WhileStatement:
    def __init__(self, writer, tokenizer) -> None:
        unique = writer.getUnique()
        doLabel = f'do{unique}'
        whLabel = f'wh{unique}'
        writer.writeLabel(doLabel)
        # 'while'
        tokenizer.advance()
        # (
        tokenizer.advance()
        # expression
        Expression(writer, tokenizer)
        # )
        writer.writeArithmetic('neg')
        writer.writeIfGoto(whLabel)
        tokenizer.advance()
        # {
        tokenizer.advance()
        # statements
        Statements(writer, tokenizer)
        # }
        tokenizer.advance()
        writer.writeLabel(doLabel)
        writer.writeLabel(whLabel)
class DoStatement:
    def __init__(self, writer, tokenizer) -> None:
        # 'do'
        tokenizer.advance()
        # ... (subroutineCall)
        self.subroutineCall = SubroutineCall(writer, tokenizer)
        # ;
        writer.writePop('temp', 0)
        tokenizer.advance()
class ReturnStatement:
    def __init__(self, writer, tokenizer) -> None:
        # 'return'
        tokenizer.advance()
        # ? ! ';'
        self.expression = None
        if tokenizer.peekNextToken().string != ';':
            # expression
            self.expression = Expression(writer, tokenizer)
        else:
            writer.writePush('constant', 0)
        writer.writeReturn()
        # ;
        tokenizer.advance()

class Expression:
    def __init__(self, writer, tokenizer) -> None:
        Term(writer, tokenizer)
        while tokenizer.peekNextToken().string in Op.triggers:
            op = Op(writer, tokenizer)
            Term(writer, tokenizer)
            writer.writeArithmetic(op.vm)
class Term:
    def __init__(self, writer, tokenizer) -> None:
        # uniquely in this method, the tokenizer eats the token imediately. to allow to simply get the token byond this
        # ( in future, might want to make new Tokenizer.peekNextNextToken() )
        token = tokenizer.advance()
        self.mainVal, self.expression, self.subroutineCall, self.unaryOp, self.term = (None,) * 5

        isIntergerConstant = (token.kind == Token.kinds['integerConstant'])
        isStringConstant = (token.kind == Token.kinds['stringConstant'])
        isKeywordConstant = (token.string in KeywordConstant.triggers)
        isSubroutineCall = (token.kind == Token.kinds['identifier'] and tokenizer.peekNextToken().string in SubroutineCall.nextTriggers)
        isVarName = (token.kind == Token.kinds['identifier'] and not isSubroutineCall)
        isAnotherExpression = (token.string == '(')
        isUnaryOp = (token.string in UnaryOp.triggers)
        
        if isIntergerConstant:
            writer.writePush('constant', token.string)
        elif isKeywordConstant:
            if token.string in ['null', 'false']:
                writer.writePush('constant', 0)
            elif token.string == 'false':
                writer.writePush('constant', 1)
                writer.writeArithmetic('neg')
            else:
                # TODO !!!
                pass
        elif isStringConstant:
            string = tokenizer.getToken().string
            writer.writePush('constant', len(string))
            writer.writeCall('String.new', 1)
            for char in string:
                writer.writePush('constant', ord(char))
                writer.writeCall('String.appendChar', 1)
        elif isVarName:
            var = writer.getByName(tokenizer.getToken().string)
            writer.writePush(var["kind"], var["index"])
            if tokenizer.peekNextToken().string == '[':
                # [
                tokenizer.advance()
                Expression(writer, tokenizer)
                writer.writeArithmetic('add')
                writer.writePop('pointer', 1)
                writer.writePush('that', 0)
                # ]
                tokenizer.advance()
        elif isSubroutineCall:
            self.subroutineCall = SubroutineCall(writer, tokenizer, token)
        elif isAnotherExpression:
            # (
            tokenizer.getToken()
            Expression(writer, tokenizer)
            # )
            tokenizer.advance()
        elif isUnaryOp:
            unaryOp = UnaryOp(writer, tokenizer, token)
            Term(writer, tokenizer)
            writer.writeArithmetic(unaryOp.vm)
        else: print("./10/CE.py @Term: no match found")
class SubroutineCall:
    nextTriggers = ["(", "."]
    def __init__(self, writer, tokenizer, currentToken=None) -> None:
        # className | varName
        if currentToken == None: self.mainName = tokenizer.advance().string
        else: self.mainName = tokenizer.getToken().string
        isMethodCall = writer.getByName(self.mainName) != None
        # ?
        self.subroutineName = '.'
        if tokenizer.peekNextToken().string == '.':
            # .
            tokenizer.advance()
            # subroutineName
            self.subroutineName += tokenizer.advance().string
        else:
            self.subroutineName = ''
        # (
        tokenizer.advance()
        # expressionList
        if isMethodCall:
            this = writer.getByName(self.mainName)
            writer.writePop(this["kind"], this["index"])
        self.expressionList = ExpressionList(writer, tokenizer)
        if not isMethodCall:
            writer.writeCall(f'{self.mainName}{self.subroutineName}', self.expressionList.argsCount)
        else:
            writer.writeCall(f'{writer.getByName(self.mainName)["type"]}{self.subroutineName}', self.expressionList.argsCount +1)
        # )
        tokenizer.advance()
class ExpressionList:
    def __init__(self, writer, tokenizer) -> None:
        self.argsCount = 0
        # expression
        if tokenizer.peekNextToken().string != ')':
            Expression(writer, tokenizer)
            self.argsCount += 1
        while tokenizer.peekNextToken().string == ',':
            # ,
            tokenizer.advance()
            # expression
            Expression(writer, tokenizer)
            self.argsCount += 1
class Op:
    triggers = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
    vmLang = ['add', 'sub', 'call Math.multiply 2', 'call Math.divide 2', 'and', 'or', 'lt', 'gt', 'eq']
    def __init__(self, writer, tokenizer) -> None:
        self.vm = self.vmLang[self.triggers.index(tokenizer.advance().string)]
class UnaryOp:
    triggers = ['-', '~']
    def __init__(self, writer, tokenizer, currentToken) -> None:
        self.vm = 'neg'
class KeywordConstant:
    triggers = ['true', 'false', 'null', 'this']
    def __init__(self, writer, tokenizer, currentToken) -> None:
        self.keywordConstant = writer.writeTokenXml(currentToken)
