import logging
from abc import ABCMeta, abstractmethod
from typing import List, TypeVar, Tuple

from sqlint.parser import Token
from sqlint.syntax_tree import SyntaxTree

T = TypeVar('T')

logger = logging.getLogger(__name__)


class Splitter(metaclass=ABCMeta):
    @abstractmethod
    def split(self, tokens: List[T], tree: SyntaxTree) -> Tuple[List[T], List[List[T]], List[T]]:
        raise NotImplementedError()

    @classmethod
    def split_other(cls, tokens: List[Token]) -> Tuple[List[Token], List[List[Token]], List[Token]]:
        """"""
        bracket_count = 0
        for idx, token in enumerate(tokens):
            bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
            bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)

            if bracket_count == 0 and token.kind in [Token.COMMA, Token.COMMENT]:
                return tokens[0:idx + 1], [], tokens[idx + 1:]

        return tokens, [], []


class IdentifierSplitter(Splitter):
    @classmethod
    def split(cls, tokens: List[Token], tree: SyntaxTree) -> Tuple[List[Token], List[List[Token]], List[Token]]:
        parent_tree = tree.parent

        logger.debug(tokens)

        if parent_tree is None or parent_tree.depth == 0:
            # The identifier placed on root depth is illegal case.
            return tokens[0:1], [], tokens[1:]

        # if parent tree is "FROM" sequence, explores "JOIN" sequences.
        from_token = Token(word='FROM', kind=Token.KEYWORD)
        if parent_tree.tokens[0] == from_token:
            return cls.split_from(tokens)

        return cls.split_other(tokens)

    @classmethod
    def split_from(cls, tokens: List[Token]) -> Tuple[List[Token], List[List[Token]], List[Token]]:
        join_tokens = [
            Token(word='INNER', kind=Token.KEYWORD),
            Token(word='LEFT', kind=Token.KEYWORD),
            Token(word='RIGHT', kind=Token.KEYWORD),
            Token(word='FULL', kind=Token.KEYWORD),
            Token(word='CROSS', kind=Token.KEYWORD),
            Token(word='OUTER', kind=Token.KEYWORD),
            Token(word='JOIN', kind=Token.KEYWORD)
        ]

        bracket_count = 0
        for idx, token in enumerate(tokens):
            bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
            bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)

            if token in join_tokens and bracket_count == 0:
                return tokens[0:idx], [], tokens[idx:]

        return cls.split_other(tokens)


class RightBrackerSplitter(Splitter):
    @classmethod
    def split(cls, tokens: List[Token], tree: SyntaxTree) -> Tuple[List[Token], List[List[Token]], List[Token]]:
        if len(tokens) >= 2 and tokens[1].word == ';':
            return tokens[0:2], [], tokens[2:]

        if tree.depth <= 1:
            return tokens[0:1], [], tokens[1:]

        return tokens[0:], [], []


class LongLineSplitter(Splitter):
    @classmethod
    def split(cls, tokens: List[Token], tree: SyntaxTree) -> Tuple[List[Token], List[List[Token]], List[Token]]:
        if tokens[0].word.upper() == 'WHEN':
            return cls._split_when(tokens)

        return cls._split(tokens)

    @classmethod
    def _split(cls, tokens: List[Token]) -> Tuple[List[Token], List[List[Token]], List[Token]]:
        lb_token = Token(word='(', kind=Token.BRACKET_LEFT)
        try:
            left_index = tokens.index(lb_token)
        except ValueError:
            # Not Found left bracket, can't split the line
            return tokens, [], []

        bracket_count = 1
        for idx, token in enumerate(tokens[left_index+1:]):
            bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
            bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)

            if bracket_count == 0:
                return (
                    tokens[0:left_index+1],
                    KeywordSelectSplitter.split_leaves(tokens[left_index+1:idx+left_index+1]),
                    # [tokens[left_index+1:idx+left_index+1]],
                    tokens[idx+left_index+1:]
                )

        return tokens, [], []

    @classmethod
    def _split_when(cls, tokens: List[Token]) -> Tuple[List[Token], List[List[Token]], List[Token]]:
        """Case - when"""

        then_token = Token(word='THEN', kind=Token.KEYWORD)

        bracket_count = 0
        for idx, token in enumerate(tokens):
            bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
            bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)

            if token == then_token and bracket_count == 0:
                return (
                    tokens[0:idx+1],
                    KeywordWhereSplitter.split_condiction(tokens[idx+1:]),
                    [])

        raise ValueError('"THEN" is requires one or more "WHEN" sequense')


