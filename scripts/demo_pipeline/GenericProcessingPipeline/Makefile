# GenericProcessingPipeline Makefile
# TPArchambault 2024.01.25
#

OBJDIR = obj
SRCDIR = cpp
BINDIR = bin

PROGS = ${BINDIR}/client ${BINDIR}/server ${BINDIR}/input_xlator ${BINDIR}/output_xlator ${BINDIR}/p_unit
CFLAGS = -g -I${PWD}/include
LDFLAGS = -llog4cxx -lstdc++fs

all: ${PROGS}

${OBJDIR}/%.o : ${SRCDIR}/%.cpp mk_bld_dirs
	g++ ${CPPFLAGS} ${CFLAGS} -c -o $@ $<

${BINDIR}/client: ${OBJDIR}/client.o mk_bld_dirs
	g++ ${CFLAGS} $< ${LDFLAGS} -o $@

${BINDIR}/server: ${OBJDIR}/server.o mk_bld_dirs
	g++ ${CFLAGS} $< ${LDFLAGS} -o $@

${BINDIR}/input_xlator: ${OBJDIR}/input_xlator.o ${OBJDIR}/fs_utils.o mk_bld_dirs
	g++ ${CFLAGS} $< ${OBJDIR}/fs_utils.o ${LDFLAGS} -luuid -o $@

${BINDIR}/p_unit: ${OBJDIR}/p_unit.o  ${OBJDIR}/fs_utils.o mk_bld_dirs
	g++ ${CFLAGS} $< ${OBJDIR}/fs_utils.o ${LDFLAGS} -luuid -o $@

${BINDIR}/output_xlator: ${OBJDIR}/output_xlator.o  ${OBJDIR}/fs_utils.o mk_bld_dirs
	g++ ${CFLAGS} $< ${OBJDIR}/fs_utils.o ${LDFLAGS} -luuid -o $@

.PHONY: mk_bld_dirs
mk_bld_dirs:
	mkdir -p ${OBJDIR}
	mkdir -p ${BINDIR}

mk_run_dirs:
	mkdir -p /tmp/pipeline/it_p0
	mkdir -p /tmp/pipeline/p0_p1
	mkdir -p /tmp/pipeline/p1_ot
	mkdir -p /tmp/pipeline/p0_working
	mkdir -p /tmp/pipeline/p1_working

clean:
	rm -f ${PROGS}

cleanall: clean
	rm -fr ${OBJDIR}
	rm -fr ${BINDIR}
