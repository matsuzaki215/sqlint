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

        return IndentStepsChecker._check(tree.root, indent_steps)

    @staticmethod
    def _check(node: Node, indent_steps: int) -> List[Violation]:
        violation_list: List[Violation] = list()

        for leaf in node.leaves:
            if leaf.indent % indent_steps != 0:
                v = violation.IndentStepsViolation(leaf, expected=indent_steps, actual=leaf.indent)
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

        return KeywordStyleChecker._check(tree.root, keyword_style)

    @staticmethod
    def _check(node: Node, keyword_style: str) -> List[Violation]:
        violation_list: List[Violation] = list()

        for leaf in node.leaves:
            for idx, token in enumerate(leaf.contents):
                if token.kind != Token.KEYWORD:
                    continue

                word: str = token.word
                expected: str = KeywordStyleChecker.get_expected(word, keyword_style)
                if word != expected:
                    params = {'index': idx, 'actual': word, 'expected': expected}
                    v = violation.KeywordStyleViolation(leaf, keyword_style, **params)
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
        result.extend(CommaChecker._check_position(tree.root, comma_position))

        return result

    @staticmethod
    def _check_position(node: Node, comma_position: str) -> List[Violation]:
        violation_list: List[Violation] = list()

        lb = Token('(', Token.BRACKET_LEFT)
        rb = Token(')', Token.BRACKET_RIGHT)

        for leaf in node.leaves:
            # removes whitespaces and comments at head and end of line.
            ltripped = leaf.ltrip_kind(Token.WHITESPACE, Token.COMMENT)
            lindex = len(leaf.contents) - len(ltripped.contents)

            tokens = ltripped.rtrip_kind(Token.WHITESPACE, Token.COMMENT).contents
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
                    violation_list.append(violation.CommaPositionViolation(leaf, comma_position, index=(lindex+idx)))

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
        result.extend(WhitespaceChecker._check_multiple(tree.root))

        # 2. Whether a Whitespace is after a comma and not before it.
        result.extend(WhitespaceChecker._check_comma(tree.root))

        # 3. Whether a Whitespace is after and before bracket.
        result.extend(WhitespaceChecker._check_bracket(tree.root))

        # 4. Whether a Whitespace is after and before operator.
        result.extend(WhitespaceChecker._check_operator(tree.root))

        return result

    @staticmethod
    def _check_multiple(node: Node) -> List[Violation]:
        violation_list: List[Violation] = list()

        for leaf in node.leaves:
            # ignores token at head of a line
            tokens = leaf.contents[1:]

            for idx, tk in enumerate(tokens):
                length = len(tk)
                # ignores except whitespaces
                if tk.kind != tk.WHITESPACE:
                    continue

                # 2 spaces before comment is valid
                if length == 2 and (idx+1 < len(tokens) and tokens[idx+1].kind == Token.COMMENT):
                    continue

                if length > 1:
                    v = violation.MultiSpacesViolation(leaf, index=idx)
                    violation_list.append(v)

            violation_list.extend(WhitespaceChecker._check_multiple(leaf))

        return violation_list

    @staticmethod
    def _check_comma(node: Node) -> List[Violation]:
        violation_list: List[Violation] = list()

        for leaf in node.leaves:
            # Comma at end of line dose not need to checked
            for idx, token in enumerate(leaf.contents[:-1]):
                if token.kind != Token.COMMA:
                    continue

                # Checks that a whitespace does not exist before comma.
                # However, when comma is at head of line, it is allowed that whitespace is before.
                if idx >= 2 and leaf.contents[idx-1].kind == Token.WHITESPACE:
                    violation_list.append(
                        violation.WhitespaceViolation(leaf, token=Token.COMMA, position='before', index=idx))

                # checks whether a whitespace exists after comma.
                if leaf.contents[idx+1].kind != Token.WHITESPACE:
                    params = {'index': idx, 'target': f'{token.word}{leaf.contents[idx+1].word}'}
                    violation_list.append(
                        violation.WhitespaceViolation(leaf, token=Token.COMMA, position='after', **params))

            violation_list.extend(
                WhitespaceChecker._check_comma(leaf))

        return violation_list

    @staticmethod
    def _check_bracket(node: Node) -> List[Violation]:
        violation_list: List[Violation] = list()

        for leaf in node.leaves:
            # Comma at end of line dose not need to checked
            for idx, token in enumerate(leaf.contents[:-1]):
                # Checks whether a whitespace does not exist after left-bracket "( ".
                if token.kind == Token.BRACKET_LEFT \
                        and leaf.contents[idx+1].kind == Token.WHITESPACE:
                    params = {'index': idx, 'target': f'{token.word}{leaf.contents[idx+1].word}'}
                    violation_list.append(
                        violation.WhitespaceViolation(leaf, token=Token.BRACKET_LEFT, position='after', **params))

                # Checks whether a whitespace does not exist before right-bracket " )".
                if token.kind == Token.BRACKET_RIGHT \
                        and (idx >= 2 and leaf.contents[idx-1].kind == Token.WHITESPACE):
                    params = {'index': idx, 'target': f'{leaf.contents[idx-1].word}{token.word}'}
                    violation_list.append(
                        violation.WhitespaceViolation(leaf, token=Token.BRACKET_RIGHT, position='before', **params))

            violation_list.extend(
                WhitespaceChecker._check_bracket(leaf))

        return violation_list

    @staticmethod
    def _check_operator(node: Node) -> List[Violation]:
        violation_list: List[Violation] = list()

        for leaf in node.leaves:
            # Comma at end of line dose not need to checked
            for idx, token in enumerate(leaf.contents[:-1]):
                if token.kind != Token.OPERATOR:
                    continue

                # Checks whether a whitespace exists before operator.
                if idx >= 2 and leaf.contents[idx-1].kind != Token.WHITESPACE:
                    params = {'index': idx, 'target': f'{leaf.contents[idx-1].word}{token.word}'}
                    violation_list.append(
                        violation.WhitespaceViolation(leaf, token=Token.OPERATOR, position='before', **params))

                # Checks whether a whitespace exists after operator.
                if leaf.contents[idx + 1].kind != Token.WHITESPACE:
                    params = {'index': idx, 'target': f'{token.word}{leaf.contents[idx + 1].word}'}
                    violation_list.append(
                        violation.WhitespaceViolation(leaf, token=Token.OPERATOR, position='after', **params))

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
        result.extend(JoinChecker._check_table_name(tree.root))

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

        result.extend(JoinChecker._check_context(tree.root, expected_list))

        return result

    @staticmethod
    def _check_table_name(node: Node) -> List[Violation]:
        """Checks the token next to 'Join' is identifier(maybe table_name) or SubQuery """
        violation_list: List[Violation] = list()

        for leaf in node.leaves:
            for idx, token in enumerate(leaf.contents):
                # ignores except join
                if token.word.upper() != 'JOIN':
                    continue

                # ignores the token next to 'JOIN' is identifier which may be table.
                if idx <= len(leaf.contents)-2 and leaf.contents[idx+2].kind == Token.IDENTIFIER:
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

                v = violation.JoinTableViolation(leaf, index=idx)
                violation_list.append(v)

            violation_list.extend(JoinChecker._check_table_name(leaf))

        return violation_list

    @staticmethod
    def _check_context(node: Node, expected_list: Dict[str, str]) -> List[Violation]:
        """Checks whether join are described fully, for example [inner join], [left outer join], [right outer join] """
        violation_list: List[Violation] = list()

        for leaf in node.leaves:
            join_indexes = [i for i, x in enumerate(leaf.contents) if x.word.upper() == 'JOIN']

            for idx in join_indexes:
                token = leaf.contents[idx]
                # ignores except join
                if token.kind != Token.KEYWORD or token.word.upper() != 'JOIN':
                    continue

                # concat keyword concerned with join
                join_contexts = [token.word]
                expected: str = expected_list['inner']
                for tk in reversed(leaf.contents[:idx]):
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
                    params = {'index': idx, 'actual': join_context_str, 'expected': expected}
                    v = violation.JoinContextViolation(leaf, **params)
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
        blank_count, v_list = LineChecker._check_blank_line(tree.root, blank_count=0)
        if blank_count >= 2:
            v_list
        result.extend()

        # 2. Checks whether breaking line after specified keywords.
        # TODO: Implement

        return result

    @staticmethod
    def _check_blank_line(node: Node, blank_count: int) -> Tuple[int, List[Violation]]:
        violation_list: List[Violation] = []

        count = len(node.contents)

        is_blank = (count == 0)

        if count == 1 and node.contents[0].kind == Token.WHITESPACE:
            violation_list.append(violation.OnlyWhitespaceViolation(node, index=0))
            is_blank = True

        # If this line is not blank and 2 or more previous lines are blank, stack violation.
        if is_blank:
            blank_count += 1
        elif blank_count >= 2:
            violation_list.append(violation.MultiBlankLineViolation(node, index=0))

        for leaf in node.leaves:
            LineChecker._check_blank_line(tree.root, blank_count=0))


        return blank_count, violation_list
