import re


class LintChecker(object):
    def check(self, text):
        raise NotImplemented()

    @staticmethod
    def is_blank_line(text):
        """

        :param text:
        :return:
        """

        # check only spaces
        return re.match(re.compile('^\s+$'), text) is not None


class CapitalLintChecker(object):
    def __init__(self, message, keywords, is_capital=False):
        """
        Check whether keywords are capital or not
        :param message: message
        :param is_capital: whether keywords are capital or not
        :param keywords: str list
        """
        self.message = message
        self.keywords = keywords
        self.is_capital = is_capital

    def check(self, text):
        result = {}

        for word in self.keywords:
            if self.is_capital:
                word = word.upper()
            else:
                word = word.lower()

            # find keywords in text
            # print('^|\s{}\s|$'.format(word))
            regex = re.compile('(^|[^a-zA-Z])({})([^a-zA-Z]|$)'.format(word), re.IGNORECASE)
            iterator = re.finditer(regex, text)

            # check whether word is capital or not
            for match in iterator:
                group = match.group(2).rstrip('\r\n')
                if group != word:
                    result[match.span()] = {'group': group,
                                            'message': '{} ({} -> {})'.format(self.message, group, word)}

        return result


class RegexLintChecker(LintChecker):
    def __init__(self, message, pattern):
        """

        :param message:
        :param pattern:
        """
        self.message = message
        self.regex = re.compile(pattern)

    def check(self, text):
        result = {}
        iterator = re.finditer(self.regex, text)
        for match in iterator:
            result[match.span()] = {'group': match.group(),
                                    'message': self.message}

        return result
