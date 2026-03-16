# Generic Processing Pipeline Demo #

## Introduction ##

The Generic Processing Pipeline is a simple multi-process example that does
little more then transfer a file through a number of translaters and processing
units. For the sake of design and testing simplicity, the input file's contents
is unchanged in the processing chain.

The processing chain used with the single file transfer, `./PipelineCtl -s`:

1. File -> `client` -> TCP/IP stream
1. TCP/IP stream -> `input_xlator` -> `/tmp/pipeline/it_p0/input_xlator.out`
1. `/tmp/pipeline/it_p0/input_xlator.out` -> `p_unit` -> `/tmp/pipeline/p1_p0/p_unit_0_.out`
1. `/tmp/pipeline/it_p0/input_xlator.out` -> `p_unit` -> `/tmp/pipeline/p1_p0/p_unit_1_.out`
1. `/tmp/pipeline/p1_p0/p_unit_1_.out` -> `output_xlator` -> `/tmp/pipeline/p1_ot/output_xlator.out`
1. TCP/IP stream -> `server` -> `/tmp/pipeline/server.out`

## Building the Pipeline ##

The Generic Processing Pipeline is coded in C++ and needs `g++` to be installed
in order to build. Although it is in `C++,` there is no locally developed code
that is Object Oriented, i.e. no classes or hierarchies, etc. just a bit of
Vectors, ifstreams, and ofstreams. Basically glorified C with stronger type
checking.

To create the build `obj/` and `bin/` directories, generate the object files
and build the target executables, invoke:

> $ make

## Creating the Runtime `tmp/` File Structure
To create the local `tmp/` file tree, invoke:

> $ make mk_run_dirs

## Executing the Pipeline ##
After the Pipeline binaries and the runtime directories have been created, the
Pipeline can be executed using the wrapper `PipelineCtl.py.` The `-t` option
will execute a small set of sanity tests. The `-s` option will execute a single
file transfer from `client` through `server.` Use the `-h` help option to see
the available set of options.

```
$ ./PipelineCtl -t
All 5 tests passed
$ ./PipelineCtl -s
Single xfer execution: Input file successfully transferred
$
```

Note: There are times when listening socket binds fail due to socket already in
use errors. I have added the `reuse` option to the socket's options and believe
this will address things but have not done extensive testing due to project
staffing allocation constraints.



