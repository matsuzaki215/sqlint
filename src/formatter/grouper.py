from abc import ABCMeta, abstractmethod
from typing import List, TypeVar, Tuple

from src.parser import Token
from src.syntax_tree import SyntaxTree

T = TypeVar('T')


class Grouper(metaclass=ABCMeta):
    @abstractmethod
    def group(self, tokens: List[T], tree: SyntaxTree) -> Tuple[List[T], List[T], List[T]]:
        raise NotImplementedError()

    @classmethod
    def group_other(cls, tokens: List[Token]) -> Tuple[List[Token], List[Token], List[Token]]:
        bracket_count = 0
        for idx, token in enumerate(tokens[1:]):
            bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
            bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)

            if bracket_count == 0 and token.kind in [Token.COMMA, Token.COMMENT]:
                return tokens[0:idx + 1], [], tokens[idx + 1:]

        return tokens[0:], [], []


class IdentifierGrouper(Grouper):
    @classmethod
    def group(cls, tokens: List[Token], tree: SyntaxTree) -> Tuple[List[Token], List[Token], List[Token]]:
        parent_tree = tree.parent

        if parent_tree is None or parent_tree.depth == 0:
            # The identifier placed on root depth is illegal case.
            return tokens[0:1], [], tokens[1:]

        # if parent tree is "FROM" sequence, explores "JOIN" sequences.
        from_token = Token(word='FROM', kind=Token.KEYWORD)
        if parent_tree.tokens[0] == from_token:
            return cls.group_from(tokens)

        return cls.group_other(tokens)

    @classmethod
    def group_from(cls, tokens: List[Token]) -> Tuple[List[Token], List[Token], List[Token]]:
        join_tokens = [
            Token(word='INNER', kind=Token.KEYWORD),
            Token(word='LEFT', kind=Token.KEYWORD),
            Token(word='RIGHT', kind=Token.KEYWORD),
            Token(word='CROSS', kind=Token.KEYWORD),
            Token(word='OUTER', kind=Token.KEYWORD),
            Token(word='JOIN', kind=Token.KEYWORD)
        ]

        bracket_count = 0
        for idx, token in enumerate(tokens[0:]):
            bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
            bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)

            if token in join_tokens and bracket_count == 0:
                return tokens[0:idx], tokens[idx:], []

        return cls.group_other(tokens)


class RightBrackerGrouper(Grouper):
    @classmethod
    def group(cls, tokens: List[Token], tree: SyntaxTree) -> Tuple[List[Token], List[Token], List[Token]]:
        if len(tokens) >= 2 and tokens[1].word == ';':
            return tokens[0:2], [], tokens[2:]

        return tokens[0:1], [], tokens[1:]


class CommaGrouper(Grouper):
    @classmethod
    def group(cls, tokens: List[Token], tree: SyntaxTree) -> Tuple[List[Token], List[Token], List[Token]]:
        parent_tree = tree.parent
        bracket_count = 0

        # TODO: implement following as Grouper and merges WITH-Grouper
        if parent_tree.depth == 0:
            # maybe this comma correspands to WITH sequence
            # expected
            # , {Identifier} AS ( {myquery ) ...
            as_token = Token(word='AS', kind=Token.KEYWORD)

            if len(tokens) <= 2:
                return tokens[0:], [], []

            if tokens[0].kind != Token.COMMA:
                raise ValueError('a head of tokens must be "," sequence.')

            if tokens[1].kind != Token.IDENTIFIER:
                # TODO: raises SQL error or check this as Violations
                raise ValueError('next of "WITH" or "," must be identifier')

            if tokens[2] != as_token:
                return tokens[0:2], [], tokens[2:]

            if tokens[3].kind != Token.BRACKET_LEFT:
                # TODO: raises SQL error or check this as Violations
                raise ValueError('next of "AS" must be "(" in "WITH" or "," sequence.')

            # Explores tokens until branch is closed
            bracket_count = 1
            for idx, token in enumerate(tokens[4:]):
                bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
                bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)

                if bracket_count == 0:
                    return tokens[0:4], tokens[4:idx + 4], tokens[idx + 4:]

            return tokens[0:1], [], tokens[1:]

        for idx, token in enumerate(tokens[1:]):
            bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
            bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)

            if bracket_count == 0 and token.kind == Token.COMMA:
                return tokens[0:idx + 1], [], tokens[idx + 1:]

        return tokens[0:], [], []


