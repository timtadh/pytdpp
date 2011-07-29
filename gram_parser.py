#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import functools
import gram_lexer as lx
from collections import MutableMapping

class Symbol(object):

    def __init__(self, sym, terminal, empty, eos):
        self.sym = sym
        self.terminal = terminal
        self.empty = empty
        self.eos = eos
        self.value = None

    def __tuple__(self):
        return (self.sym, self.terminal, self.empty, self.eos)

    def __eq__(self, b):
        if b is None: return False
        if isinstance(b, Symbol):
            return self.__tuple__() == b.__tuple__()
        return False

    def __ne__(self, b):
        return not self.__eq__(b)

    def __hash__(self):
        return hash(self.__tuple__())

    def __repr__(self):
        if self.eos: return '<EoS>'
        if self.empty: return '<EmptyString>'
        if self.terminal and self.value: return '<Terminal %s %s>' % (self.sym, self.value)
        if self.terminal: return '<Terminal %s>' % self.sym
        return '<NonTerminal %s>' % self.sym

def Terminal(sym):
    return Symbol(sym, True, False, False)
def EmptyString():
    return Symbol('e', True, True, False)
def EoS():
    return Symbol('$', True, False, True)
def NonTerminal(sym):
    return Symbol(sym, False, False, False)


class Productions(MutableMapping):

    def __init__(self, tokens, *args, **kwargs):
        super(Productions, self).__init__(*args, **kwargs)
        self.productions = dict()
        #self.functions = dict()
        self.order = list()
        self.tokens = tokens
        self.index = dict()

    def containing(self, sym):
        if sym not in self.index: return
        for p in self.index[sym]:
            yield p

    def __ior__(self, b):
        for k,v in b.iteritems():
            for p in v:
                self[k] = p
            #if k not in b.functions: continue
            #if k in self.functions: offset = len(self.functions[k])
            #else: offset = 0
            #for i, f in enumerate(b.functions[k]):
                #self.addfunc(k, offset+i, f)

        return self

    #def addfunc(self, key, i, func):
        #assert len(self[key])-1 == i
        #if key not in self.functions:
            #self.functions[key] = list()
        #assert len(self.functions[key]) == i
        #self.functions[key].append(func)

    #def getfunc(self, key, i):
        #return self.functions[key][i]

    def __setitem__(self, key, value):
        if key.sym not in self.productions:
            self.productions[key.sym] = list()
            self.order.append(key)
        if not isinstance(value, tuple): value = tuple(value)
        if value in self.productions[key.sym]: return
        self.productions[key.sym].append(value)
        for sym in value:
            if sym not in self.index:
                self.index[sym] = list()
            self.index[sym].append((key, value))

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.order[key]
        return self.productions[key.sym]

    def __delitem__(self, key):
        for p in self.productions[key.sym]:
            for sym in p:
                if sym in self.index:
                    self.index[sym].remove((key, p))
        del self.productions[key.sym]
        self.order.remove(key)

    def __iter__(self):
        for key in self.order:
            yield key

    def __len__(self):
        return len(self.order)

    def __repr__(self): return repr(self.productions)


class parse(object):
        # Productions : Production Productions'
        # Productions' : Production Productions'
        # Productions' : e
        # Production : NAME COLON Symbols END
        # Symbols : Symbol Symbols'
        # Symbols' : Symbol Symbols'
        # Symbols' : e
        # Symbol : NAME
        # Symbol : E

    def __new__(cls, tokens, grammar, **kwargs):
        ## Does magic to allow PLY to do its thing.-
        self = super(parse, cls).__new__(cls, **kwargs)
        self.__init__(tokens)
        self.s = list(lx.Lex(grammar))
        i, r = self.Start(0)
        return r

    def __init__(self, tokens):
        self.symbols = set()
        self.non_terminals = set()
        self.tokens = set(tokens)
        self.productions = Productions(tokens)

    def addproduction(self, nt, p):
        self.productions[NonTerminal(nt)] = p

    def Start(self, i):
        'Start : Productions'
        tokens = self.symbols - self.non_terminals
        i, r = self.Productions(i)
        return i, self.productions

    def Productions(self, i):
        # Productions : Production Productions'
        i, r0 = self.Production(i)
        i, r1 = self.Productions_(i)
        return i, None

    def Productions_(self, i):
        # Productions' : Production Productions'
        # Productions' : e
        if i == len(self.s):
            return i, None

        a = self.s[i]
        if a.type == lx.NAME: # Productions' : . Production Productions'
            i, r0 = self.Production(i)
            i, r1 = self.Productions_(i)
            return i, None
        else:  # Productions' : e .
            return i, None

    def Production(self, i):
        # Production : NAME COLON Symbols END
        a =self.s[i]
        if a.type == lx.NAME:
            i += 1
            name = a.value
        else:
            raise SyntaxError

        a =self.s[i]
        if a.type == lx.COLON:
            i += 1
        else:
            raise SyntaxError

        i, symbols = self.Symbols(i)

        a =self.s[i]
        if a.type == lx.END:
            i += 1
        else:
            raise SyntaxError

        self.non_terminals.add(name)
        self.symbols.add(name)
        self.addproduction(name, symbols)

        return i, None

    def Symbols(self, i):
        # Symbols : Symbol Symbols'
        i, symbol = self.Symbol(i)
        i, extra = self.Symbols_(i)
        return i, [ symbol ] + extra

    def Symbols_(self, i):
        # Symbols' : Symbol Symbols'
        # Symbols' : e
        if i == len(self.s):
            return i, list()

        a =self.s[i]
        if a.type == lx.NAME or a.type == lx.E: # Symbols' : . Symbol Symbols'
            i, symbol = self.Symbol(i)
            i, extra = self.Symbols_(i)
            return i, [ symbol ] + extra
        else:  # Symbols' : e .
            return i, list()

    def Symbol(self, i):
        # Symbol : NAME
        # Symbol : E
        a =self.s[i]
        if a.type == lx.NAME:
            i += 1
            if a.value in self.tokens:
                r = Terminal(a.value)
            else:
                r = NonTerminal(a.value)
        elif a.type == lx.E:
            i += 1
            r = EmptyString()
        else:
            raise SyntaxError
        return i, r

    def error(self, t):
        raise Exception, "Error %s" % t

if __name__ == '__main__':

    #import pdb
    #pdb.set_trace()
    tokens = [ 'NUMBER', 'SLASH', 'DASH', 'STAR', 'PLUS', 'LPAREN', 'RPAREN' ]
    grammar = '''
    Expr : Term Expr';
    Expr' : PLUS Term Expr';
    Expr' : DASH Term Expr';
    Expr' : e;
    Term : Factor Term';
    Term' : STAR Factor Term';
    Term' : SLASH Factor Term';
    Term' : e;
    Factor : NUMBER;
    Factor : LPAREN Expr RPAREN;
    '''
    print parse(tokens, grammar)


