fapolicy-analyzer documentation
===

## website

### building

Requires hugo extended.

```shell
curl -LO https://github.com/gohugoio/hugo/releases/download/v0.123.1/hugo_extended_0.123.1_linux-amd64.deb
dpkg -i hugo_extended_0.123.1_linux-amd64.deb
```

From within the site directory execute

1. `hugo mod init github.com/ctc-oss/fapolicy-analyzer`
2. `hugo mod get -u ./...`
3. `hugo`

To test while developing run

`hugo server --minify --buildDrafts`
