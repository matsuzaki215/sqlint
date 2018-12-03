#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Token(object):
    COMMA = 'Comma'
    BRACKET = 'Bracket'
    KEYWORD = 'Keyword'
    OPERATOR = 'Operator'
    COMMENT = 'Comment'
    IDENTIFIER = 'Identifier'
    WHITESPACE = 'Whitespace'
    UNKNOWN = 'Unknown'

    def __init__(self, word, kind=UNKNOWN):
        self.word = word
        self.kind = kind

    def __len__(self):
        return len(self.word)

    def __str__(self):
        return "<{}: '{}'>".format(self.kind, self.word)

    def __repr__(self):
        return "<{}: '{}'>".format(self.kind, self.word)
