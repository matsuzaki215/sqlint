from typing import Dict
from enum import Enum

from src.parser.syntax_tree import Node
from src.parser.token import Token


class Code(Enum):
    # E1: Indentation
    INDENT_STEPS = ('E101', 'indent steps must be {expected} multiples, but {actual} spaces')
    # E2: Whitespaces
    MULTIPLE_SPACE = ('E201', 'too many whitespaces')
    WHITESPACE_AFTER_COMMA = ('E202', 'whitespace must be after comma: {target}')
    WHITESPACE_BEFORE_COMMA = ('E203', 'whitespace must not be before comma: ,')
    WHITESPACE_AFTER_BRACKET = ('E204', 'whitespace must not be after bracket: {target}')
    WHITESPACE_BEFORE_BRACKET = ('E205', 'whitespace must not be before bracket: {target}')
    WHITESPACE_AFTER_OPERATOR = ('E206', 'whitespace must be after binary operator: {target}')
    WHITESPACE_BEFORE_OPERATOR = ('E207', 'whitespace must be after binary operator: {target}')
    # E3: Comma
    COMMA_HEAD = ('E301', 'comma must be head of line')
    COMMA_END = ('E302', 'comma must be end of line')
    # E4: Reserved Keyword
    KEYWORD_UPPER = ('E401', 'reserved keywords must be upper case: {actual} -> {expected}')
    KEYWORD_UPPER_HEAD = ('E402', 'a head of reserved keywords must be upper case: {actual} -> {expected}')
    KEYWORD_LOWER = ('E403', 'reserved keywords must be lower case: {actual} -> {expected}')
    # E5: Join Context
    JOIN_TABLE = ('E501', 'table_name must be at the same line as join context')
    JOIN_CONTEXT = ('E502', 'join context must be fully: {actual} -> {expected}')
    # E6: Brake line
    BREAK_LINE = ('E606', 'expected to break a line before \'and\', \'or\', \'on\'')

    def __init__(self, code: str, template: str):
        """
        Args:
            code: violation code
            template: violation template message
        """
        self.code = code
        self.template = template

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, value: str):
        self._code = value

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, value: str):
        self._template = value


class Violation:
    def __init__(self, node: Node, code: Code, **kwargs):
        self.node: Node = node
        self.code: Code = code
        self.params: Dict = kwargs

    def get_message(self):
        _template = '(L{line}, {pos}): ' + self.code.template
        self.params['pos'] = self.node.get_position(self.params['index'])

        return _template.format(
            line=self.node.line_num,
            **self.params)


class IndentStepsViolation(Violation):
    def __init__(self, node: Node, **kwargs):
        super().__init__(node, Code.INDENT_STEPS, **kwargs)
        self.params['index'] = 0


class KeywordStyleViolation(Violation):
    def __init__(self, node: Node, style: str, **kwargs):
        self.style = style

        if style == 'upper-all':
            _code = Code.KEYWORD_UPPER
        elif style == 'upper-head':
            _code = Code.KEYWORD_UPPER_HEAD
        elif style == 'lower':
            _code = Code.KEYWORD_LOWER
        else:
            raise ValueError('keyword style must be in [upper-all, upper-head, lower]')

        super().__init__(node, _code, **kwargs)


class CommaPositionViolation(Violation):
    def __init__(self, node: Node, comma_position: str, **kwargs):
        self.comma_position = comma_position

        if comma_position == 'head':
            _code = Code.COMMA_HEAD
        elif comma_position == 'end':
            _code = Code.COMMA_END
        else:
            raise ValueError('position must be in [head, end]')

        super().__init__(node, _code, **kwargs)


class MultiSpacesViolation(Violation):
    def __init__(self, node: Node, **kwargs):
        super().__init__(node, Code.MULTIPLE_SPACE, **kwargs)


class WhitespaceViolation(Violation):
    def __init__(self, node: Node, token: str, position: str, **kwargs):
        # TODO: modify more simple, maybe it is better to split several classes.
        if token == Token.COMMA:
            if position == 'before':
                _code = Code.WHITESPACE_BEFORE_COMMA
            elif position == 'after':
                _code = Code.WHITESPACE_AFTER_COMMA
            else:
                raise ValueError('whitespace position must be in [before, after]')
        elif token == Token.BRACKET_LEFT:
            _code = Code.WHITESPACE_AFTER_BRACKET
        elif token == Token.BRACKET_RIGHT:
            _code = Code.WHITESPACE_BEFORE_BRACKET
        elif token == Token.OPERATOR:
            if position == 'before':
                _code = Code.WHITESPACE_BEFORE_OPERATOR
            elif position == 'after':
                _code = Code.WHITESPACE_AFTER_OPERATOR
            else:
                raise ValueError('whitespace position must be in [before, after]')
        else:
            raise ValueError('token kind must be in [{}, {}, {}, {}]'.format(
                Token.COMMA, Token.BRACKET_LEFT, Token.BRACKET_RIGHT, Token.OPERATOR))

        super().__init__(node, _code, **kwargs)


class JoinTableViolation(Violation):
    def __init__(self, node: Node, **kwargs):
        super().__init__(node, Code.JOIN_TABLE, **kwargs)


class JoinContextViolation(Violation):
    def __init__(self, node: Node, **kwargs):
        super().__init__(node, Code.JOIN_CONTEXT, **kwargs)
