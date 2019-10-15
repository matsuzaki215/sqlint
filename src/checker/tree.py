from typing import List

from . import base
from .violation import Violation
from src.parser.syntax_tree import SyntaxTree
from src.config.config_loader import ConfigLoader


def check(tree: SyntaxTree, config: ConfigLoader):
    """Checks syntax tree and returns error messages

    Args:
        tree:
        config:

    Returns:

    """

    violation_list: List[Violation] = []

    checker_list = [
        # Check whether indent steps are N times.
        base.IndentStepsChecker,
        # Check whitespaces
        # 1. Check whether a whitespace exists after comma and not before .
        base.WhitespaceChecker,
        # Check whether reserved keywords is capital or not (default: not capital).
        base.KeywordStyleChecker,
        # Check whether comma, which connects some columns or conditions, is head(end) of line.
        base.CommaChecker,
        # Check about join context
        base.JoinChecker
    ]

    for checker in checker_list:
        violation_list.extend(checker.check(tree, config))

    for vi in violation_list:
        print(vi.get_message())

    # parse sql context
    # parsed_tokens = exec_parser(stmt)
    """
    blank_line_num = 0
    line_num = 1
    for tokens in parsed_tokens:
        # the position of a head of token in the line.
        position = 1
        # not suggest to break line as comma in bracket nest
        bracket_nest_count = 0

        # no tokens or only whitespace
        if (len(tokens) == 0 or
           (len(tokens) == 1 and tokens[0].kind == Token.WHITESPACE)):
            blank_line_num += 1
        else:
            if blank_line_num >= 2:
                result.append('(L{}, {}): {} ({})'.format(line_num, 0, 'too many blank lines', blank_line_num))
            blank_line_num = 0

        for i, token in enumerate(tokens):
            # debug
            # logger.debug('L{}:{}: {}'.format(line_num, position, token))

            if token.kind == Token.COMMENT:
                continue

            if token.word == '(':
                bracket_nest_count += 1
            if token.word == ')':
                bracket_nest_count -= 1

            # Check whether a whitespace exists not before ) or after (
            result.extend(_check_whitespace_brackets(line_num, position, tokens, i))

            # Check whether a whitespace exist before and after binary operators
            # (e.g.) =, <, >, <=. >=. <>, !=, +, -, *, /, %
            result.extend(_check_whitespace_operators(line_num, position, tokens, i))

            # Check whether the table name is on the same line as join context
            result.extend(_check_join_table(line_num, position, tokens, i))

            # Check whether join context is [left outer join], [inner join] or [cross join]
            result.extend(_check_join_context(line_num, position, tokens, i))

            # Check whether break line at 'and', 'or', 'on' (except between A and B)
            if bracket_nest_count == 0:
                result.extend(_check_break_line(line_num, position, tokens, i))

            # TODO: Not Implemented yet.
            # join on での不等号の順番（親テーブル < 日付）
            # join on での改行
            # 予約語ごとに、適切なインデントがされているか
            # サブクエリは外に出す
            # エイリアスが予約語と一致していないか
            # Suggestion: 定数のハードコーディングをやめる

            position += len(token)

        line_num += 1

    if blank_line_num >= 2:
        result.append('(L{}, {}): {} ({})'.format(line_num, 0, 'too many blank lines', blank_line_num))

    # Display 'Yey' message if there's no mistake.
    if len(result) == 0:
        result.append('Yey! You made no mistake🍺')

    return result
    """
