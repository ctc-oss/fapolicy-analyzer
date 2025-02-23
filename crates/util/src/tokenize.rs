pub fn tokenize(input: &str) -> Vec<String> {
    let mut tokens = Vec::new();
    let mut current = String::new();
    let mut chars = input.chars().peekable();

    while let Some(&c) = chars.peek() {
        if c.is_whitespace() {
            chars.next();
            continue;
        }
        if c == '"' || c == '\'' {
            let quote_char = c;
            chars.next();
            while let Some(ch) = chars.next() {
                match ch {
                    '\\' => {
                        if let Some(escaped) = chars.next() {
                            current.push(escaped);
                        }
                    }
                    c if c == quote_char => {
                        break;
                    }
                    _ => current.push(ch),
                }
            }
            tokens.push(current.clone());
            current.clear();
        } else {
            while let Some(&ch) = chars.peek() {
                if ch.is_whitespace() || ch == '"' || ch == '\'' {
                    break;
                } else {
                    current.push(ch);
                    chars.next();
                }
            }
            tokens.push(current.clone());
            current.clear();
        }
    }
    tokens
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_tokenize() {
        assert_eq!(&tokenize("bar"), &["bar"]);
        assert_eq!(&tokenize("foo bar"), &["foo", "bar"]);
        assert_eq!(&tokenize(" foo bar"), &["foo", "bar"]);
        assert_eq!(&tokenize("foo bar "), &["foo", "bar"]);
        assert_eq!(&tokenize("foo     bar"), &["foo", "bar"]);
        assert_eq!(&tokenize("  foo bar  "), &["foo", "bar"]);
        assert_eq!(&tokenize("'foo bar'"), &["foo bar"]);
        assert_eq!(&tokenize("'foo ba'r"), &["foo ba", "r"]);
        assert_eq!(&tokenize("\"foo bar\""), &["foo bar"]);
        assert_eq!(&tokenize("'foo bar' 'biz baz'"), &["foo bar", "biz baz"]);
        assert_eq!(&tokenize("'foo bar' 'biz baz"), &["foo bar", "biz baz"]);
    }
}
