.PHONY : clean dnf vendor srpm

clean:
	rm fapolicy-analyzer.tar.gz
	rm vendor-rs.tar.gz
	rm vendor-py.tar.gz

dnf:
	dnf install -y git openssl-devel dbus-devel python3-devel python3-pip python3-toml python3-beautifulsoup4 python3-requests python3-babel
	dnf install -y rust-packaging || true
	dnf install -y rust-toolset || true
	cargo install cargo-vendor-filterer

vendor:
	cargo check
	git archive HEAD -o fapolicy-analyzer.tar.gz --prefix=fapolicy-analyzer/
	./scripts/srpm/vendor.sh

srpm: dnf vendor
	mkdir -p /tmp/rpmbuild/SOURCES
	cp vendor-rs.tar.gz vendor-py.tar.gz fapolicy-analyzer.tar.gz /tmp/rpmbuild/SOURCES
	rpmbuild -bs -D "_topdir /tmp/rpmbuild" \$(spec)
	mkdir -p \$(outdir)
	cp -v /tmp/rpmbuild/SRPMS/* \$(outdir)/
