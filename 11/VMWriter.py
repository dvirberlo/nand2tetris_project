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
        row = self._getNamedRow(name)
        return row["kind"] if row != None else None
    def typeOf(self, name) -> str:
        row = self._getNamedRow(name)
        return row["type"] if row != None else None
    def indexdOf(self, name) -> int:
        row = self._getNamedRow(name)
        return row["index"] if row != None else None
    def _getNamedRow(self, name) -> object:
        for row in self.table:
            if row["name"] == name:
                return row
        return None

class VMWriter:
    def __init__(self, file) -> None:
        self.file = file

        self.className = ''
        self.classScope = SymbolTable()
        self.subroutineScope = SymbolTable()
        self.uniqueCounter = 0

    def getUnique(self):
        self.uniqueCounter += 1
        return self.uniqueCounter

    def getByName(self, name) -> object:
        row = self.subroutineScope._getNamedRow(name)
        if row == None:
            row = self.classScope._getNamedRow(name)
        return row
    
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
    def writeReturn(self) -> None:
        self.file.write('return\n')