class CommaSplitter(Splitter):
    @classmethod
    def split(cls, tokens: List[Token], tree: SyntaxTree) -> Tuple[List[Token], List[List[Token]], List[Token]]:
        parent_tree = tree.parent
        bracket_count = 0

        # TODO: implement following as Splitter and merges WITH-Splitter
        if parent_tree.depth == 0:
            # maybe this comma correspands to WITH sequence
            # expected
            # , {Identifier} AS ( {myquery ) ...
            as_token = Token(word='AS', kind=Token.KEYWORD)

            if len(tokens) <= 2:
                return tokens, [], []

            if tokens[0].kind != Token.COMMA:
                raise ValueError(f'a head of tokens must be "," sequence, but {tokens[0]}')

            if tokens[1].kind != Token.IDENTIFIER:
                # TODO: raises SQL error or check this as Violations
                raise ValueError(f'next of "WITH" or "," must be identifier, but {tokens[1]}')

            if tokens[2] != as_token:
                return tokens[0:2], [], tokens[2:]

            if tokens[3].kind != Token.BRACKET_LEFT:
                # TODO: raises SQL error or check this as Violations
                raise ValueError(f'next of "AS" must be "(" in "WITH" or "," sequence, but {tokens[3]}')

            # Explores tokens until branch is closed
            bracket_count = 1
            for idx, token in enumerate(tokens[4:]):
                bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
                bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)

                if bracket_count == 0:
                    return tokens[0:4], [tokens[4:idx + 4]], tokens[idx + 4:]

            return tokens[0:1], [], tokens[1:]

        # Explores next COMMA
        for idx, token in enumerate(tokens[1:]):
            bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
            bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)

            if token.kind == Token.COMMA and bracket_count == 0:
                return tokens[0:idx + 1], [], tokens[idx + 1:]

        return tokens, [], []


