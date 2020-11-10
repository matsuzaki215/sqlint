// BigQuery Operators
// https://cloud.google.com/bigquery/docs/reference/standard-sql/functions-and-operators?hl=ja#operators
const BINARY_OPERATORS_ESCAPED = [
    "=", "<", ">", "!",
    "\\+", "\\-", "\\*", "\\/",
    "&", "\\|",
    // "~", "^",
];

/**
 * regex patterns
 */
const reservedKeywords = RESERVED_KEYWORDS.concat(RESERVED_FUNCTIONS).join("|");
const reservedOperators = BINARY_OPERATORS_ESCAPED.join("");

const REGEX_COMMA = /^(\s*)(,)(\s*)/;
const REGEX_BRACKET_LEFT = /^(\s*)(\()(\s*)/;
const REGEX_BRACKET_RIGHT = /^(\s*)(\))(\s*)/;
// Ignore whether keywords are Upper or Lower
const REGEX_KEYWORD = new RegExp(`^(\\s*)(${reservedKeywords})(\\(|\\s+|$)`, "i");
const REGEX_OPERATOR = new RegExp(`^(\\s*)([${reservedOperators}]+)(\\s*)`);
const REGEX_COMMENT_SINGLE = /^(\s*)(#.*|--.*)/;
const REGEX_COMMENT_BEGIN = /^(\s*)(\/\*)/;
const REGEX_COMMENT_END = /^(.*?)(\*\/)/;
const REGEX_QUOTES = /^(\s*)(".+"|'.+'|`.+`)(\s*)/;
const REGEX_IDENTIFIER = /^(\s*)([^,(){}#\s]+)(\s*)/;
const REGEX_WHITESPACE = /^(\s*)/;


// regex expression for parsing by span-tag-wrapped or non-wrapped
const regexSpaces = /^(\s+)/;
const regexNewline = /^\s*(&nbsp;)\s*/;
const regexInequality = /^\s*(&lt;|&gt;)\s*/;
const regexSpan = /^\s*(<span .+?>(.+?)<\/span>)\s*/;
const regexSpanWithClass = /^\s*(<span class="(.+?)">(.+?)<\/span>)\s*/;
const regexOthers = /\s*(\S+?)(\s*|<|$)/;
