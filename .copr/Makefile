.PHONY: clean idenfity prepfs dnf vendor vendor-app vendor-py vendor-rs dep srpm
.SILENT: clean

OS_PRETTY_NAME = $(shell grep /etc/os-release -e "^PRETTY_NAME=" | tr -d '"' | cut -d= -f2 | cut -d: -f1)
OS_ID_FN =       $(shell grep /etc/os-release -e "^ID=" | tr -d '"' | cut -d= -f2 | cut -d: -f1)
OS_ID   ?=       $(OS_ID_FN)

idenfity:
	@echo "Platform: $(OS_PRETTY_NAME) (id: $(OS_ID))"

prepfs:
	mkdir -p /tmp/rpmbuild/SOURCES
	mkdir -p \$(outdir)

clean:
	rm -f fapolicy-analyzer.tar.gz
	rm -f vendor-rs.tar.gz
	rm -f vendor-py.tar.gz

ifeq ($(OS_ID),rhel)
dnf: dnf-common dnf-el
else
dnf: dnf-common dnf-fc
endif

dnf-common:
	dnf install -y git which openssl-devel dbus-devel python3-devel python3-pip python3-toml python3-beautifulsoup4 python3-requests python3-babel

dnf-fc:
	dnf install -y rust-packaging

dnf-el:
	dnf install -y rpmdevtools
	dnf install -y rust-toolset
	cargo install cargo-vendor-filterer

ifeq ($(OS_ID),rhel)
vendor: vendor-app vendor-rs vendor-py
else
vendor: vendor-app
endif

vendor-app:
	git archive HEAD -o fapolicy-analyzer.tar.gz --prefix=fapolicy-analyzer/

vendor-py:
	which spectool && spectool -gf -C /tmp/rpmbuild/SOURCES/ \$(spec) || true

vendor-rs:
	cargo check
	./scripts/srpm/vendor-rs.sh
	cp vendor-rs.tar.gz /tmp/rpmbuild/SOURCES/

move-sources: prepfs
	cp fapolicy-analyzer.tar.gz /tmp/rpmbuild/SOURCES/

build:
	rpmbuild -bs -D "_topdir /tmp/rpmbuild" \$(spec)

export:
	mkdir -p \$(outdir)/
	cp -v /tmp/rpmbuild/SRPMS/* \$(outdir)/

# the copr entrypoint
srpm: idenfity dnf vendor move-sources build export
