import pprint as pp
from ast import AST

from string import whitespace

#------------------------------------------------------------------------
# Syntax
#------------------------------------------------------------------------

class Table(AST):
    def __init__(self, id, *policy):
        self.id = id
        self.policy = policy

    def to_yaml(self):
        return 'Table(id=%r, policy=%r)' % (self.id, self.policy)

class Transform(AST):
    def __init__(self, id, *policy):
        self.id = id
        self.policy = policy

    def to_yaml(self):
        return 'Transform(id=%r, policy=%r)' % (self.id, self.policy)

class Fields(AST):
    def __init__(self, *elts):
        self.elts = elts

    def to_yaml(self):
        return 'Fields(elts=%r)' % (self.elts,)

class List(AST):
    def __init__(self, *elts):
        self.elts = list(elts[0])

    def to_yaml(self):
        return 'List(elts=%r)' % (self.elts,)

class Let(AST):
    def __init__(self, *bindings):
        binders = bindings[0:-2]
        body = bindings[-1]
        self.map = dict((a,b) for a, _, b in binders)
        self.body = body

    def to_yaml(self):
        return 'Let(bindings=%r)' % (self.map.items(),)

class Renderer(AST):
    def __init__(self, id, *expr):
        self.id = id
        self.expr = expr

    def to_yaml(self):
        return 'Renderer(id=%r, expr=%r)' % (self.id, self.expr)

class Import(AST):
    def __init__(self, *module):
        self.module = module

    def to_yaml(self):
        return 'Import(module=%r)' % (self.module,)

class Bind(AST):
    def __init__(self, *binders):
        self.map = dict((a,b) for a, b in binders)

    def to_yaml(self):
        return 'Bind(map=%r)' % (self.map.tems())

class Pull(AST):
    def __init__(self, source, expr):
        self.source = source
        self.expr = expr

    def to_yaml(self):
        return 'Pull(source=%r, expr=%r)' % (self.source, self.expr)

class Push(AST):
    def __init__(self, schema, expr):
        self.schema = schema
        self.expr = expr

    def to_yaml(self):
        return 'Push(schema=%r, expr=%r)' % (self.schema, self.expr)

#------------------------------------------------------------------------
# Parser
#------------------------------------------------------------------------

tokens = {
    'table'     : Table,
    'fields'    : Fields,
    'transform' : Transform,
    'renderer'  : Renderer,
    'let'       : Let,
    'list'      : List,
    'import'    : Import,
    'bind'      : Bind,
    'pull'      : Pull,
}

lexemes = set('()[]"\'\#') | set(whitespace)

def parse(ast):
    if isinstance(ast, list):
        head = ast[0]

        if isinstance(head, list):
            return map(parse, ast)
        else:
            if head in tokens:
                args = map(parse, ast[1:])
                return tokens[head](*args)
            else:
                return map(parse, ast)
    else:
        return ast

def lex(sexp):
    stack, i, length = [[]], 0, len(sexp)

    while i < length:
        c = sexp[i]
        active = type(stack[-1])

        if active == list:
            # sexp open paren
            if c == '(':
                stack.append([])

            # sexp close paren
            elif c == ')':
                stack[-2].append(stack.pop())
                if stack[-1][0] == ('quote',):
                    stack[-2].append(stack.pop())

            # string literal
            elif c == '"':
                stack.append('')

            # scheme-style quotation
            elif c == "'":
                stack.append([('quote',)])

            # noop whitespace
            elif c in whitespace:
                pass

            else:
                stack.append((c,))

        elif active == str:

            # string literal
            if c == '"':
                stack[-2].append(stack.pop())
                if stack[-1][0] == ('quote',):
                    stack[-2].append(stack.pop())

            # string escape
            elif c == '\\':
                i += 1
                stack[-1] += sexp[i]

            # name token
            else:
                stack[-1] += c

        elif active == tuple:
            if c in lexemes:
                token = stack.pop()

                if token[0][0].isdigit():
                    stack[-1].append(eval(token[0]))

                # string token
                else:
                    stack[-1].append(token[-1])

                # quotation
                if stack[-1][0] == ('quote',):
                    stack[-2].append(stack.pop())

                # let binding
                if token[0][0] == ':':
                    pass

                # stencil token
                if token[0][0] == '#':
                    stack[-1].pop()

                continue

            else:
                stack[-1] = ((stack[-1][0] + c),)

        i += 1
    return stack.pop()


source = """
(import BokehRuntime)
(import py-numpy (as np))

(table plot
  (renderer shapes)
  (data
   (pull flowers
    (let (x : petalL)
         (y : petalW)
         (fillC : (ColorBy Species))
         (shape : 'Circle)))))

(table pairs
  (fields source colorAtt xAtt yAtt)
  (renderer shapes)
  (data
   (pull source
         (let (x : Att)
              (y : yAtt)
              (fillC : (colorBy colorAtt))
              (shape : 'Circle)))))

(table dataset
  (fields a b c)
  (data (init (let (x : (np.arange 100))
                   (y : (np.sin x))
                   (z : (np.cos x))
                ##(a:x, b:y, c:z))))
  (render table (fields a b c))
  (render scatter (bind (x: a) (y: b) (color: "orange")))
  (render scatter (bind (x: a) (y: c) (color: "red")))
  (render plot (bind (x: a) (y: b) (color: "yellow")))
  (render plot (bind (x: a) (y: c) (color: "black")))
  (render plot (bind (x: a) (y: b) (color: "blue"))
               (bind (x: a) (y: c) (color: "green"))))

"""

glyphs = """
(table source
  (fields x y z radius color)
  (data (init
    ##(x:(list 1,2,3,4,5),
       y:(list 5,4,3,2,1),
       z:(list 3,3,3,3,3),
       radius:(list 10,5,5,5,5),
       color:(list "blue","blue","red","blue","blue"))))
  (render GlyphRenderer
    (bind (x:x) (y:y) (color:"blue") (type: "circles"))
    (guide x LinearAxis {orientation:"bottom"})
    (guide y LinearAxis {orientation:"left"})))
"""

if __name__ == '__main__':
    ast = lex(source)
    pp.pprint(ast)
    pp.pprint(parse(ast))
