from JackTokenizer import Token

class CompilationEngine:
    def __init__(self, file) -> None:
        self.file = file

    def write(self, string) -> None:
        assert type(string) == str, 'writes to file strings only'
        self.file.write(string)
    
    def writeTokenXml(self, token, indentC) -> None:
        assert type(token) == Token, 'token is not a Token'
        indentS = '  '
        self.write(indentC * indentS + '<'+token.kind+'> ' +self._xmlLang(token.string) +' </'+token.kind+'>\n')
    
    def _xmlLang(self, str) -> str:
        return str.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\'', '&apos;').replace('"', '&quot;')
    
    
    def Class(self) -> None:
        pass
    
    def ClassVarDec(self) -> None:
        pass
    
    def SubroutineDec(self) -> None:
        pass
    
    def ParameterList(self) -> None:
        pass
    
    def SubroutineBody(self) -> None:
        pass
    
    def VarDec(self) -> None:
        pass
    
    def Statements(self) -> None:
        pass

    def StatementsTypes(self, keyWord) -> None:
        assert keyWord in ['let', 'do', 'if', 'while', 'return']
        pass
    
    def ExpressionList(self) -> None:
        pass
    
    def Expression(self) -> None:
        pass
    
    def Term(self) -> None:
        pass
