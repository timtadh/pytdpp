#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys

reserved = dict(
    (word.lower(), word) for word in (
        'E',
    )
)

TOKENSR = reserved.values() + [
    'COLON', 'NAME', 'END',
]
TOKENS = dict((k, i) for i, k in enumerate(TOKENSR))
sys.modules[__name__].__dict__.update(TOKENS)

class token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value
    def __repr__(self):
        return TOKENSR[self.type] + '=' + str(self.value)
    def __eq__(self, b):
        if b is None: return False
        if not isinstance(b, token): return False
        return self.type == b.type and self.value == b.value

def Lex(inpt):
    chars = list()

    def string(s):
        if s in reserved:
            return token(TOKENS[reserved[s]], s)
        return token(NAME, s)

    for line, cline in enumerate(inpt.split('\n')):
        for c, x in enumerate(cline):
            if x.isalpha():
                chars.append(x)
            elif chars and x == "'":
                chars.append(x)
            elif chars and x.isdigit():
                chars.append(x)
            elif chars:
                yield string(''.join(chars))
                chars = list()

            if x == ' ': continue
            elif x == ';': yield token(END, x)
            elif x == ':': yield token(COLON, x)
            elif not (x.isalpha() or (chars and x == "'") or (chars and x.isdigit())):
                m = 'Unexpected character! %s on line %i character %i' % (x, line+1, c+1)
                raise SyntaxError, m
    if chars:
        yield string(''.join(chars))
