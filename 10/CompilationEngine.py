from JackTokenizer import Token

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
    
    # compile functions:
    def Class(self, className, close= False) -> None:
        if not close:
            # class
            self.writeNonTerminal('class', False, 1)
            # 'class'
            self.writeTokenXml(Token('class', Token.kinds['keyword'], Token.keyWords['class']))
            # className
            self.writeTokenXml(Token(className, Token.kinds['identifier']))
            # {
            self.writeTokenXml(Token('{', Token.kinds['symbol']))
        else:
            # }
            self.writeTokenXml(Token('}', Token.kinds['symbol']), -1)
            # /class
            self.writeNonTerminal('class', True)
    
    def classVarDec(self, keyword, varType, varNames) -> None:
        # classVarDec
        self.writeNonTerminal('classVarDec', False, 1)
        # in ['static', 'field']
        self.writeTokenXml(Token(keyword, Token.kinds['keyword'], Token.keyWords[keyword]))
        # type
        self.Type(varType)
        # varName + *(, varName)
        self.writeTokenXml(Token(varNames[0], Token.kinds['identifier']))
        for varName in varNames[1:]:
            # ,
            self.writeTokenXml(Token(',', Token.kinds['symbol']))
            # varName
            self.writeTokenXml(Token(varName, Token.kinds['identifier']))
        # ;
        self.writeTokenXml(Token(';', Token.kinds['symbol']), -1)
        # /classVarDec
        self.writeNonTerminal('classVarDec', True)
    
    def SubroutineDec(self, keyword, typeName, subroutineName, parameters, close= False) -> None:
        if not close:
            # subroutineDec
            self.writeNonTerminal('subroutineDec', False, 1)
            # in ['constructor', 'function', 'method']
            self.writeTokenXml(Token(keyword,  Token.kinds['keyword'], Token.keyWords[keyword]))
            # 'void' | type
            self.Type(typeName)
            # subroutineName
            self.writeTokenXml(Token(subroutineName,  Token.kinds['identifier']))
            # '('
            self.writeTokenXml(Token('(',  Token.kinds['symbol']))
            # parameterList
            self.ParameterList(parameters)
            # ')'
            self.writeTokenXml(Token(')',  Token.kinds['symbol']))
            self.SubroutineBody(False)
        else:
            self.SubroutineBody(True)
            self.writeNonTerminal('subroutineDec', True)
    
    def VarDec(self, varType, varNames) -> None:
        # varDec
        self.writeNonTerminal('varDec', False, 1)
        # in ['static', 'field']
        self.writeTokenXml(Token('var', Token.kinds['keyword'], Token.keyWords['var']))
        # type
        self.Type(varType)
        # varName + *(, varName)
        self.writeTokenXml(Token(varNames[0], Token.kinds['identifier']))
        for varName in varNames[1:]:
            # ,
            self.writeTokenXml(Token(',', Token.kinds['symbol']))
            # varName
            self.writeTokenXml(Token(varName, Token.kinds['identifier']))
        # ;
        self.writeTokenXml(Token(';', Token.kinds['symbol']), -1)
        # /varDec
        self.writeNonTerminal('varDec', True)
    
    def Statements(self, close= False) -> None:
        if not close:
            self.writeNonTerminal('statements', False, 1)
        else:
            self.indentD()
            self.writeNonTerminal('statements', True)
    
    def LetStatement(self, varName) -> None:
        pass
    def IfStatement(self) -> None:
        pass
    def WhileStatement(self) -> None:
        pass
    def DoStatement(self) -> None:
        pass
    def ReturnStatement(self) -> None:
        pass
    
    def ExpressionList(self, expressions) -> None:
        pass
    
    def Expression(self, opTerms) -> None:
        pass
    
    def Term(self, symbol) -> None:
        pass
    
    # compile small functions:
    def Type(self, typeName) -> None:
        if typeName in ['void', 'int', 'char', 'boolean']:
            self.writeTokenXml(Token(typeName, Token.kinds['keyword'], Token.keyWords[typeName]))
        else:
            self.writeTokenXml(Token(typeName, Token.kinds['identifier']))
    
    def ParameterList(self, parameters) -> None:
        self.writeNonTerminal('parameterList', False, 1)
        if parameters != []:
            self.Type(parameters[0][0])
            self.writeTokenXml(Token(parameters[0][1], Token.kinds['identifier']))
        for parameter in parameters[1:]:
            self.writeTokenXml(Token(',', Token.kinds['symbol']))
            self.Type(parameter[0])
            self.writeTokenXml(Token(parameter[1], Token.kinds['identifier']))
        self.indentD()
        self.writeNonTerminal('parameterList', True)
    
    def SubroutineBody(self, close= False) -> None:
        if not close:
            self.writeNonTerminal('subroutineBody', False, 1)
            self.writeTokenXml(Token('{', Token.kinds['symbol']))
        else:
            self.writeTokenXml(Token('}', Token.kinds['symbol']), -1)
            self.writeNonTerminal('subroutineBody', True)

        
