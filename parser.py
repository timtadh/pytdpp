#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import functools, types
import analysis, tdpp
from gram_parser import parse as gram_parse
from analysis import first, follow, build_table
from gram_parser import EmptyString, EoS, Terminal, NonTerminal

class BaseParser(object):

    # Set this in you subclass to your list of tokens (as strings)
    tokens = None

    PRODUCTIONS = '__productions__'

    @classmethod
    def production(cls, production):
        def dec(f, *args, **kwargs):
            if not hasattr(f, cls.PRODUCTIONS):
                setattr(f, cls.PRODUCTIONS, list())
            getattr(f, cls.PRODUCTIONS).append(production)
            return f
        return dec

    def __new__(cls, lexer, *args, **kwargs):
        self = super(BaseParser, cls).__new__(cls)
        Start = NonTerminal('Start')
        self.lexer = lexer
        PARSE = functools.partial(gram_parse, cls.tokens)
        productions = None
        for attrname in dir(self):
            attr = getattr(self, attrname)
            if type(attr) == types.MethodType and hasattr(attr, cls.PRODUCTIONS):
                for prod in getattr(attr, cls.PRODUCTIONS):
                    p = PARSE(prod+';')
                    p.addfunc(p[0], 0, attr)
                    if productions is not None: productions |= p
                    else: productions = p
        print productions
        print productions.functions
        if Start in productions.order:
            productions.order.remove(Start)
            productions.order.insert(0, Start)
        self.productions = productions
        return self

    def parse(self, text):
        g = self.__parse__(self.lexer(text), self.productions)
        return self.__process__(g)

    def __process__(self, gen):
        def top(stack): return stack[-1]
        def call(frame): return frame['f'](frame['me'], *frame['args'])
        def collapse(stack):
            ret = None
            if stack and top(stack)['limit'] == len(top(stack)['args']):
                arg = call(stack.pop())
                if stack: top(stack)['args'].append(arg)
                print arg
                ret = collapse(stack)
                if ret is None: ret = arg
            print ret
            return ret

        ret = None
        stack = list()
        for children, sym, f in gen:
            if sym.terminal:
                top(stack)['args'].append(sym.value)
            else:
                stack.append({'me':sym, 'args':list(), 'limit':children, 'f':f})
            ret = collapse(stack)
        return ret

    def __parse__(self, tokens, productions):
        def next():
            try:
                t = tokens.next()
                tok = Terminal(t.type)
                tok.original = t
                tok.value = t.value
                return tok
            except:
                return EoS()
        M = build_table(productions)

        stack = [ EoS(), productions[0] ]
        X = stack[-1]
        a = next()
        while X != EoS():
            #print X.sym, a.sym, stack
            if X == a:
                yield 0, a, None
                stack.pop()
                a = next()
            elif X.empty:
                yield 0, X, None
                stack.pop()
            elif X.terminal:
                raise Exception
            elif not M[(X, a)]:
                raise Exception
            elif M[(X, a)]:
                nt = M[(X, a)][0]
                production = productions[nt][M[(X, a)][1]]
                function = productions.getfunc(nt, M[(X, a)][1])
                yield len(production), X, function
                stack.pop()
                for sym in (production[i] for i in range(len(production)-1, -1, -1)):
                    stack.append(sym)
            X = stack[-1]

class TestParser(BaseParser):

    tokens = ['NUMBER']

    @BaseParser.production("Start : NUMBER")
    def Start(self, NUMBER):
        print 'hello'

if __name__ == '__main__':
    print TestParser()