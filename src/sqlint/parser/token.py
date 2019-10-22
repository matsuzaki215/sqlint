from typing import TypeVar

T = TypeVar('T')


class Token:
    COMMA = 'Comma'
    DOT = 'Dot'
    BRACKET_LEFT = 'Left Bracket'
    BRACKET_RIGHT = 'Right Bracket'
    KEYWORD = 'Keyword'
    FUNCTION = 'Function'
    OPERATOR = 'Operator'
    COMMENT = 'Comment'
    IDENTIFIER = 'Identifier'
    WHITESPACE = 'Whitespace'
    UNKNOWN = 'Unknown'

    def __init__(self, word: str, kind: str = UNKNOWN):
        self.word: str = word
        self.kind: str = kind

    def __len__(self) -> int:
        return len(self.word)

    def __str__(self) -> str:
        return f'< {self.kind}: {self.word} >'

    def __repr__(self) -> str:
        return f'token.Token("{self.word}", {self.kind})'

    def __eq__(self, other: T) -> bool:
        if isinstance(other, str):
            return self.word == str(other)
        if isinstance(other, Token):
            return self.word.upper() == other.word.upper() and self.kind == other.kind

        return False
