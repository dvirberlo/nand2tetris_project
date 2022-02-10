from JackTokenizer import Token

class SymbolTable:
    def __init__(self) -> None:
        self.table = []
    
    def definde(self, name, type, kind) -> None:
        self.table.append({
            "name": name,
            "type": type,
            "kind": kind,
            "index": self.countByKind(kind),
        })
    
    def countByKind(self, kind) -> int:
        count = 0
        for row in self.table:
            if row["kind"] == kind: count += 1
        return count
    
    def kindOf(self, name) -> str:
        return self._getNamedRow(name)["kind"]
    def typeOf(self, name) -> str:
        return self._getNamedRow(name)["type"]
    def indexdOf(self, name) -> int:
        return self._getNamedRow(name)["index"]
    def _getNamedRow(self, name) -> object:
        for row in self.table:
            if row["name"] == name:
                return row

class VMWriter:
    def __init__(self, file) -> None:
        self.file = file
    
    def writePush(self, segment, index) -> None:
        self.file.write(f'push {segment} {index}\n')
    def writePop(self, segment, index) -> None:
        self.file.write(f'pop {segment} {index}\n')
    def writeArithmetic(self, command) -> None:
        self.file.write(f'{command}\n')
    
    def writeLabel(self, label) -> None:
        self.file.write(f'label {label}\n')
    def writeGoto(self, label) -> None:
        self.file.write(f'goto {label}\n')
    def writeIfGoto(self, label) -> None:
        self.file.write(f'if-goto {label}\n')
    
    def writeCall(self, name, argsCount) -> None:
        self.file.write(f'call {name} {argsCount}\n')
    def writeFunction(self, name, localsCount) -> None:
        self.file.write(f'function {name} {localsCount}\n')


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
