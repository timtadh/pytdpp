#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

from gram_parser import parse, EmptyString, EoS,  NonTerminal, Terminal
import analysis

import functools, nose
from ply import lex
from ply.lex import Token

tokens = [
    'NUMBER', 'SLASH', 'DASH',
    'STAR', 'PLUS', 'LPAREN', 'RPAREN'
]

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


productions = parse(tokens, grammar)

def FIRST(sym):
    if hasattr(sym, 'sym'):
        return analysis.first(productions, sym)
    return analysis.first(productions, NonTerminal(sym))
def FOLLOW(sym):
    if hasattr(sym, 'sym'):
        return analysis.follow(productions, sym)
    return analysis.follow(productions, NonTerminal(sym))

def t_print():
    for k,v in productions.iteritems():
        print k
        for p in v:
            print ' '*4, p
        print ' '*4, 'first', tuple(FIRST(k))
        print ' '*4, 'follow', tuple(FOLLOW(k))

def t_runall():
    for k,v in productions.iteritems():
        FIRST(k)
        FOLLOW(k)

def t_first():
    assert FIRST("Expr") == FIRST("Term") == FIRST("Factor")
    assert FIRST('Expr') == set([Terminal('LPAREN'), Terminal('NUMBER')])
    assert FIRST("Expr'") == set([Terminal('PLUS'), Terminal('DASH'), EmptyString()])
    assert FIRST("Term'") == set([Terminal('STAR'), Terminal('SLASH'), EmptyString()])

def t_follow():
    assert FOLLOW("Expr") == FOLLOW("Expr'") == set([Terminal("RPAREN"), EoS()])
    assert FOLLOW("Term") == FOLLOW("Term'")
    assert FOLLOW("Term") == set([Terminal("DASH"), Terminal("PLUS"), Terminal("RPAREN"), EoS()])
    assert FOLLOW("Factor") == set([
        Terminal('STAR'), Terminal('SLASH'), Terminal("DASH"), Terminal("PLUS"), Terminal("RPAREN"), EoS()
    ])

def t_check():
    assert analysis.LL1(productions)
    assert not analysis.LL1(parse(tokens, grammar + '\n Factor : LPAREN NUMBER RPAREN;'))


def t_build():
    print analysis.build_table(productions, True)