class KeywordSplitter(Splitter):
    @classmethod
    def split(cls, tokens: List[Token], tree: SyntaxTree) -> Tuple[List[Token], List[List[Token]], List[Token]]:
        head = tokens[0]

        if head.kind not in [Token.KEYWORD, Token.FUNCTION]:
            raise ValueError(f'token kind must be reserved KEYWORD or FUNCTION, but {head.kind}')

        key_functions = [
            (['CREATE'], cls._split_create),
            (['RETURNS'], cls._split_returns),
            (['LANGUAGE'], cls._split_language),
            (['AS'], cls._split_as),
            (['WITH'], cls._split_with),
            (['SELECT'], KeywordSelectSplitter.split_select),
            (['FROM'], cls._split_from),
            (['WHERE'], KeywordWhereSplitter.split_where),
            (['ORDER'], cls._split_order),
            (['GROUP'], cls._split_split),
            (['HAVING'], cls._split_having),
            (['CASE'], cls._split_case),
            (['WHEN'], cls._split_when),
            (['INNER', 'LEFT', 'RIGHT', 'FULL', 'CROSS', 'OUTER', 'JOIN'], KeywordJoinSplitter.split_join),
        ]

        word = head.word.upper()
        # Switches by specified keywords

        for keys, func in key_functions:
            if word in keys:
                return func(tokens)

        return tokens, [], []

    @classmethod
    def _split_create(cls, tokens: List[Token]) -> Tuple[List[Token], List[List[Token]], List[Token]]:
        stoppers = [
            Token(word='RETURNS', kind=Token.KEYWORD),
            Token(word='LANGUAGE', kind=Token.KEYWORD),
            Token(word='AS', kind=Token.KEYWORD),
        ]

        for stp in stoppers:
            try:
                index = tokens.index(stp, 1, -1)
                return tokens[0:index], [], tokens[index:]
            except ValueError:
                continue

        return tokens[0:1], [], tokens[1:]

    @classmethod
    def _split_returns(cls, tokens: List[Token]) -> Tuple[List[Token], List[List[Token]], List[Token]]:
        stoppers = [
            Token(word='LANGUAGE', kind=Token.KEYWORD),
            Token(word='AS', kind=Token.KEYWORD),
        ]

        for stp in stoppers:
            try:
                index = tokens.index(stp, 1, -1)
                return tokens[0:index], [], tokens[index:]
            except ValueError:
                continue

        return tokens[0:1], [], tokens[1:]

    @classmethod
    def _split_language(cls, tokens: List[Token]) -> Tuple[List[Token], List[List[Token]], List[Token]]:
        stoppers = [
            Token(word='AS', kind=Token.KEYWORD),
        ]

        for stp in stoppers:
            try:
                index = tokens.index(stp, 1, -1)
                return tokens[0:index], [], tokens[index:]
            except ValueError:
                continue

        return tokens[0:1], [], tokens[1:]

    @classmethod
    def _split_as(cls, tokens: List[Token]) -> Tuple[List[Token], List[List[Token]], List[Token]]:
        if len(tokens) <= 2:
            return tokens, [], []

        if tokens[1].kind != Token.BRACKET_LEFT:
            return tokens[0:2], [], tokens[2:]

        # Explores tokens until branch is closed
        bracket_count = 1
        for idx, token in enumerate(tokens[2:]):
            bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
            bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)

            if bracket_count == 0:
                return tokens[0:2], [tokens[2:idx+2]], tokens[idx+2:]

        return tokens[0:2], [], tokens[2:]

    @classmethod
    def _split_with(cls, tokens: List[Token]) -> Tuple[List[Token], List[List[Token]], List[Token]]:
        """Splits WITH sequence

        Examples:
        pattern.1
        ---
        WITH {Identifier} AS (
            myquery
        )
        ---

        pattern.2
        ---
        WITH {Identifier}
        ---

        Args:
            tokens:

        Returns:

        """
        as_token = Token(word='AS', kind=Token.KEYWORD)

        if len(tokens) <= 2:
            return tokens, [], []

        # TODO: Modify parser to soloved this mis-labbeling
        if tokens[1].kind in [Token.KEYWORD, Token.FUNCTION]:
            tokens[1].kind = Token.IDENTIFIER

        if tokens[1].kind != Token.IDENTIFIER:
            # TODO: raises SQL error or check this as Violations
            raise ValueError(f'next of "WITH" must be identifier, but {tokens[1]}')

        if tokens[2] != as_token:
            return tokens[0:2], [], tokens[2:]

        if tokens[3].kind != Token.BRACKET_LEFT:
            # TODO: raises SQL error or check this as Violations
            raise ValueError(f'next of "AS" must be "(" in "WITH" sequence, but {tokens[3]}')

        # Explores tokens until branch is closed
        bracket_count = 1
        for idx, token in enumerate(tokens[4:]):
            bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
            bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)

            if bracket_count == 0:
                return tokens[0:4], [tokens[4:idx+5]], tokens[idx+5:]

        return tokens[0:1], [tokens[1:]], []

    @classmethod
    def _split_from(cls, tokens: List[Token]) -> Tuple[List[Token], List[List[Token]], List[Token]]:
        """Splits FROM sequence

        Args:
            tokens:

        Returns:

        """

        from_token = Token(word='FROM', kind=Token.KEYWORD)
        stoppers = [
            Token(word='SELECT', kind=Token.KEYWORD),
            Token(word='WHERE', kind=Token.KEYWORD),
            Token(word='ORDER', kind=Token.KEYWORD),
            Token(word='GROUP', kind=Token.KEYWORD),
            Token(word='HAVING', kind=Token.KEYWORD),
        ]

        # Explores tokens until FROM is closed by condition sequence corresponding it.
        from_count = 1
        bracket_count = 0
        for idx, token in enumerate(tokens[1:]):
            bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
            bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)

            if token == from_token and bracket_count == 0:
                from_count += 1

            if token in stoppers and from_count == 1 and bracket_count == 0:
                if tokens[1].kind == Token.BRACKET_LEFT:
                    return tokens[0:2], [tokens[2:idx+1]], tokens[idx+1:]
                else:
                    return tokens[0:1], [tokens[1:idx + 1]], tokens[idx + 1:]

        return tokens[0:1], [tokens[1:]], []

    @classmethod
    def _split_split(cls, tokens: List[Token]) -> Tuple[List[Token], List[List[Token]], List[Token]]:
        """Splits GROIP BY sequence

        Args:
            tokens:

        Returns:

        """
        return tokens[0:2], [tokens[2:]], []

    @classmethod
    def _split_order(cls, tokens: List[Token]) -> Tuple[List[Token], List[List[Token]], List[Token]]:
        """Splits ORDER BY sequence

        Args:
            tokens:

        Returns:

        """
        return tokens[0:2], [tokens[2:]], []

    @classmethod
    def _split_having(cls, tokens: List[Token]) -> Tuple[List[Token], List[List[Token]], List[Token]]:
        """Splits ORDER BY sequence

        Args:
            tokens:

        Returns:

        """
        return tokens[0:1], [tokens[1:]], []

    @classmethod
    def _split_case(cls, tokens: List[Token]) -> Tuple[List[Token], List[List[Token]], List[Token]]:
        """Splits WHEN sequence

        Args:
            tokens:

        Returns:

        """

        case_token = Token(word='CASE', kind=Token.KEYWORD)
        when_token = Token(word='WHEN', kind=Token.KEYWORD)
        end_token = Token(word='END', kind=Token.KEYWORD)

        try:
            when_index = tokens.index(when_token)
        except ValueError:
            # TODO: raises SQL error or check this as Violations
            raise ValueError('"CASE" sequence requires one or more "WHEN" sequense')

        bracket_count = 0
        case_count = 1
        for idx, token in enumerate(tokens[when_index:]):
            bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
            bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)

            if token == case_token and bracket_count == 0:
                case_count += 1
            if token == end_token and case_count == 1 and bracket_count == 0:
                return tokens[0:when_index], [tokens[when_index:idx+when_index]], tokens[idx+when_index:]

        return tokens[0:when_index], [tokens[when_index:]], []

    @classmethod
    def _split_when(cls, tokens: List[Token]) -> Tuple[List[Token], List[List[Token]], List[Token]]:
        """Splits WHEN sequence

        Args:
            tokens:

        Returns:

        """

        case_token = Token(word='CASE', kind=Token.KEYWORD)
        when_token = Token(word='WHEN', kind=Token.KEYWORD)
        end_token = Token(word='END', kind=Token.KEYWORD)

        bracket_count = 0
        case_count = 1
        for idx, token in enumerate(tokens[1:]):
            bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
            bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)

            if bracket_count == 0:
                case_count += (1 if token == case_token else 0)
                case_count += (-1 if token == end_token else 0)

            if token == when_token and case_count <= 1 and bracket_count == 0:
                return tokens[0:idx+1], [], tokens[idx+1:]

        return tokens, [], []

    @classmethod
    def split_leaves(cls, tokens: List[Token]) -> List[List[Token]]:
        """Splits leaves of Select sequence
        """

        result = []

        bracket_count = 0
        start = 0
        for idx, token in enumerate(tokens):
            bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
            bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)

            if token.kind == Token.COMMA and bracket_count == 0:
                result.append(tokens[start:idx])
                start = idx

        if start < len(tokens):
            result.append(tokens[start:len(tokens)])

        return result


