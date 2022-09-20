.PHONY: clean idenfity dnf vendor vendor-app vendor-py vendor-rs dep srpm
.SILENT: clean

OS_ID_FN = $(shell grep /etc/os-release -e "^ID=" | tr -d '"' | cut -d= -f2 | cut -d: -f1)
OS_ID   ?= $(OS_ID_FN)

idenfity:
	@echo "Platform $(OS_ID)"

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
	dnf install -y git openssl-devel dbus-devel python3-devel python3-pip python3-toml python3-beautifulsoup4 python3-requests python3-babel
	dnf install -y rust-packaging || true
	dnf install -y rust-toolset || true
	cargo install cargo-vendor-filterer

dnf-rpmdev:
	# only dependent for spectool in python-py
	dnf install -y rpmdevtools

ifeq ($(OS_ID),rhel)
vendor: vendor-app vendor-rs vendor-py
else
vendor: vendor-app vendor-rs
endif

vendor-app:
	git archive HEAD -o fapolicy-analyzer.tar.gz --prefix=fapolicy-analyzer/

vendor-py:
	spectool -gf \$(spec)

vendor-rs:
	cargo check
	./scripts/srpm/vendor-rs.sh

srpm: idenfity dnf vendor
	@echo "=========================== SRPM ==========================="
	pwd
	mkdir -p /tmp/rpmbuild/SOURCES
	ls -al
	cp *.tar.gz /tmp/rpmbuild/SOURCES
	cat /etc/os-release
	rpmbuild -bs -D "_topdir /tmp/rpmbuild" \$(spec)
	mkdir -p \$(outdir)
	cp -v /tmp/rpmbuild/SRPMS/* \$(outdir)/
