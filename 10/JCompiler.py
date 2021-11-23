import os
import sys
import math
# TODO: readable
class JCompiler:
    ext = '.jack'
    # extP = '.vm'
    extP = 'T.vm.xml'
    version = '0.1'
    name = 'JCompiler'

    stringS = '"'
    symbols = '{[]}().,;+-*/&!|<>='
    keywords = 'class, constructor, function, method, field, static, var, int, char, boolean, void, true, false, null, this, let, do, if, else, while, return'.split(', ')
      
    def __init__(self):
        self.insideComment = False
        self.stack = []
        self.lastToken = False

    def compile(self, filepath, writeCallback):
        filename = os.path.basename(filepath).replace(self.ext, '')
        with open(filepath) as file:
          for line in file:
              lineCode = self._removeMeaningless(line)
              if line != '':
                  lineCode = self._parse(self._tokenize(lineCode))
                  writeCallback(lineCode)

    def _removeMeaningless(self, line):
        multyLineS = '/*'
        multyLineE = '*/'
        singleLineS = '//'
        line = line.replace('\n', '').replace('\t', '')
        if self.insideComment:
            if multyLineE not in line:
                line = ''
            else:
                line = line[line.index(multyLineE)+len(multyLineE):]
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
    
    def _tokenize(self, line):
        tokens = []
        while line != '':
            if line[0] == ' ':
                line = line[1:]
            elif line[0] in self.symbols:
                tokens.append(['symbol', line[0]])
                line = line[1:]
            elif line[0] == self.stringS:
                string = line.split(self.stringS)[1]
                tokens.append(['stringConstant', string])
                line = line[len(string)+2:]
            else:
                nextword = line.split(' ')[0][:self._firstSymbolIndex(line.split(' ')[0])]
                if nextword.isdigit():
                    tokens.append(['integerConstant', nextword])
                    line = line[len(nextword):]
                elif nextword in self.keywords:
                    tokens.append(['keyword', nextword])
                    line = line[len(nextword):]
                else:
                    tokens.append(['identifier', nextword])
                    line = line[len(nextword):]
        return tokens
    def _firstSymbolIndex(self, string):
        index = len(string)
        for symbol in self.symbols:
            if symbol in string and string.index(symbol) < index:
                index = string.index(symbol)
        return index

    # TODO true, false, null, this
    parseDict = {
        'class': {
            'self': ['class', '}', True],
            'children': []
        },
        'constructor': {
            'self': ['subroutineDec', '}', True],
            'children': [
                ['parameterList', '()', False],
                ['subroutineBody', '{}', True],
            ]
        },
        'function': {
            'self': ['subroutineDec', '}', True],
            'children': [
                ['parameterList', '()', False],
                ['subroutineBody', '{}', True],
            ]
        },
        'method': {
            'self': ['subroutineDec', '}', True],
            'children': [
                ['parameterList', '()', False],
                ['subroutineBody', '{}', True],
            ]
        },
        'field': {
            'self': ['classVarDec', ';', True],
            'children': []
        },
        'static': {
            'self': ['classVarDec', ';', True],
            'children': []
        },
        'var': {
            'self': ['varDec', ';', True],
            'children': []
        },
        'let': {
            'self': ['letStatement', ';', True],
            'children': [],
        },
        'do': {
            'self': ['doStatement', ';', True],
            'children': [],
        },
        'if': {
            'self': ['ifStatement', '}', True],
            'children': [],
        },
        'else': {
            'self': ['', '}', True],
            'children': [],
        },
        'while': {
            'self': ['whileStatement', '}', True],
            'children': [],
        },
        'return': {
            'self': ['returnStatement', ';', True],
            'children': [],
        },
    }
    statements = ['letStatement', 'doStatement', 'ifStatement', '', 'whileStatement', 'returnStatement']
    
    def _parseTokenTree(self, token):
        result = { 'token': False, 'tree': False, 'before':False, 'statements': False, 'close': False, 'append': [], 'pop': 0, 'counter': 0, 'wrriten': False }
        [cls, val] = token
        if val in self.parseDict.keys():
            # tree start
            [treeName, grammer, before] = self.parseDict[val]['self']
            parentName = 'statements'
            if treeName in self.statements and (len(self.stack) < 2 or self.stack[-2][1] != parentName):
                self.stack.append([parentName, parentName, 0])
                result['statements'] = True
            result['token'] = token
            result['tree'] = treeName
            result['before'] = before
            result['close'] = False
            result['wrriten'] = True
            result['append'].append([val, treeName, 0])
        elif len(self.stack) > 0 and self.stack[-1][0] in self.parseDict:
            [key, treeName, counter] = self.stack[-1]
            if val == self.parseDict[key]['self'][1]:
                # tree end
                before = self.parseDict[key]['self'][2]
                result['token'] = token
                result['tree'] = treeName
                result['before'] = before
                result['close'] = True
                result['wrriten'] = True
                result['pop'] += 1
            elif len(self.parseDict[key]['children']) > 0 and val == self.parseDict[key]['children'][math.floor(counter/2)][1][counter%2]:
                # tree child start/end
                close = counter%2 == 1
                [childName, childG, before] = self.parseDict[key]['children'][math.floor(counter/2)]
                result['token'] = token
                result['tree'] = childName
                result['before'] = before
                result['close'] = close
                result['wrriten'] = True
                result['counter'] += 1
        if self.x < 20: print(result)
        return result.values()

    def _performParseTree(self, Ptree, val):
        xml = ''
        (Rtoken, Rtree, Rbefore, Rstatements, Rclose, Rappend, Rpop, Rcounter, Rwrriten) = Ptree
        if Rwrriten:
            xml += self._xmlTree(Rtoken, Rtree, Rbefore, Rclose)
        if self.stack != []:
            self.stack = self.stack[Rpop:]
        for item in Rappend:
            self.stack.append(item)
        if self.stack != [] and self.stack[-1][0] in self.parseDict:
            [key, treeName, counter] = self.stack[-1]
            if len(self.parseDict[key]['children']) > 0 and val == self.parseDict[key]['children'][math.floor(counter/2)][1][counter%2]:
                [childName, childG, before] = self.parseDict[key]['children'][math.floor(counter/2)]
                self.stack[-1] = [key, treeName, counter + Rcounter]
    
    x = 1
    def _parse(self, tokens):
        xml = ''
        for token in tokens:
            wrriten = False
            [cls, val] = token
            
            
            (Rtoken, Ptree, Rbefore, Rstatements, Rclose, Rappend, Rpop, Rcounter, Rwrriten) = self._parseTokenTree(token)
            parentName = 'statements'
            if Ptree in self.statements and (len(self.stack) < 2 or self.stack[-2][1] != parentName):
                xml += self._xml(self._xmlIndent(), parentName, False)
                self.stack.append([parentName, parentName, 0])
            elif Ptree not in self.statements and len(self.stack) > 2 and self.stack[-2][1] == parentName:
                xml += self._xml(self._xmlIndent(), parentName, True)
                self.stack.pop()
            Ptree = self._parseTokenTree(token)
            (Rtoken, Rtree, Rbefore, Rstatements, Rclose, Rappend, Rpop, Rcounter, Rwrriten) = Ptree
            self._performParseTree(Ptree, val)
            wrriten = Rwrriten

            # if self.x < 100: print(self.stack)
            self.x += 1
            # specials
            if self.stack != [] and self.stack[-1][1] == 'expressionList' and val != ',':
                treeName = 'expression'
                xml += self._xmlTree(token, treeName, True)
                self.stack.append([treeName, treeName, 0])
            if not wrriten:
                if val in '()':
                    treeName = 'expressionList'
                    close = val == ')'
                    if close or self.lastToken[0] == 'identifier':
                        xml += self._xmlTree(token, treeName, False, close)
                        wrriten = True
                        if close:
                            if self.stack != [] and self.stack[-1][1] == 'expression':
                                self.stack.pop()
                            self.stack.pop()
                        else: self.stack.append([treeName, treeName, 0])
                elif val in '=[]' or (val == ';' and self.stack != [] and self.stack[-1][1] == 'expression'):
                    close = val in '];'
                    treeName = 'expression'
                    xml += self._xmlTree(token, treeName, False, close)
                    wrriten = True
                    if close: self.stack.pop()
                    else: self.stack.append([treeName, treeName, 0])
                elif self.stack != [] and self.stack[-1][1] == 'expression' and cls != 'symbol':
                    treeName = 'term'
                    xml += self._xmlTree(token, treeName, True)
                    xml += self._xml(self._xmlIndent(), treeName, True)
                    wrriten = True
                elif self.stack != [] and self.stack[-1][1] == 'expressionList' and val == ',':
                    treeName = 'expression'
                    xml += self._xmlTree(token, treeName, True, True)
                    wrriten = True
                    self.stack.pop()
                else:
                    xml += self._xml(self._xmlIndent(), token)
            self.lastToken = token
        return xml

    def _statmentCheck(self, treeName):
        xml = ''
        if treeName not in self.statements and self.stack != [] and self.stack[-1][1] == 'statements':
            parentName = 'statements'
            xml += self._xml(self._xmlIndent()-1, parentName, True)
            self.stack.pop()
            self.stack.pop()
        return xml
    def _xmlIndent(self):
        stackLen = len(self.stack)
        if stackLen > 0 and self.stack[-1][2]%2 == 1:
            stackLen += 1
        return stackLen
    def _xmlTree(self, token, treeName, before, close=False):
        indent = self._xmlIndent()
        if not treeName:
            return self._xml(indent, token, close)
        # if before: tokenXml = self._xml(indent+1, token, close)
        # else: tokenXml = self._xml(indent+1, token, close)
        # treeXml = self._xml(indent, treeName, close)
        # if close: before = not before
        # if before: return treeXml + tokenXml
        # else: return tokenXml + treeXml
        if not close:
            if before:
                return self._xml(indent, treeName, close) + self._xml(indent+1, token, close)
            else:
                return self._xml(indent, token, close) + self._xml(indent, treeName, close)
        else:
            if before:
                return self._xml(indent, token, close) + self._xml(indent-1, treeName, close)
            else:
                return self._xml(indent-1, treeName, close) + self._xml(indent-1, token, close)
    def _xml(self, indentC,  obj, close=False):
        indentS = '  '
        if (type(obj) == str):
            return indentC * indentS + ('</' if close else '<') + self._xmlLang(obj) + ">\n"
        else:
            return indentC * indentS + '<'+obj[0]+'> ' +self._xmlLang(obj[1]) +' </'+obj[0]+'>\n'
    def _xmlLang(self, str):
        return str.replace('<', '&lt;').replace('>', '&gt;')



