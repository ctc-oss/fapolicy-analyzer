File Access Policy Analyzer
===

Tools to assist with the configuration and maintenance of [fapolicyd](https://github.com/linux-application-whitelisting/fapolicyd).

## File Access Policy Analyzer User Interface

Run the fapolicy-analyzer UI:

```{shell}
python3 -m fapolicy-analyzer.ui
```

## Requirements

- Python 3.9
- Rust 1.52
- fapolicyd 1.0

### fapolicyd configuration
To generate rules that can be analyzed we require the following `syslog_format` configuration

`syslog_format = rule,dec,perm,uid,gid,pid,exe,:,path,ftype,trust`

## Getting Help
Feel free to ask a question or start a discussion in the [Discussion](https://github.com/ctc-oss/fapolicy-analyzer/discussions)

## Developers

See the [Wiki](https://github.com/ctc-oss/fapolicy-analyzer/wiki) for more resources.
