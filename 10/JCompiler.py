import os
import sys
import math
# TODO: readable
class JCompiler:
    ext = '.jack'
    # extP = '.vm'
    extP = '.vm.xml'
    version = '0.1'
    name = 'JCompiler'
    boot = ''

    stringS = '"'
    symbols = '{[]}().,;+-*/&!|<>='
    keywords = 'class, constructor, function, method, field, static, var, int, char, boolean, void, true, false, null, this, let, do, if, else, while, return'.split(', ')
      
    def __init__(self):
        self.insideComment = False
        self.stack = []
        self.lastToken = ['', 's']

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

    statements = ['let', 'do', 'if', 'while', 'return']
    nonStatements = ['constructor', 'function', 'method', 'field', 'static', 'var', 'class']
    x = 0

    def _parse(self, tokens):
        xml = ''
        for token in tokens:
            self.x += 1
            xmlF = self._isFirst(token)
            xmlT = self._isStatement(token)
            if not xmlT: xmlT += self._isSubroutineDec(token)
            if not xmlT: xmlT += self._isClassVarDec(token)
            if not xmlT: xmlT += self._isOthers(token)
            xmlT += self._isLast(token, xmlT or xmlF)
            xml += xmlF + xmlT
            self.lastToken = token
        return xml
    def _isFirst(self, token):
        [cls, val] = token
        xml = ''
        expressionName = 'expression'
        termName = 'term'
        if self.lastToken[1] == 'return' and val != ';':
            xml += self._xml(self._xmlIndent(), expressionName, False)
            self.stack.append({'val': expressionName})
            xml += self._xmlTree(token, termName, True)
            xml += self._xml(self._xmlIndent(), termName, True)
            
        if val in '=[]' or (val == ';' and self.stack != [] and self.stack[-1]['val'] == expressionName):
            close = val in '];'
            if close:
                self.stack.pop()
                xml += self._xml(self._xmlIndent(), expressionName, True)
            else:
                if cls not in ['identifier', 'keyword']:
                    xml += self._xmlTree(token, expressionName, False, close)
                    self.stack.append({'val': expressionName})
                else:
                    xml += self._xml(self._xmlIndent(), expressionName, close)
                    self.stack.append({'val': expressionName})
                    xml += self._xmlTree(token, termName, False, close)
                    self.stack.append({'val': termName})

        statementsName = 'statements'
        if val in self.statements and (self.stack == [] or self.stack[-1]['val'] != statementsName):
            xml += self._xml(self._xmlIndent(), statementsName, False)
            self.stack.append({'val': statementsName})
        elif val in self.nonStatements and self.stack != [] and self.stack[-1]['val'] == statementsName:
            xml += self._xml(self._xmlIndent(), statementsName, True)
            self.stack.pop()
        if self.stack != [] and self.stack[-1]['val'] == statementsName and val == '}':
            self.stack.pop()
            xml += self._xml(self._xmlIndent(), statementsName, True)
        return xml
    def _isStatement(self, token):
        [cls, val] = token
        keyWords = [['let'], ['do'], ['if'], ['while'], ['return']]
        keyMarks = [ ';',     ';',    '}',    '}',       ';'      ]
        endName = 'Statement'
        xml = ''
        for idx in range(len(keyWords)):
            if val in keyWords[idx]:
                xml += self._xmlTree(token, val+endName, True, False)
                self.stack.append({'val': val})
            elif val in keyMarks[idx] and self.stack != [] and self.stack[-1]['val'] in keyWords[idx]:
                xml += self._xmlTree(token, self.stack[-1]['val']+endName, True, True)
                self.stack.pop()
        return xml
    def _isSubroutineDec(self, token):
        [cls, val] = token
        keyWords = ['constructor', 'function', 'method']
        keyMarks = [ '(', ')', '{', '}']
        parentName = 'subroutineDec'
        children = [ ['parameterList', False], ['subroutineBody', True] ]
        xml = ''
        # if val == '}' and self.stack != []: print(self.stack[-1]['val'])
        if val in keyWords:
            xml += self._xmlTree(token, parentName, True, False)
            self.stack.append({'val': val, 'inChild': False})
        elif val in keyMarks and self.stack != [] and self.stack[-1]['val'] in keyWords:
            [childName, before] = children[math.floor(keyMarks.index(val)/2)]
            close = keyMarks.index(val)%2 == 1
            if keyMarks.index(val) +1 == len(keyMarks):
                xml += self._xmlTree(token, childName, True, True)
                self.stack[-1]['inChild'] = False
                xml += self._xml(self._xmlIndent()-1, parentName, True)
                self.stack.pop()
            else:
                xml += self._xmlTree(token, childName, before, close)
                self.stack[-1]['inChild'] = not close
        return xml
    def _isClassVarDec(self, token):
        [cls, val] = token
        keyWords = ['field', 'static']
        keyMarks = [';']
        parentName = 'classVarDec'
        xml = ''
        if val in keyWords:
            xml = self._xmlTree(token, parentName, True, False)
            self.stack.append({'val': val})
        elif val in keyMarks and self.stack != [] and self.stack[-1]['val'] in keyWords:
            xml = self._xmlTree(token, parentName, True, True)
            self.stack.pop()
        return xml
    def _isOthers(self, token):
        [cls, val] = token
        keyWords = [['var'], ['class']]
        keyMarks = [[';'], ['}']]
        parentNames = ['varDec', 'class']
        xml = ''
        for idx in range(len(keyWords)):
            if val in keyWords[idx]:
                xml = self._xmlTree(token, parentNames[idx], True, False)
                self.stack.append({'val': val})
            elif val in keyMarks[idx] and self.stack != [] and self.stack[-1]['val'] in keyWords[idx]:
                xml = self._xmlTree(token, parentNames[idx], True, True)
                self.stack.pop()
        return xml
    def _isLast(self, token, wrriten):
        [cls, val] = token
        xml = ''        
        expressionListName = 'expressionList'
        expressionName = 'expression'
        termName = 'term'
        if self.stack != [] and self.stack[-1]['val'] == expressionListName and val not in ',)':
            # xml += self._xmlTree(token, expressionName, True)
            xml += self._xml(self._xmlIndent(), expressionName, False)
            self.stack.append({'val': expressionName})
        if not wrriten:
            if val in '()':
                close = val == ')'
                if (close and (self.stack[-2]['val'] == expressionListName or self.stack[-1]['val'] == expressionListName)) or (not close and self.lastToken[0] == 'identifier'):
                    if self.stack[-1]['val'] == expressionName:
                        self.stack.pop()
                        xml += self._xml(self._xmlIndent(), expressionName, True)
                    xml += self._xmlTree(token, expressionListName, False, close)
                    if close:
                        if self.stack != [] and self.stack[-1]['val'] == expressionName:
                            self.stack.pop()
                        self.stack.pop()
                    else: self.stack.append({'val': expressionListName})
                else:
                    xml += self._xmlTree(token, expressionName, False, close)
                    if not close: self.stack.append({'val': expressionName})
                    else: self.stack.pop()
            elif self.stack != [] and self.stack[-1]['val'] == expressionName and cls != 'symbol':
                xml += self._xmlTree(token, termName, True)
                xml += self._xml(self._xmlIndent(), termName, True)
            elif len(self.stack) > 2 and self.stack[-2]['val'] == expressionListName and val == ',':
                xml += self._xmlTree(token, expressionName, False, True)
                self.stack.pop()
                xml += self._xml(self._xmlIndent(), expressionName, False)
                self.stack.append({'val': expressionName})
            else:
                xml += self._xml(self._xmlIndent(), token)
        return xml

    def _xmlIndent(self):
        stackLen = len(self.stack)
        if stackLen > 0:
            for item in self.stack:
                if 'inChild' in item and item['inChild']:
                    stackLen += 1
        return stackLen
    def _xmlTree(self, token, treeName, before, close=False):
        indent = self._xmlIndent()
        # if not treeName:
        #     return self._xml(indent, token, close)
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
        forceSingleMode = True
        forceMultyMode = False
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
    destPath = filepath.replace(trClass.ext, trClass.extP)
    with open(destPath, 'w') as destFile:
        def singleParseCallback(text):
            destFile.write(text)
        print(trClass.name + ' single-mode parse: ' + filepath + ' started... ', end='', flush=True)
        trClass().compile(filepath, singleParseCallback)
        print('done')

def multyParse(trClass, dirPath, filenames):
    destPath = os.path.join(dirPath, os.path.basename(os.path.normpath(dirPath)) + trClass.extP)
    with open(destPath, 'w') as destFile:
        translator = trClass()
        destFile.write(translator.boot)
        def multyParseCallback(text):
            destFile.write(text)
        print(trClass.name + ' multy-mode parse: ' + dirPath + ' started... ', flush=True)
        for filename in filenames:
            filePath = os.path.join(dirPath, filename)
            print('+  ' + filename + ' started... ', end='', flush=True)
            translator.compile(filePath, multyParseCallback)
            print('done', flush=True)
        print('done', flush=True)

if __name__ == '__main__': main(sys.argv)