class KeywordGrouper(Grouper):
    @classmethod
    def group(cls, tokens: List[Token], tree: SyntaxTree) -> Tuple[List[Token], List[Token], List[Token]]:
        head = tokens[0]

        if head.kind != Token.KEYWORD:
            raise ValueError(f'token kind must be KEYWORD, but {head.kind}')

        key_functions = [
            (['CREATE'], cls._group_create),
            (['RETURNS'], cls._group_returns),
            (['LANGUAGE'], cls._group_language),
            (['AS'], cls._group_as),
            (['WITH'], cls._group_with),
            (['SELECT'], cls._group_select),
            (['FROM'], cls._group_from),
            (['WHERE'], cls._group_where),
            (['ORDER'], cls._group_order),
            (['GROUP'], cls._group_group),
            (['HAVING'], cls._group_having),
            (['CASE'], cls._group_case),
            (['WHEN'], cls._group_where),
            (['INNER', 'LEFT', 'RIGHT', 'CROSS', 'OUTER', 'JOIN'], cls._group_join),
            (['ON', 'USING'], cls._group_joinkey),
        ]

        word = head.word.upper()
        # Switches by specified keywords

        for keys, func in key_functions:
            if word in keys:
                return func(tokens)

        return tokens[0:], [], []

    @classmethod
    def _group_create(cls, tokens: List[Token]) -> Tuple[List[Token], List[Token], List[Token]]:
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
    def _group_returns(cls, tokens: List[Token]) -> Tuple[List[Token], List[Token], List[Token]]:
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
    def _group_language(cls, tokens: List[Token]) -> Tuple[List[Token], List[Token], List[Token]]:
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
    def _group_as(cls, tokens: List[Token]) -> Tuple[List[Token], List[Token], List[Token]]:
        if len(tokens) <= 2:
            return tokens[0:], [], []

        if tokens[1].kind != Token.BRACKET_LEFT:
            return tokens[0:2], [], tokens[2:]

        # Explores tokens until branch is closed
        bracket_count = 1
        for idx, token in enumerate(tokens[2:]):
            bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
            bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)

            if bracket_count == 0:
                return tokens[0:2], tokens[2:idx+2], tokens[idx+2:]

        return tokens[0:2], [], tokens[2:]

    @classmethod
    def _group_with(cls, tokens: List[Token]) -> Tuple[List[Token], List[Token], List[Token]]:
        """Groups WITH sequence

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
            return tokens[0:], [], []

        if tokens[1].kind != Token.IDENTIFIER:
            # TODO: raises SQL error or check this as Violations
            raise ValueError('next of "WITH" must be identifier')

        if tokens[2] != as_token:
            return tokens[0:2], [], tokens[2:]

        if tokens[3].kind != Token.BRACKET_LEFT:
            # TODO: raises SQL error or check this as Violations
            raise ValueError('next of "AS" must be "(" in "WITH" sequence.')

        # Explores tokens until branch is closed
        bracket_count = 1
        for idx, token in enumerate(tokens[4:]):
            bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
            bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)

            if bracket_count == 0:
                return tokens[0:4], tokens[4:idx+5], tokens[idx+5:]

        return tokens[0:1], tokens[1:], []

    @classmethod
    def _group_select(cls, tokens: List[Token]) -> Tuple[List[Token], List[Token], List[Token]]:
        """Groups Select sequence

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
                return tokens[0:1], tokens[1:idx+1], tokens[idx+1:]

        return tokens[0:1], tokens[1:], []

    @classmethod
    def _group_from(cls, tokens: List[Token]) -> Tuple[List[Token], List[Token], List[Token]]:
        """Groups FROM sequence

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
                return tokens[0:1], tokens[1:idx+1], tokens[idx+1:]

        return tokens[0:1], tokens[1:], []

    @classmethod
    def _group_where(cls, tokens: List[Token]) -> Tuple[List[Token], List[Token], List[Token]]:
        """Groups WHERE sequence

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
                return tokens[0:1], tokens[1:idx+1], tokens[idx+1:]

        return tokens[0:1], tokens[1:], []

    @classmethod
    def _group_group(cls, tokens: List[Token]) -> Tuple[List[Token], List[Token], List[Token]]:
        """Groups GROIP BY sequence

        Args:
            tokens:

        Returns:

        """
        return tokens[0:2], tokens[2:], []

    @classmethod
    def _group_order(cls, tokens: List[Token]) -> Tuple[List[Token], List[Token], List[Token]]:
        """Groups ORDER BY sequence

        Args:
            tokens:

        Returns:

        """
        return tokens[0:2], tokens[2:], []

    @classmethod
    def _group_having(cls, tokens: List[Token]) -> Tuple[List[Token], List[Token], List[Token]]:
        """Groups ORDER BY sequence

        Args:
            tokens:

        Returns:

        """
        return tokens[0:1], tokens[1:], []

    @classmethod
    def _group_joinkey(cls, tokens: List[Token]) -> Tuple[List[Token], List[Token], List[Token]]:
        """Groups ON or USING sequence

        Args:
            tokens:

        Returns:

        """

        on_token = Token(word='ON', kind=Token.KEYWORD)
        using_token = Token(word='USING', kind=Token.KEYWORD)

        and_or_tokens = [
            Token(word='AND', kind=Token.KEYWORD),
            Token(word='OR', kind=Token.KEYWORD)
        ]

        if tokens[0] == on_token:
            bracket_count = 0
            for idx, token in enumerate(tokens[1:]):
                bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
                bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)

                if token in and_or_tokens and bracket_count == 0:
                    return tokens[0:idx+1], [], tokens[idx+1:]
        elif tokens[0] == using_token:
            # TODO: confirms whether overlooking other cases.
            return tokens[0:], [], []

        return tokens[0:], [], []

    @classmethod
    def _group_case(cls, tokens: List[Token]) -> Tuple[List[Token], List[Token], List[Token]]:
        """Groups WHEN sequence

        Args:
            tokens:

        Returns:

        """

        case_token = Token(word='CASE', kind=Token.KEYWORD)
        when_token = Token(word='WHEN', kind=Token.KEYWORD)
        end_token = Token(word='END', kind=Token.KEYWORD)

        if tokens[1].kind != Token.IDENTIFIER:
            # TODO: raises SQL error or check this as Violations
            raise ValueError('next of "CASE" must be identifier')

        if tokens[2] != when_token:
            # TODO: raises SQL error or check this as Violations
            raise ValueError('"CASE" sequence requires one or more "WHEN" sequense')

        bracket_count = 0
        case_count = 1
        for idx, token in enumerate(tokens[2:]):
            bracket_count += (1 if token.kind == Token.BRACKET_LEFT else 0)
            bracket_count += (-1 if token.kind == Token.BRACKET_RIGHT else 0)

            if token == case_token and bracket_count == 0:
                case_count += 1
            if token == end_token and case_count == 1 and bracket_count == 0:
                return tokens[0:2], tokens[2:idx+2], tokens[idx+2:]

        return tokens[0:2], tokens[2:], []

    @classmethod
    def _group_when(cls, tokens: List[Token]) -> Tuple[List[Token], List[Token], List[Token]]:
        """Groups WHEN sequence

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

        return tokens[0:], [], []

    @classmethod
    def _group_join(cls, tokens: List[Token]) -> Tuple[List[Token], List[Token], List[Token]]:
        """Groups WHEN sequence

        Args:
            tokens:

        Returns:

        """

        join_token = Token(word='JOIN', kind=Token.KEYWORD)
        join_tokens = [
            Token(word='INNER', kind=Token.KEYWORD),
            Token(word='LEFT', kind=Token.KEYWORD),
            Token(word='RIGHT', kind=Token.KEYWORD),
            Token(word='CROSS', kind=Token.KEYWORD),
            Token(word='OUTER', kind=Token.KEYWORD),
            Token(word='JOIN', kind=Token.KEYWORD)
        ]

        condition_tokens = [
            Token(word='ON', kind=Token.KEYWORD),
            Token(word='USING', kind=Token.KEYWORD)
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
            return tokens[0:condition_index], tokens[condition_index:next_join_index], tokens[next_join_index:]

        return tokens[0:next_join_index], [], tokens[next_join_index:]
