from JackTokenizer import Token

class CompilationEngine:
    indentS = '  '

    def __init__(self, file) -> None:
        self.file = file
        self.indentC = 0
    
    def write(self, string, indentI= 0) -> None:
        assert type(string) == str, 'writes to file strings only'
        self.file.write(string)
        self.indentC += indentI
    
    # xml functions:
    def writeTokenXml(self, token) -> None:
        assert type(token) == Token, 'token is not a Token'
        self.write(self.indentC * self.indentS + '<'+token.kind+'> ' +self._xmlLang(token.string) +' </'+token.kind+'>\n')
    
    def writeNonTerminal(self, element, close= False):
        assert type(element) == str, 'element should be str'
        self.write(self.indentC * self.indentS + ('</' if close else '<') + element + '>\n')
        self.indentC += -1 if close else 1

    def _xmlLang(self, str) -> str:
        return str.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\'', '&apos;').replace('"', '&quot;')
    
    # compile functions:
    def Class(self, close= False) -> None:
        self.writeNonTerminal('class', close)
    
    def classVarDec(self, close= False) -> None:
        self.writeNonTerminal('classVarDec', close)
    
    def SubroutineDec(self, close= False) -> None:
        self.writeNonTerminal('subroutineDec', close)
    
    def ParameterList(self, close= False) -> None:
        self.writeNonTerminal('parameterList', close)
    
    def SubroutineBody(self, close= False) -> None:
        self.writeNonTerminal('subroutineBody', close)
    
    def VarDec(self, close= False) -> None:
        self.writeNonTerminal('varDec', close)
    
    def Statements(self, close= False) -> None:
        self.writeNonTerminal('statements', close)

    def StatementsTypes(self, keyWord, close= False) -> None:
        assert keyWord in ['let', 'do', 'if', 'while', 'return']
        self.writeNonTerminal(keyWord + 'Statement', close)
    
    def ExpressionList(self, close= False) -> None:
        self.writeNonTerminal('expressionList', close)
    
    def Expression(self, close= False) -> None:
        self.writeNonTerminal('expression', close)
    
    def Term(self, close= False) -> None:
        self.writeNonTerminal('term', close)
