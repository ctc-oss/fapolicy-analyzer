rpm query
===

Use `rpm` to query

dump format `path size mtime digest mode owner group isconfig isdoc rdev symlink`
eg.
[root@ef9ac5f7b3bb /]# rpm -q --dump valgrind-3.16.0-2.el8.x86_64
/usr/bin/valgrind 24120 1595348804 0c548a7821c5d2b9d18e3979ce18c03873c26921bacdf0082891f12b7896da4f 0100755 root root 0 0 0 X


`docker run --rm -it -v $PWD/target/debug:/usr/local/bin centos:8 bash`
