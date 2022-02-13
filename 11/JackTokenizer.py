class Token:
    keyWords = {'class': 'class', 'constructor': 'constructor', 'function': 'function', 'method': 'method', 'field': 'field', 'static': 'static', 'var': 'var', 'int': 'int', 'char': 'char', 'boolean': 'boolean', 'void': 'void', 'true': 'true', 'false': 'false', 'null': 'null', 'this': 'this', 'let': 'let', 'do': 'do', 'if': 'if', 'else': 'else', 'while': 'while', 'return': 'return'}
    kinds = {'symbol': 'symbol', 'stringConstant': 'stringConstant', 'integerConstant': 'integerConstant', 'keyword': 'keyword', 'identifier': 'identifier'}
    
    def __init__(self, string, kind, keyWord= None) -> None:
        assert kind == None or kind in self.kinds
        # assert kind in self.kinds
        assert keyWord == None or keyWord in self.keyWords

        self.string = string
        self.kind = kind
        self.keyWord = keyWord

class JackTokenizer:
    symbols = '{[]}().,;+-*/&!|<>=~'
    keywords = 'class, constructor, function, method, field, static, var, int, char, boolean, void, true, false, null, this, let, do, if, else, while, return'.split(', ')
    stringS = '"'

    def __init__(self, file) -> None:
        self.insideComment = False
        self.currentToken = None
        self.lastToken = None
        self.file = file
        self.line = ''
    
    def hasMoreTokens(self) -> bool:
        result = self._getNextToken(False) != None
        return result
    
    def advance(self) -> Token:
        assert self.hasMoreTokens(), 'no tokens left'
        self.lastToken = self.currentToken
        self.currentToken = self._getNextToken()
        return self.currentToken

    def getToken(self) -> Token:
        return self.currentToken
    
    def getLastToken(self) -> Token:
        return self.lastToken
    
    def peekNextToken(self) -> Token:
        return self._getNextToken(False)

    def _getNextToken(self, writeChange = True) -> Token:
        self.line = self._removeMeaningless(self.line)
        while self.line == '':
            line = self.file.readline()
            if line == '':
                return None
            self.line = self._removeMeaningless(line)
        token = None
        sCrop = None
        if self.line[0] in self.symbols:
            token = Token(self.line[0], Token.kinds['symbol'])
            sCrop = 1
        elif self.line[0] == self.stringS:
            string = self.line.split(self.stringS)[1]
            token = Token(string, Token.kinds['stringConstant'])
            sCrop = len(string)+2
        else:
            nextword = self.line.split(' ')[0][:self._firstSymbolIndex(self.line.split(' ')[0])]
            if nextword.isdigit():
                token = Token(nextword, Token.kinds['integerConstant'])
                sCrop = len(nextword)
            elif nextword in self.keywords:
                token = Token(nextword, Token.kinds['keyword'], Token.keyWords[nextword])
                sCrop = len(nextword)
            else:
                token = Token(nextword, Token.kinds['identifier'])
                sCrop = len(nextword)
        if writeChange: self.line = self.line[sCrop: ]
        return token
    
    def _firstSymbolIndex(self, string) -> int:
        index = len(string)
        for symbol in self.symbols:
            if symbol in string and string.index(symbol) < index:
                index = string.index(symbol)
        return index
    
    def _removeMeaningless(self, line) -> None:
        multyLineS = '/*'
        multyLineE = '*/'
        singleLineS = '//'
        line = line.replace('\n', '').replace('\t', '')
        if self.insideComment:
            if multyLineE not in line:
                line = ''
            else:
                line = line[line.index(multyLineE)+len(multyLineE):]
                self.insideComment = False
        while multyLineS in line:
            if multyLineE in line:
                self.insideComment = False
                line = line[:line.index(multyLineS)] + line[line.index(multyLineE)+len(multyLineE):]
            else:
                self.insideComment = True
                line = line[:line.index(multyLineS)]
        if singleLineS in line: line = line[:line.index('//')]
        while line != '' and line[0] == ' ':
            line = line[1:]
        return line
