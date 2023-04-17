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
dnf: dnf-common dnf-el
else
dnf: dnf-common dnf-fc
endif

dnf-common:
	dnf install -y git which openssl-devel dbus-devel python3-devel python3-pip python3-toml python3-beautifulsoup4 python3-requests python3-babel python3-markdown2 itstool

dnf-fc:
	dnf install -y rust-packaging

dnf-el:
	dnf install -y rpmdevtools
	dnf install -y rust-toolset
	# v0.5.9 requires rust 1.64
	cargo install cargo-vendor-filterer@0.5.8

ifeq ($(OS_ID),rhel)
# we only need to vendor rust and python on rhel
vendor: prep_rpmbuild_dir vendor-app vendor-doc vendor-rs vendor-py
else
vendor: prep_rpmbuild_dir vendor-app vendor-doc
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

vendor-doc:
	python3 help update
	tar --exclude=es --exclude=*.py --exclude=.gitignore -cvzf vendor-docs.tar.gz help
	cp vendor-docs.tar.gz /tmp/rpmbuild/SOURCES/

build:
	rpmbuild -bs -D "_topdir /tmp/rpmbuild" \$(spec)

export:
	mkdir -p \$(outdir)/
	cp -v /tmp/rpmbuild/SRPMS/* \$(outdir)/

# the copr entrypoint
srpm: idenfity dnf vendor move-sources build export
