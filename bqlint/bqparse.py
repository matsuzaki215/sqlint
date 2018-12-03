import click
import logging
import re

from .config import (
    RESERVED_KEYWORDS,
    RESERVED_FUNCTIONS,
    BINARY_OPERATORS_ESCAPED,
)

# setting logger
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

PATTERN_COMMA = '(\s*)(,)(\s*)'
PATTERN_BRACKET_LEFT = '(\s*)(\()(\s*)'
PATTERN_BRACKET_RIGHT = '(\s*)(\))(\s*)'
PATTERN_KEYWORD = '(\s*)({})(\(|\s+|$)'
PATTERN_OPERATOR = '(\s*)([{}]+)(\s*)'
PATTERN_COMMENT_SINGLE = '(\s*)(#.*)'
PATTERN_COMMENT_BEGIN = '(\s*)(/\*)'
PATTERN_COMMENT_END = '(.*?)(\*/)'
PATTERN_QUOTES = '(\s*)("\S*"|\'\S*\'|`\S*`)(\s*)'
PATTERN_IDENTIFIER = '(\s*)([^,\(\){}#\s]+)(\s*)'
PATTERN_WHITESPACE = '(\s*)'


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


class BQParse(object):
    def __init__(self):
        # compile matching patterns
        self.regex_comma = re.compile(PATTERN_COMMA)
        self.regex_bracket_left = re.compile(PATTERN_BRACKET_LEFT)
        self.regex_bracket_right = re.compile(PATTERN_BRACKET_RIGHT)
        self.regex_keywords = []
        for word in (set(RESERVED_KEYWORDS) | set(RESERVED_FUNCTIONS)):
            self.regex_keywords.append(re.compile(PATTERN_KEYWORD.format(word), re.IGNORECASE))
        pattern_binary_operators = ''.join(BINARY_OPERATORS_ESCAPED)
        self.regex_operator = re.compile(PATTERN_OPERATOR.format(pattern_binary_operators))
        self.regex_comment_single = re.compile(PATTERN_COMMENT_SINGLE)
        self.regex_comment_begin = re.compile(PATTERN_COMMENT_BEGIN)
        self.regex_comment_end = re.compile(PATTERN_COMMENT_END)
        self.regex_quotes = re.compile(PATTERN_QUOTES)
        self.regex_identifier = re.compile(PATTERN_IDENTIFIER.format(pattern_binary_operators))
        self.regex_whitespace = re.compile(PATTERN_WHITESPACE)

    def execute(self, files):
        """

        :param files: parse files
        """
        for f in files:
            result = self.parse(f)
            for i, tokens in enumerate(result):
                logger.info("L{}: {}".format(i, [str(tk) for tk in tokens]))

    def parse(self, filepath):
        """

        :param filepath:
        :return:
        """
        result = []

        with open(filepath, "r") as fp:
            is_comment_line = False
            for line in fp:
                tokens, is_comment_line = self.match_tokens(line.rstrip('\r\n'), is_comment_line)
                result.append(tokens)

        return result

    def match_tokens(self, text, is_comment_line=False):
        """

        :param text:
        :param is_comment_line:
        :return:
        """
        tokens = []

        # check multi-line comment : /* comment */
        while len(text) > 0:
            # comment end (*/)
            if is_comment_line:
                match = re.search(self.regex_comment_end, text)
                if match:
                    if len(match.group(1)) > 0:
                        tokens.append(Token(match.group(1), Token.COMMENT))
                    tokens.append(Token(match.group(2), Token.COMMENT))
                    text = text[match.end():]
                    is_comment_line = False
                    continue
                else:
                    tokens.append(Token(text, Token.COMMENT))
                    break

            # comment begin (/*)
            match = re.match(self.regex_comment_begin, text)
            if match:
                if len(match.group(1)) > 0:
                    tokens.append(Token(match.group(1), Token.WHITESPACE))
                tokens.append(Token(match.group(2), Token.COMMENT))
                text = text[match.end():]
                is_comment_line = True
                continue

            # comment single(#)
            match = re.match(self.regex_comment_single, text)
            if match:
                if len(match.group(1)) > 0:
                    tokens.append(Token(match.group(1), Token.WHITESPACE))
                tokens.append(Token(match.group(2), Token.COMMENT))
                text = text[match.end():]
                continue

            # comma
            match = re.match(self.regex_comma, text)
            if match:
                if len(match.group(1)) > 0:
                    tokens.append(Token(match.group(1), Token.WHITESPACE))
                tokens.append(Token(match.group(2), Token.COMMA))
                if len(match.group(3)) > 0:
                    tokens.append(Token(match.group(3), Token.WHITESPACE))
                text = text[match.end():]
                continue

            # bracket_left
            match = re.match(self.regex_bracket_left, text)
            if match:
                if len(match.group(1)) > 0:
                    tokens.append(Token(match.group(1), Token.WHITESPACE))
                tokens.append(Token(match.group(2), Token.BRACKET))
                if len(match.group(3)) > 0:
                    tokens.append(Token(match.group(3), Token.WHITESPACE))
                text = text[match.end():]
                continue

            # bracket_right
            match = re.match(self.regex_bracket_right, text)
            if match:
                if len(match.group(1)) > 0:
                    tokens.append(Token(match.group(1), Token.WHITESPACE))
                tokens.append(Token(match.group(2), Token.BRACKET))
                if len(match.group(3)) > 0:
                    tokens.append(Token(match.group(3), Token.WHITESPACE))
                text = text[match.end():]
                continue

            # keywords
            for regex in self.regex_keywords:
                match = re.match(regex, text)
                if match:
                    break
            if match:
                if len(match.group(1)) > 0:
                    tokens.append(Token(match.group(1), Token.WHITESPACE))
                tokens.append(Token(match.group(2), Token.KEYWORD))
                if match.group(3) == '(':
                    tokens.append(Token(match.group(3), Token.BRACKET))
                elif len(match.group(3)) > 0:
                    tokens.append(Token(match.group(3), Token.WHITESPACE))
                text = text[match.end():]
                continue

            # operator
            match = re.match(self.regex_operator, text)
            if match:
                if len(match.group(1)) > 0:
                    tokens.append(Token(match.group(1), Token.WHITESPACE))
                tokens.append(Token(match.group(2), Token.OPERATOR))
                if len(match.group(3)) > 0:
                    tokens.append(Token(match.group(3), Token.WHITESPACE))
                text = text[match.end():]
                continue

            # quotes (as identifier )
            match = re.match(self.regex_quotes, text)
            if match:
                if len(match.group(1)) > 0:
                    tokens.append(Token(match.group(1), Token.WHITESPACE))
                tokens.append(Token(match.group(2), Token.IDENTIFIER))
                if len(match.group(3)) > 0:
                    tokens.append(Token(match.group(3), Token.WHITESPACE))
                text = text[match.end():]
                continue

            # identifier
            match = re.match(self.regex_identifier, text)
            if match:
                if len(match.group(1)) > 0:
                    tokens.append(Token(match.group(1), Token.WHITESPACE))
                tokens.append(Token(match.group(2), Token.IDENTIFIER))
                if len(match.group(3)) > 0:
                    tokens.append(Token(match.group(3), Token.WHITESPACE))
                text = text[match.end():]
                continue

            # blank
            match = re.match(self.regex_whitespace, text)
            if match:
                if len(match.group(1)) > 0:
                    tokens.append(Token(match.group(1), Token.WHITESPACE))
                text = text[match.end():]
                continue

        return tokens, is_comment_line


@click.command(context_settings={"ignore_unknown_options": True})
@click.argument('files', nargs=-1, type=click.Path())
def main(files):
    """

    :param files:
    :return:
    """
    bqlint = BQParse()
    bqlint.execute(files)


if __name__ == '__main__':
    main()
