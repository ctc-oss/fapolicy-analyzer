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

dnf:
	dnf install -y git openssl-devel dbus-devel python3-devel python3-pip python3-toml python3-beautifulsoup4 python3-requests python3-babel
	dnf install -y rust-packaging || true
	dnf install -y rust-toolset || true
	cargo install cargo-vendor-filterer

vendor: vendor-app vendor-py vendor-rs
	cargo check
	git archive HEAD -o fapolicy-analyzer.tar.gz --prefix=fapolicy-analyzer/
	./scripts/srpm/vendor.sh

vendor-app:
	git archive HEAD -o fapolicy-analyzer.tar.gz --prefix=fapolicy-analyzer/

vendor-py:
	./scripts/srpm/vendor-py.sh

vendor-rs:
	cargo check
	./scripts/srpm/vendor-rs.sh

ifeq ($(OS_ID),rhel)
dep: dnf vendor-app vendor-rs vendor-py
else
dep: dnf vendor-app vendor-rs
endif

srpm: idenfity dep
	mkdir -p /tmp/rpmbuild/SOURCES
	cp vendor-*.tar.gz fapolicy-analyzer.tar.gz /tmp/rpmbuild/SOURCES
	rpmbuild -bs -D "_topdir /tmp/rpmbuild" \$(spec)
	mkdir -p \$(outdir)
	cp -v /tmp/rpmbuild/SRPMS/* \$(outdir)/