class KeywordSelectSplitter(KeywordSplitter):
    @classmethod
    def split_select(cls, tokens: List[Token]) -> Tuple[List[Token], List[List[Token]], List[Token]]:
        """Splits Select sequence

        Examples:
        ---
        SELECT
            {Identifier} AS {Identifier},
            {Identifier} AS {Identifier},
            {Identifier} AS {Identifier},
        FROM
        ---

        Args:
            tokens:

        Returns:

        """

        select_token = Token(word='SELECT', kind=Token.KEYWORD)
        stoppers = [
            Token(word='FROM', kind=Token.KEYWORD),
            Token(word='WHERE', kind=Token.KEYWORD),
            Token(word='ORDER', kind=Token.KEYWORD),
            Token(word='GROUP', kind=Token.KEYWORD),
            Token(word='HAVING', kind=Token.KEYWORD),
        ]

        # Explores tokens until SELECT is closed by FROM corresponding it.
        select_count = 1
        bracket_count = 0
        for idx, token in enumerate(tokens[1:]):
            bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
            bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)

            if token == select_token and bracket_count == 0:
                select_count += 1
            if token in stoppers and select_count == 1 and bracket_count == 0:
                return (
                    tokens[0:1],
                    cls.split_leaves(tokens[1:idx+1]),
                    tokens[idx+1:])

        return tokens[0:1], [tokens[1:]], []