def main(argv):
    trClass = JCompiler
    help = 'Usage:\n' + '  python3 ' + trClass.name + '.py [ ...files| ...dirs] [ -r| --recursive]'
    version = trClass.name + ' v' + trClass.version + ' for ' + trClass.ext +' files (nand2tetris.org)\n' + 'written by @dvirberlo'

    recursiveWarn = 'WARNING: recursive mode is on.'
    forceWarn = 'WARNING: force mode is on.'
    removableArgs = {
        '-r': recursiveWarn, '--recursive':recursiveWarn,
        '-fsm': forceWarn, '--force-single-mode': forceWarn,
        '-fmm': forceWarn, '--force-multy-mode': forceWarn,
    }
    args = argv[1:]
    if len(args) == 0:
        print(help + '\n\n' + version)
    elif '-h' in args or '--help' in args:
        print(help)
    elif '-v' in args or '--version' in args:
        print(version)
    else:
        paths = args
        recursive = '-r' in args or '--recursive' in args
        forceSingleMode = '-fsm' in args or '--force-single-mode' in args
        forceMultyMode = '-fmm' in args or '--force-multy-mode' in args
        for rmArg in removableArgs:
            if rmArg in paths:
                if removableArgs[rmArg]: print(removableArgs[rmArg])
                paths.remove(rmArg)
            while rmArg in paths:
                paths.remove(rmArg)
        
        if recursive and len(paths) == 0:
            paths = ['.']

        for path in paths:
            if os.path.isfile(path):
                singleParse(trClass, path)
            else:
                for (dirPath, dirnames, filenames) in os.walk(path):
                    extFilenames = [filename for filename in filenames if trClass.ext in filename]
                    if len(extFilenames) == 0:
                        print(trClass.name + ' skipped: ' + dirPath , flush=True)
                    elif not forceMultyMode and (forceSingleMode or len(extFilenames) < 2):
                        for filename in extFilenames:
                            filePath = os.path.join(dirPath, filename)
                            singleParse(trClass, filePath)
                    else:
                        multyParse(trClass, dirPath, extFilenames)

def singleParse(trClass, filepath):
    asmPath = filepath.replace(trClass.ext, trClass.extP)
    with open(asmPath, 'w') as asmFile:
        def singleParseCallback(asm):
            asmFile.write(asm)
        print(trClass.name + ' single-mode parse: ' + filepath + ' started... ', end='', flush=True)
        trClass().compile(filepath, singleParseCallback)
        print('done')

def multyParse(trClass, dirPath, filenames):
    asmPath = os.path.join(dirPath, os.path.basename(os.path.normpath(dirPath)) + trClass.extP)
    with open(asmPath, 'w') as asmFile:
        translator = trClass()
        asmFile.write(translator.boot)
        def multyParseCallback(asm):
            asmFile.write(asm)
        print(trClass.name + ' multy-mode parse: ' + dirPath + ' started... ', flush=True)
        for filename in filenames:
            filePath = os.path.join(dirPath, filename)
            print('+  ' + filename + ' started... ', end='', flush=True)
            translator.compile(filePath, multyParseCallback)
            print('done', flush=True)
        print('done', flush=True)

if __name__ == '__main__': main(sys.argv)