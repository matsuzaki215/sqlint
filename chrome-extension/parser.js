
/**
 *
 * @returns {*}
 */
function getBigQueryTokens() {
    // gets HTMLCollection
    let elements = document.getElementsByClassName("CodeMirror-line");

    if (elements.length === 0)
        // raise error
        return [];

    let result = [];
    elements = Array.from( elements );

    elements.forEach( function(line) {
        // console.log("line: " + line.innerHTML);
        let children = line.getElementsByTagName("span");

        /**
         * split some query keywords wrapped HTML tags in query textarea
         * - all keywords are wrapped HTML tags.
         * - only `*` is not wrapped HTML tags.
         * - if some keywords has HTML tags inside, that tags are html encoded.
         *
         */
        console.log("children; " + 0 + " : " + children[0].innerHTML);


        let target = children[0].innerHTML;
        while (target.length > 0) {
            console.log("target = " + target);

            // get whitespaces
            let spaces = regexSpaces.exec(target);
            if (spaces) {
                target = target.substring(spaces[0].length);
                // result.push(new BigQueryKeywords(spaces[0], "whitespace"));
            }

            let match = execMatch(target);
            if (!match) {
                // when can not match, raise Error
                break;
            }

            console.log("match: `" + match + "`");

            if(match[2] != 'newline') {
              result.push(new BigQueryToken(match[3], match[2]));
            }

            target = target.substring(match[1].length);
        }

    });

    return result;
}

function execMatch(text) {
  let match = regexNewline.exec(text);
  if (match) {
    match[2] = 'newline';
    match[3] = match[1];
    return match
  }

  match = regexInequality.exec(text);
  if (match) {
    match[2] = 'inequality';
    switch( match[1] ) {
      case '&lt;': match[3] = '<'; break;
      case '&gt;': match[3] = '>'; break;
      default:
        match[3] = match[1];
    }
    return match
  }

  match = regexSpanWithClass.exec(text);
  if (match) {
    return match
  }

  match = regexSpan.exec(text);
  if (match) {
    return null
  }

  match = regexOthers.exec(text);
  if (match) {
    match[2] = 'unknown';
    match[3] = match[1];
    return match
  }

  return match
}

/**
 *
 * @param keywords : list of BigQueryToken
 * @returns {*}
 */
function parse(keywords) {
    let tokenList = [];
    let isInComment = false;
    let isInSelect = false;

    for(let val of keywords) {
        [tokens, isInComment, isInSelect] = _tokenize(val.word, isInComment, isInSelect);
        tokenList.push(tokens);
    }

    return tokenList
}