class KeywordWhereSplitter(KeywordSplitter):
    @classmethod
    def split_where(cls, tokens: List[Token]) -> Tuple[List[Token], List[List[Token]], List[Token]]:
        """Splits WHERE sequence

        Args:
            tokens:

        Returns:

        """

        where_token = Token(word='WHERE', kind=Token.KEYWORD)
        stoppers = [
            Token(word='SELECT', kind=Token.KEYWORD),
            Token(word='ORDER', kind=Token.KEYWORD),
            Token(word='GROUP', kind=Token.KEYWORD),
            Token(word='HAVING', kind=Token.KEYWORD),
        ]

        # Explores tokens until FROM is closed by condition sequence corresponding it.
        where_count = 1
        bracket_count = 0
        for idx, token in enumerate(tokens[1:]):
            bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
            bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)

            if token == where_token and bracket_count == 0:
                where_count += 1

            if token in stoppers and where_count == 1 and bracket_count == 0:
                return (
                    tokens[0:1],
                    cls.split_condiction(tokens[1:idx+1]),
                    tokens[idx+1:])

        return tokens[0:1], cls.split_condiction(tokens[1:]), []

    @classmethod
    def split_condiction(cls, tokens: List[Token]) -> List[List[Token]]:
        """Splits ON or USING sequence

        Args:
            tokens:

        Returns:

        """

        case_token = Token(word='CASE', kind=Token.KEYWORD)
        end_token = Token(word='END', kind=Token.KEYWORD)
        and_token = Token(word='AND', kind=Token.KEYWORD)
        or_token = Token(word='OR', kind=Token.KEYWORD)
        between_tokens = Token(word='BETWEEN', kind=Token.KEYWORD)

        result = []

        case_count = 0
        between_count = 0
        bracket_count = 0
        start = 0
        for idx, token in enumerate(tokens):
            bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
            bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)
            if bracket_count > 0:
                continue

            if token.kind == Token.COMMENT and case_count == 0:
                result.append(tokens[start:idx])
                result.append(tokens[idx:idx+1])
                start = idx+1
                continue

            case_count += (1 if token == case_token else 0)
            case_count += (-1 if token == end_token else 0)

            if token == between_tokens:
                between_count += 1

            if token == and_token and between_count >= 1:
                between_count -= between_count
                continue

            if token in [and_token, or_token] and case_count == 0 and between_count == 0:
                result.append(tokens[start:idx])
                start = idx

        if start < len(tokens) - 1:
            result.append(tokens[start:len(tokens)])

        return result


class KeywordJoinSplitter(KeywordSplitter):
    @classmethod
    def split_join(cls, tokens: List[Token]) -> Tuple[List[Token], List[List[Token]], List[Token]]:
        """Splits WHEN sequence

        Args:
            tokens:

        Returns:

        """
        join_token = Token(word='JOIN', kind=Token.KEYWORD)
        join_tokens = [
            Token(word='INNER', kind=Token.KEYWORD),
            Token(word='LEFT', kind=Token.KEYWORD),
            Token(word='RIGHT', kind=Token.KEYWORD),
            Token(word='FULL', kind=Token.KEYWORD),
            Token(word='CROSS', kind=Token.KEYWORD),
            Token(word='OUTER', kind=Token.KEYWORD),
            Token(word='JOIN', kind=Token.KEYWORD)
        ]
        condition_tokens = [
            Token(word='ON', kind=Token.KEYWORD),
            Token(word='USING', kind=Token.FUNCTION)
        ]

        try:
            join_index = tokens.index(join_token)
        except ValueError:
            raise ValueError(f'{tokens[0]} needs "JOIN" context')

        condition_index = -1
        next_join_index = len(tokens)
        bracket_count = 0
        for idx, token in enumerate(tokens[join_index+1:]):
            bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
            bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)

            if token in condition_tokens and bracket_count == 0:
                condition_index = idx+(join_index+1)

            if token in join_tokens and bracket_count == 0:
                next_join_index = idx+(join_index+1)
                break

        if condition_index != -1:
            return (
                tokens[0:condition_index],
                cls._split_condiction(tokens[condition_index:next_join_index]),
                tokens[next_join_index:])

        return tokens[0:next_join_index], [], tokens[next_join_index:]

    @classmethod
    def _split_condiction(cls, tokens: List[Token]) -> List[List[Token]]:
        """Splits ON or USING sequence

        Args:
            tokens:

        Returns:

        """

        # if tokens[0].word.upper() == 'USING', no need spliting maybe
        # TODO: confirms whether overlooking other cases.
        if tokens[0].word.upper() != 'ON':
            return [tokens]

        return KeywordWhereSplitter.split_condiction(tokens)
