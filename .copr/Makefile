.PHONY: clean identify prepfs dnf vendor vendor-app vendor-py vendor-rs dep srpm
.SILENT: clean

OS_PRETTY_NAME = $(shell grep /etc/os-release -e "^PRETTY_NAME=" | tr -d '"' | cut -d= -f2 | cut -d: -f1)
OS_ID_FN =       $(shell grep /etc/os-release -e "^ID=" | tr -d '"' | cut -d= -f2 | cut -d: -f1)
OS_ID   ?=       $(OS_ID_FN)

identify:
	@echo "Platform: $(OS_PRETTY_NAME) (id: $(OS_ID))"

prepfs: prep_outdir prep_rpmbuild_dir

prep_outdir:
	mkdir -p \$(outdir)

prep_rpmbuild_dir:
	mkdir -p /tmp/rpmbuild/SOURCES/

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
	dnf install -y git which openssl-devel dbus-devel python3-devel python3-pip python3-toml python3-beautifulsoup4 python3-requests python3-babel python3-markdown2 itstool
	dnf install -y rust-packaging || true
	dnf install -y rust-toolset || true
	cargo install cargo-vendor-filterer

dnf-rpmdev:
	# only dependent for spectool in python-py
	dnf install -y rpmdevtools

ifeq ($(OS_ID),rhel)
# we only need to vendor rust and python on rhel
vendor: prep_rpmbuild_dir vendor-app vendor-doc vendor-rs vendor-py
else
vendor: prep_rpmbuild_dir vendor-app vendor-doc
endif

vendor-app:
	git archive HEAD -o fapolicy-analyzer.tar.gz --prefix=fapolicy-analyzer/
	cp fapolicy-analyzer.tar.gz /tmp/rpmbuild/SOURCES/

vendor-py:
	which spectool && spectool -gf -C /tmp/rpmbuild/SOURCES/ \$(spec) || true

vendor-rs:
	cargo check
	./scripts/srpm/vendor-rs.sh
	cp vendor-rs.tar.gz /tmp/rpmbuild/SOURCES/

vendor-doc:
	python3 help update
	tar --exclude=es --exclude=*.py --exclude=.gitignore -cvzf vendor-docs.tar.gz help
	cp vendor-docs.tar.gz /tmp/rpmbuild/SOURCES/

srpm: identify prepfs dnf vendor
	rpmbuild -bs -D "_topdir /tmp/rpmbuild" \$(spec)
	cp -v /tmp/rpmbuild/SRPMS/* \$(outdir)/