function _tokenize(text, isInComment, isInSelect) {
    let tokens = [];

    // check multi-line comment : /* comment */
    while (text.length > 0) {
        console.log(`[parse] : ${text}`);

        let result = [];

        // comment end (*/)
        if (isInComment) {
            result = REGEX_COMMENT_END.exec(text);
            if (result != null) {
                if (result[1].length > 0) {
                    tokens.push(new Token(result[1], Token.COMMENT));
                }
                tokens.push(new Token(result[2], Token.COMMENT));
                text = text.substring(result[0].length);
                isInComment = false;
                continue;
            } else {
                tokens.push(new Token(text, Token.COMMENT));
                break;
            }
        }

        // comment begin (/*)
        result = REGEX_COMMENT_BEGIN.exec(text);
        if (result != null) {
            if (result[1].length > 0) {
                tokens.push(new Token(result[1], Token.WHITESPACE));
            }
            tokens.push(new Token(result[2], Token.COMMENT));
            text = text.substring(result[0].length);
            isInComment = true;
            continue;
        }

        // comment single(#)
        result = REGEX_COMMENT_SINGLE.exec(text);
        if (result != null) {
            if (result[1].length > 0) {
                tokens.push(new Token(result[1], Token.WHITESPACE));
            }
            tokens.push(new Token(result[2], Token.COMMENT));
            text = text.substring(result[0].length);
            continue;
        }

        // comma
        result = REGEX_COMMA.exec(text);
        if (result != null) {
            if (result[1].length > 0) {
                tokens.push(new Token(result[1], Token.WHITESPACE));
            }
            tokens.push(new Token(result[2], Token.COMMA));
            if (result[3].length > 0) {
                tokens.push(new Token(result[3], Token.WHITESPACE));
            }
            text = text.substring(result[0].length);
            continue;
        }

        // bracket_left
        result = REGEX_BRACKET_LEFT.exec(text);
        if (result != null) {
            if (result[1].length > 0) {
                tokens.push(new Token(result[1], Token.WHITESPACE));
            }
            tokens.push(new Token(result[2], Token.BRACKET));
            if (result[3].length > 0) {
                tokens.push(new Token(result[3], Token.WHITESPACE));
            }
            text = text.substring(result[0].length);
            continue;
        }

        // bracket_right
        result = REGEX_BRACKET_RIGHT.exec(text);
        if (result != null) {
            if (result[1].length > 0) {
                tokens.push(new Token(result[1], Token.WHITESPACE));
            }
            tokens.push(new Token(result[2], Token.BRACKET));
            if (result[3].length > 0) {
                tokens.push(new Token(result[3], Token.WHITESPACE));
            }
            text = text.substring(result[0].length);
            continue;
        }

        // keywords
        result = REGEX_KEYWORD.exec(text);
        if (result != null) {
            if (result[1].length > 0) {
                tokens.push(new Token(result[1], Token.WHITESPACE));
            }

            if (result[2].toUpperCase() === "SELECT") {
                isInSelect = true;
            }
            if (result[2].toUpperCase() === "FROM") {
                isInSelect = false;
            }

            tokens.push(new Token(result[2], Token.KEYWORD));
            if (result[3] === "(") {
                tokens.push(new Token(result[3], Token.BRACKET));
            } else if (result[3].length > 0) {
                tokens.push(new Token(result[3], Token.WHITESPACE));
            }
            text = text.substring(result[0].length);
            continue;
        }

        // quotes (as identifier )
        result = REGEX_QUOTES.exec(text);
        if (result != null) {
            if (result[1].length > 0) {
                tokens.push(new Token(result[1], Token.WHITESPACE));
            }
            tokens.push(new Token(result[2], Token.IDENTIFIER));
            if (result[3].length > 0) {
                tokens.push(new Token(result[3], Token.WHITESPACE));
            }
            text = text.substring(result[0].length);
            continue;
        }

        // operator
        result = REGEX_OPERATOR.exec(text);
        if (result != null) {
            if (result[1].length > 0) {
                tokens.push(new Token(result[1], Token.WHITESPACE));
            }

            if (result[2] === "*" && isInSelect) {
                tokens.push(new Token(result[2], Token.KEYWORD));
            }
            else {
                tokens.push(new Token(result[2], Token.OPERATOR));
            }
            if (result[3].length > 0) {
                tokens.push(new Token(result[3], Token.WHITESPACE));
            }
            text = text.substring(result[0].length);
            continue;
        }

        // identifier
        result = REGEX_IDENTIFIER.exec(text);
        if (result != null) {
            if (result[1].length > 0) {
                tokens.push(new Token(result[1], Token.WHITESPACE));
            }
            tokens.push(new Token(result[2], Token.IDENTIFIER));
            if (result[3].length > 0) {
                tokens.push(new Token(result[3], Token.WHITESPACE));
            }
            text = text.substring(result[0].length);
            continue;
        }

        // blank
        result = REGEX_WHITESPACE.exec(text);
        if (result != null) {
            if (result[1].length > 0) {
                tokens.push(new Token(result[1], Token.WHITESPACE));
            }
            text = text.substring(result[0].length);
            continue;
        }

        // others
        // Not Implemented
        console.log("ERROR: not match any patterns");
    }

    return [tokens, isInComment, isInSelect];
}
