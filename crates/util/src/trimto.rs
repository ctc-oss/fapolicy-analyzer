/*
 * Copyright Concurrent Technologies Corporation 2024
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

/// Like the Scala stripMargin function
pub trait TrimTo {
    fn trim_to(&self, marker: char) -> String;
}

impl<T: AsRef<str>> TrimTo for T {
    fn trim_to(&self, marker: char) -> String {
        let mut lines = vec![];
        for line in self.as_ref().split("\n") {
            if let Some((_, s)) = line.split_once(marker) {
                lines.push(s)
            } else {
                lines.push(line)
            }
        }
        lines.join("\n")
    }
}

#[cfg(test)]
mod tests {
    use crate::trimto::TrimTo;

    #[test]
    fn simple() {
        assert_eq!("  |x".trim_to('|'), "x");
        assert_eq!("|x".trim_to('|'), "x");
        assert_eq!("x".trim_to('|'), "x");
        assert_eq!("-|x".trim_to('|'), "x");
        assert_eq!("fe fi fo|x".trim_to('|'), "x");
    }

    #[test]
    fn multiline() {
        assert_eq!("1|a\n2|b\n3|c".trim_to('|').replace("\n", ""), "abc");
        assert_eq!("|a\n|b\n|c".trim_to('|').replace("\n", ""), "abc");
    }
}
