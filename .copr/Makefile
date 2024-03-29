.PHONY: clean identify prepfs dnf vendor vendor-app vendor-py vendor-rs dep srpm
.SILENT: clean

OS_PRETTY_NAME = $(shell grep /etc/os-release -e "^PRETTY_NAME=" | tr -d '"' | cut -d= -f2 | cut -d: -f1)
OS_ID_FN =       $(shell grep /etc/os-release -e "^ID=" | tr -d '"' | cut -d= -f2 | cut -d: -f1)
OS_ID   ?=       $(OS_ID_FN)
VERSION ?=       $(shell grep "Version:" $(spec) | tr -s ' ' | cut -d' ' -f2)

identify:
	@echo "Platform: $(OS_PRETTY_NAME) (id: $(OS_ID))"

prepfs: prep_outdir prep_rpmbuild_dir

prep_outdir:
	mkdir -p \$(outdir)

prep_rpmbuild_dir:
	mkdir -p /tmp/rpmbuild/SOURCES/

clean:
	rm -f fapolicy-analyzer-${VERSION}.tar.gz
	rm -f vendor-rs-${VERSION}.tar.gz

dnf: dnf-common

dnf-common:
	dnf install -y git which openssl-devel dbus-devel audit-libs-devel clang python3-devel python3-pip python3-toml python3-beautifulsoup4 python3-requests python3-babel itstool
	dnf install -y python3-markdown2 || python3 -m pip install markdown2
	dnf install -y rust-packaging

ifeq ($(OS_ID),rhel)
# we only need to vendor rust and python on rhel
vendor: prep_rpmbuild_dir vendor-app vendor-doc vendor-py
else
vendor: prep_rpmbuild_dir vendor-app vendor-doc
endif

vendor-app:
	git archive HEAD -o "fapolicy-analyzer-${VERSION}.tar.gz" --prefix=fapolicy-analyzer/

vendor-py:
	which spectool && spectool -g -C /tmp/rpmbuild/SOURCES/ \$(spec) || true

vendor-rs:
	./scripts/srpm/vendor-rs.sh ${VERSION}
	cp vendor-rs-${VERSION}.tar.gz /tmp/rpmbuild/SOURCES/vendor-rs-${VERSION}.tar.gz

move-sources: prepfs
	cp fapolicy-analyzer-${VERSION}.tar.gz /tmp/rpmbuild/SOURCES/

vendor-doc:
	python3 help update
	tar --exclude=es --exclude=*.py --exclude=.gitignore -cvzf vendor-docs-${VERSION}.tar.gz help
	cp vendor-docs-${VERSION}.tar.gz /tmp/rpmbuild/SOURCES/

build:
	rpmbuild -bs -D "_topdir /tmp/rpmbuild" \$(spec)

export:
	mkdir -p \$(outdir)/
	cp -v /tmp/rpmbuild/SRPMS/* \$(outdir)/

# the copr entrypoint
srpm: identify dnf vendor move-sources build export
