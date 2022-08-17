File Access Policy Analyzer
===

Tools to assist with the configuration and maintenance of [fapolicyd](https://github.com/linux-application-whitelisting/fapolicyd).

## GUI

Run the fapolicy-analyzer UI:

```{shell}
make run
```

## Requirements

- Python 3.6
- Rust 1.58.1
- fapolicyd 1.x

### fapolicyd configuration

To generate rules that can be analyzed we require the following `syslog_format` configuration in fapolicyd.conf
```
syslog_format = rule,dec,perm,uid,gid,pid,exe,:,path,ftype,trust
```

## Getting Help

- Start a [Discussion](https://github.com/ctc-oss/fapolicy-analyzer/discussions) with the team
- See the [Wiki](https://github.com/ctc-oss/fapolicy-analyzer/wiki) for more resources

## License

GPL v3
