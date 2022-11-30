.PHONY: clean idenfity prepfs dnf vendor vendor-app vendor-py vendor-rs dep srpm
.SILENT: clean

OS_ID_FN = $(shell grep /etc/os-release -e "^ID=" | tr -d '"' | cut -d= -f2 | cut -d: -f1)
OS_ID   ?= $(OS_ID_FN)

idenfity:
	@echo "Platform $(OS_ID)"

prepfs:
	mkdir -p /tmp/rpmbuild/SOURCES
	mkdir -p \$(outdir)

clean:
	rm -f fapolicy-analyzer.tar.gz
	rm -f vendor-rs.tar.gz
	rm -f vendor-py.tar.gz

ifeq ($(OS_ID),rhel)
dnf: dnf-common dnf-rpmdev
else
dnf: dnf-common
endif

dnf-common:
	dnf install -y git openssl-devel dbus-devel python3-devel python3-pip python3-toml python3-beautifulsoup4 python3-requests python3-babel python3-markdown2 itstool
	dnf install -y rust-packaging || true
	dnf install -y rust-toolset || true
	cargo install cargo-vendor-filterer

dnf-rpmdev:
	# only dependent for spectool in python-py
	dnf install -y rpmdevtools

ifeq ($(OS_ID),rhel)
vendor: vendor-app vendor-doc vendor-rs vendor-py
else
vendor: vendor-app vendor-doc vendor-rs
endif

vendor-app:
	git archive HEAD -o fapolicy-analyzer.tar.gz --prefix=fapolicy-analyzer/
	cp fapolicy-analyzer.tar.gz /tmp/rpmbuild/SOURCES/

vendor-py:
	spectool -gf -C /tmp/rpmbuild/SOURCES \$(spec)

vendor-rs:
	cargo check
	./scripts/srpm/vendor-rs.sh
	cp vendor-rs.tar.gz /tmp/rpmbuild/SOURCES

vendor-doc:
	python3 help_utils.py update
	tar --exclude=es -cvzf vendor-docs.tar.gz help
	cp vendor-docs.tar.gz /tmp/rpmbuild/SOURCES

srpm: idenfity prepfs dnf vendor
	rpmbuild -bs -D "_topdir /tmp/rpmbuild" \$(spec)
	cp -v /tmp/rpmbuild/SRPMS/* \$(outdir)/
