fapolicy-analyzer documentation
===

## website

### building

Requires hugo extended.

From within the site directory execute

1. `hugo mod init github.com/ctc-oss/fapolicy-analyzer`
2. `hugo mod get -u ./...`
3. `hugo`

To test while developing run

`hugo server --minify --buildDrafts`
