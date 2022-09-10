.PHONY : clean dnf vendor srpm

clean:
	rm fapolicy-analyzer.tar.gz
	rm crates.tar.gz

dnf:
	dnf install -y git gettext rust-packaging python3-devel python3-pip openssl-devel python-toml python-beautifulsoup4 python-requests
	cargo install cargo-vendor-filterer

vendor:
	cargo check
	git archive HEAD -o fapolicy-analyzer.tar.gz --prefix=fapolicy-analyzer/
	./scripts/srpm/vendor.sh

srpm: dnf vendor
	mkdir -p /tmp/rpmbuild/SOURCES
	cp crates.tar.gz fapolicy-analyzer.tar.gz /tmp/rpmbuild/SOURCES
	rpmbuild -bs -D "_topdir /tmp/rpmbuild" \$(spec)
	mkdir -p \$(outdir)
	cp -v /tmp/rpmbuild/SRPMS/* \$(outdir)/
