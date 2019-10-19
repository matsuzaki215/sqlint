from abc import ABCMeta, abstractmethod
from typing import Dict, List, Tuple

from . import violation
from .violation import Violation
from src.parser.syntax_tree import SyntaxTree, Node
from src.parser.token import Token
from src.config.config_loader import ConfigLoader


class Checker(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def check(tree: SyntaxTree, config: ConfigLoader) -> List[Violation]:
        pass


class IndentStepsChecker(Checker):
    @staticmethod
    def check(tree: SyntaxTree, config: ConfigLoader) -> List[Violation]:
        # TODO: Enable users to ignore violation cases by config.

        # Checks whether indent steps are N times.
        indent_steps = config.get('indent-steps', 4)

        return IndentStepsChecker._check(tree, indent_steps)

    @staticmethod
    def _check(tree: SyntaxTree, indent_steps: int) -> List[Violation]:
        violation_list: List[Violation] = list()

        for leaf in tree.leaves:
            if leaf.indent % indent_steps != 0:
                v = violation.IndentStepsViolation(
                    line=leaf.node.line_num,
                    pos=1,
                    expected=indent_steps,
                    actual=leaf.indent)
                violation_list.append(v)

            violation_list.extend(
                IndentStepsChecker._check(leaf, indent_steps))

        return violation_list


class KeywordStyleChecker(Checker):
    """Checks reserved keywords style.

    Whether reserved keywords match one of following formats.
        - lower: e.g)  select
        - upper-all: e.g) SELECT
        - upper-head: e.g) Select
    """
    @staticmethod
    def check(tree: SyntaxTree, config: ConfigLoader) -> List[Violation]:
        # TODO: Enable users to ignore violation cases by config.

        keyword_style = config.get('keyword-style', 'lower')

        return KeywordStyleChecker._check(tree, keyword_style)

    @staticmethod
    def _check(tree: SyntaxTree, keyword_style: str) -> List[Violation]:
        violation_list: List[Violation] = list()

        for leaf in tree.leaves:
            for idx, token in enumerate(leaf.tokens):
                if token.kind != Token.KEYWORD:
                    continue

                word: str = token.word
                expected: str = KeywordStyleChecker.get_expected(word, keyword_style)
                if word != expected:
                    pos = leaf.get_position(idx)
                    params = {'style': keyword_style, 'actual': word, 'expected': expected}

                    v = violation.KeywordStyleViolation(
                        line=leaf.node.line_num,
                        pos=pos,
                        **params)
                    violation_list.append(v)

            violation_list.extend(
                KeywordStyleChecker._check(leaf, keyword_style))

        return violation_list

    @staticmethod
    def get_expected(keyword: str, keyword_style: str) -> str:
        expected: str = keyword

        if keyword_style == 'lower':
            expected = keyword.lower()
        if keyword_style == 'upper-all':
            expected = keyword.upper()
        if keyword_style == 'upper-head':
            expected = f'{keyword[0].upper()}{keyword[1:].lower()}'

        return expected


class CommaChecker(Checker):
    """ Checks violations about comma.

    1. Whether comma is head or end of a line.(default: head)
    """

    @staticmethod
    def check(tree: SyntaxTree, config: ConfigLoader) -> List[Violation]:
        # TODO: Enable users to ignore violation cases by config.

        comma_position = config.get('comma-position')

        result: List[Violation] = []

        # 1. Whether comma is head or end of a line.(default: head)
        result.extend(CommaChecker._check_position(tree, comma_position))

        return result

    @staticmethod
    def _check_position(tree: SyntaxTree, comma_position: str) -> List[Violation]:
        violation_list: List[Violation] = list()

        lb = Token('(', Token.BRACKET_LEFT)
        rb = Token(')', Token.BRACKET_RIGHT)

        for leaf in tree.leaves:
            # removes whitespaces and comments at head and end of line.
            ltripped_node: Node = leaf.node.ltrip_kind(Token.WHITESPACE, Token.COMMENT)
            lindex = len(leaf.node) - len(ltripped_node)

            tokens = ltripped_node.rtrip_kind(Token.WHITESPACE, Token.COMMENT).tokens
            comma_indexes = [i for i, x in enumerate(tokens) if x == ',']

            if comma_position == 'head':
                comma_indexes = [i for i in comma_indexes if i != 0]
            elif comma_position == 'end':
                comma_indexes = [i for i in comma_indexes if i != len(tokens)-1]

            for idx in comma_indexes:
                # If a comma is in brackets, it is appropriate not to break a line at comma.
                # So determines that by counting left- and right- brackets at left-right-side.
                is_open_bracket = 0 < (tokens[0:idx].count(lb) - tokens[0:idx].count(rb))
                is_close_bracket = 0 < (tokens[idx+1:].count(rb) - tokens[idx+1:].count(lb))

                if not is_open_bracket or not is_close_bracket:
                    pos = leaf.get_position(lindex+idx)
                    violation_list.append(
                        violation.CommaPositionViolation(
                            line=leaf.node.line_num,
                            pos=pos,
                            comma_position=comma_position))

            violation_list.extend(
                CommaChecker._check_position(leaf, comma_position))

        return violation_list


class WhitespaceChecker(Checker):
    """ Checks violations about whitespace.

    1. Whether multiple whitespaces exist.
    2. Whether a Whitespace is after a comma and not before it.
    3. Whether a Whitespace is after a bracket and not before it.
    4. Whether a Whitespace is after a operator and not before it.

    """

    @staticmethod
    def check(tree: SyntaxTree, config: ConfigLoader) -> List[Violation]:
        # TODO: Enable users to ignore violation cases by config.
        result: List[Violation] = []

        # 1. Whether comma is head or end of a line.(default: head)
        result.extend(WhitespaceChecker._check_multiple(tree))

        # 2. Whether a Whitespace is after a comma and not before it.
        result.extend(WhitespaceChecker._check_comma(tree))

        # 3. Whether a Whitespace is after and before bracket.
        result.extend(WhitespaceChecker._check_bracket(tree))

        # 4. Whether a Whitespace is after and before operator.
        result.extend(WhitespaceChecker._check_operator(tree))

        return result

    @staticmethod
    def _check_multiple(tree: SyntaxTree) -> List[Violation]:
        violation_list: List[Violation] = list()

        for leaf in tree.leaves:
            # ignores token at head of a line
            tokens = leaf.tokens[1:]

            for idx, tk in enumerate(tokens):
                length = len(tk)
                # ignores except whitespaces
                if tk.kind != tk.WHITESPACE:
                    continue

                # 2 spaces before comment is valid
                if length == 2 and (idx+1 < len(tokens) and tokens[idx+1].kind == Token.COMMENT):
                    continue

                if length > 1:
                    pos = leaf.get_position(idx)
                    v = violation.MultiSpacesViolation(leaf.node.line_num, pos)
                    violation_list.append(v)

            violation_list.extend(WhitespaceChecker._check_multiple(leaf))

        return violation_list

    @staticmethod
    def _check_comma(tree: SyntaxTree) -> List[Violation]:
        violation_list: List[Violation] = list()

        for leaf in tree.leaves:
            # Comma at end of line dose not need to checked
            for idx, token in enumerate(leaf.tokens[:-1]):
                if token.kind != Token.COMMA:
                    continue

                # Checks that a whitespace does not exist before comma.
                # However, when comma is at head of line, it is allowed that whitespace is before.
                if idx >= 2 and leaf.tokens[idx-1].kind == Token.WHITESPACE:
                    pos = leaf.get_position(idx)
                    params = {'token': Token.COMMA,
                              'position': 'before'}
                    violation_list.append(
                        violation.WhitespaceViolation(
                            line=leaf.node.line_num,
                            pos=pos,
                            **params))

                # checks whether a whitespace exists after comma.
                if leaf.tokens[idx+1].kind != Token.WHITESPACE:
                    pos = leaf.get_position(idx)
                    params = {'token': Token.COMMA,
                              'position': 'after',
                              'target': f'{token.word}{leaf.tokens[idx+1].word}'}
                    violation_list.append(
                        violation.WhitespaceViolation(
                            line=leaf.node.line_num,
                            pos=pos,
                            **params))

            violation_list.extend(
                WhitespaceChecker._check_comma(leaf))

        return violation_list

    @staticmethod
    def _check_bracket(tree: SyntaxTree) -> List[Violation]:
        violation_list: List[Violation] = list()

        for leaf in tree.leaves:
            # Comma at end of line dose not need to checked
            for idx, token in enumerate(leaf.tokens[:-1]):
                # Checks whether a whitespace does not exist after left-bracket "( ".
                if token.kind == Token.BRACKET_LEFT \
                        and leaf.tokens[idx+1].kind == Token.WHITESPACE:
                    pos = leaf.get_position(idx)
                    params = {'token': Token.BRACKET_LEFT,
                              'position': 'after',
                              'target': f'{token.word}{leaf.tokens[idx+1].word}'}
                    violation_list.append(
                        violation.WhitespaceViolation(line=leaf.node.line_num, pos=pos, **params))

                # Checks whether a whitespace does not exist before right-bracket " )".
                if token.kind == Token.BRACKET_RIGHT \
                        and (idx >= 2 and leaf.tokens[idx-1].kind == Token.WHITESPACE):
                    pos = leaf.get_position(idx)
                    params = {
                        'token': Token.BRACKET_RIGHT,
                        'position': 'before',
                        'target': f'{leaf.tokens[idx-1].word}{token.word}'}
                    violation_list.append(
                        violation.WhitespaceViolation(
                            line=leaf.node.line_num,
                            pos=pos,
                            **params))

            violation_list.extend(
                WhitespaceChecker._check_bracket(leaf))

        return violation_list

    @staticmethod
    def _check_operator(tree: SyntaxTree) -> List[Violation]:
        violation_list: List[Violation] = list()

        for leaf in tree.leaves:
            # Comma at end of line dose not need to checked
            for idx, token in enumerate(leaf.tokens[:-1]):
                if token.kind != Token.OPERATOR:
                    continue

                # Checks whether a whitespace exists before operator.
                if idx >= 2 and leaf.tokens[idx-1].kind != Token.WHITESPACE:
                    pos = leaf.get_position(idx)
                    params = {
                        'token': Token.OPERATOR,
                        'position': 'before',
                        'target': f'{leaf.tokens[idx-1].word}{token.word}'}
                    violation_list.append(
                        violation.WhitespaceViolation(line=leaf.node.line_num, pos=pos, **params))

                # Checks whether a whitespace exists after operator.
                if leaf.tokens[idx + 1].kind != Token.WHITESPACE:
                    pos = leaf.get_position(idx)
                    params = {
                        'token': Token.OPERATOR,
                        'position': 'after',
                        'target': f'{token.word}{leaf.tokens[idx + 1].word}'}
                    violation_list.append(
                        violation.WhitespaceViolation(line=leaf.node.line_num, pos=pos, **params))

            violation_list.extend(
                WhitespaceChecker._check_operator(leaf))

        return violation_list


class JoinChecker(Checker):
    """ Checks violations about join context.

    1. Whether join context and table name are same line.
    2. Whether join contexts are described fully, for example [inner join], [left outer join], [right outer join]

    """

    @staticmethod
    def check(tree: SyntaxTree, config: ConfigLoader) -> List[Violation]:
        # TODO: Enable users to ignore violation cases by config.
        result: List[Violation] = []

        # 1. Whether join context and table name are same line.
        result.extend(JoinChecker._check_table_name(tree))

        # 2. Whether join contexts are described fully, for example [inner join], [left outer join], [right outer join]
        keyword_style = config.get('keyword-style', 'lower')
        expected_kvs = {
            'left': ['left', 'outer', 'join'],
            'outer': ['left', 'outer', 'join'],
            'right': ['right', 'outer', 'join'],
            'inner': ['inner', 'join'],
            'cross': ['cross', 'join'],
        }
        expected_list = {}
        for k, vs in expected_kvs.items():
            expected_list[k] = ' '.join([
                KeywordStyleChecker.get_expected(v, keyword_style) for v in vs])

        result.extend(JoinChecker._check_context(tree, expected_list))

        return result

    @staticmethod
    def _check_table_name(tree: SyntaxTree) -> List[Violation]:
        """Checks the token next to 'Join' is identifier(maybe table_name) or SubQuery """
        violation_list: List[Violation] = list()

        for leaf in tree.leaves:
            for idx, token in enumerate(leaf.tokens):
                # ignores except join
                if token.word.upper() != 'JOIN':
                    continue

                # ignores the token next to 'JOIN' is identifier which may be table.
                if idx <= len(leaf.tokens)-2 and leaf.tokens[idx+2].kind == Token.IDENTIFIER:
                    continue

                # TODO: Checks below
                # TODO: SubQueries will become violation in the future.
                """
                Ignores the token next to 'Join' is 'Select' (maybe SubQuery)
                Examples:
                    1) ------
                    From
                        x
                        Join Select id From y
                    ------
                    2) ------
                    From
                        x
                        Join (Select id From y)
                    ------
                """
                pos = leaf.get_position(idx)
                v = violation.JoinTableViolation(line=leaf.node.line_num, pos=pos)
                violation_list.append(v)

            violation_list.extend(JoinChecker._check_table_name(leaf))

        return violation_list

    @staticmethod
    def _check_context(tree: SyntaxTree, expected_list: Dict[str, str]) -> List[Violation]:
        """Checks whether join are described fully, for example [inner join], [left outer join], [right outer join] """
        violation_list: List[Violation] = list()

        for leaf in tree.leaves:
            join_indexes = [i for i, x in enumerate(leaf.tokens) if x.word.upper() == 'JOIN']

            for idx in join_indexes:
                token = leaf.tokens[idx]
                # ignores except join
                if token.kind != Token.KEYWORD or token.word.upper() != 'JOIN':
                    continue

                # concat keyword concerned with join
                join_contexts = [token.word]
                expected: str = expected_list['inner']
                for tk in reversed(leaf.tokens[:idx]):
                    if tk.kind == Token.WHITESPACE:
                        continue

                    if tk.word.upper() in ['INNER', 'OUTER', 'LEFT', 'RIGHT', 'CROSS']:
                        join_contexts.insert(0, tk.word)
                        if tk.word.lower() in expected_list:
                            expected = expected_list[tk.word.lower()]
                    else:
                        break

                join_context_str = ' '.join(join_contexts)
                if join_context_str.upper() not in ['INNER JOIN', 'RIGHT OUTER JOIN', 'LEFT OUTER JOIN', 'CROSS JOIN']:
                    pos = leaf.get_position(idx)
                    params = {'actual': join_context_str, 'expected': expected}
                    v = violation.JoinContextViolation(line=leaf.node.line_num, pos=pos, **params)
                    violation_list.append(v)

            violation_list.extend(JoinChecker._check_context(leaf, expected_list))

        return violation_list


class LineChecker(Checker):
    """Checks violations about lines management.

    1. Checks whether two or more blank lines exist.

    2. Checks whether breaking line after specified keywords.
    Examples:
    --- Good ---
    Select
        x
    From
        y
    ------------

    ---- NG ----
    Select x From y
    ------------
    """

    @staticmethod
    def check(tree: SyntaxTree, config: ConfigLoader) -> List[Violation]:
        result: List[Violation] = []

        # 1. Checks whether two or more blank lines exist.
        v_list, blank_count, last_node = LineChecker._check_blank_line(tree, blank_count=0)
        if blank_count >= 2:
            v_list.append(violation.MultiBlankLineViolation(last_node.line_num, pos=1))
        result.extend(v_list)

        # 2. Checks whether breaking line after specified keywords.
        # TODO: Implement

        return result

    @staticmethod
    def _check_blank_line(tree: SyntaxTree, blank_count: int) -> Tuple[List[Violation], int, Node]:
        violation_list: List[Violation] = []
        last_node = tree.node

        for leaf in tree.leaves:
            count = len(leaf.node)
            is_blank = (count == 0)

            if count == 1 and leaf.tokens[0].kind == Token.WHITESPACE:
                violation_list.append(violation.OnlyWhitespaceViolation(leaf.node.line_num, pos=1))

            # If this line is not blank and 2 or more previous lines are blank, stack violation.
            if is_blank:
                blank_count += 1
            elif blank_count >= 2:
                violation_list.append(violation.MultiBlankLineViolation(leaf.node.line_num-1, pos=1))
                blank_count = 0

            v_list, blank_count, last_node = LineChecker._check_blank_line(leaf, blank_count)
            violation_list.extend(v_list)

        return violation_list, blank_count, last_node
