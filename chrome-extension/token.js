
/**
 *
 */
class Token {
    static COMMA = 'Comma';
    static BRACKET = 'Bracket';
    static KEYWORD = 'Keyword';
    static OPERATOR = 'Operator';
    static COMMENT = 'Comment';
    static IDENTIFIER = 'Identifier';
    static WHITESPACE = 'Whitespace';
    static UNKNOWN = 'Unknown';

    constructor(word, kind = Token.UNKNOWN) {
        this.word = word;
        this.kind = kind;
    }

    get word() {
        return this._word;
    }

    set word(value) {
        this._word = value;
    }

    get kind() {
        return this._kind;
    }

    set kind(value) {
        if (value.length === 0) {
            value = 'unknown';
        }

        this._kind = value;
    }

    toString() {
        return `<"${this.kind}", "${this.word}">`;
    }
}


/**
 *
 */
class BigQueryToken {
    constructor(word, kind) {
        this.word = word;
        this.kind = kind;
    }

    get word() {
        return this._word;
    }

    set word(value) {
        this._word = value;
    }

    get kind() {
        return this._kind;
    }

    set kind(value) {
        if (value.length === 0) {
            value = 'unknown';
        }

        this._kind = value;
    }

    toString() {
        return `<"${this.kind}", "${this.word}">`;
    }
}
