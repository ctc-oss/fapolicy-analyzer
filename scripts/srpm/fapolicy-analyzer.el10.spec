%bcond_without cli
%bcond_without gui

Summary:       File Access Policy Analyzer
Name:          fapolicy-analyzer
Version:       1.5.0
Release:       1%{?dist}
License:       GPL-3.0-or-later
URL:           https://github.com/ctc-oss/fapolicy-analyzer
Source0:       %{url}/releases/download/v%{version}/%{name}-%{version}.tar.gz

# vendored documentation sources, used to generate help docs
Source1:       %{url}/releases/download/v%{version}/vendor-docs-%{version}.tar.gz

# vendored rust dependencies
Source2:       %{url}/releases/download/v%{version}/vendor-rs-%{version}.tar.gz

BuildRequires: python3-devel
BuildRequires: python3dist(pip)
BuildRequires: python3dist(wheel)

BuildRequires: babel
BuildRequires: gettext
BuildRequires: itstool
BuildRequires: desktop-file-utils

BuildRequires: clang
BuildRequires: audit-libs-devel
BuildRequires: dbus-devel
BuildRequires: lmdb-devel

BuildRequires: uv
BuildRequires: maturin
BuildRequires: rust-packaging

BuildRequires: rust-anstream-devel
BuildRequires: rust-anstyle-query-devel
BuildRequires: rust-arc-swap-devel
BuildRequires: rust-assert_matches-devel
BuildRequires: rust-bindgen-devel
BuildRequires: rust-cc-devel
BuildRequires: rust-chrono-devel
BuildRequires: rust-clap-devel
BuildRequires: rust-clap_derive-devel
BuildRequires: rust-confy-devel
BuildRequires: rust-digest-devel
BuildRequires: rust-directories-devel
BuildRequires: rust-env_logger-devel
BuildRequires: rust-human-panic-devel
BuildRequires: rust-indoc-devel
BuildRequires: rust-is_executable-devel
BuildRequires: rust-iana-time-zone-devel
BuildRequires: rust-jiff-devel
BuildRequires: rust-log-devel
BuildRequires: rust-libloading-devel
BuildRequires: rust-memoffset-devel
BuildRequires: rust-nom7-devel
BuildRequires: rust-notify-devel
BuildRequires: rust-pkg-config-devel
BuildRequires: rust-prettyplease-devel
BuildRequires: rust-pyo3-devel
BuildRequires: rust-pyo3-macros-devel
BuildRequires: rust-rayon-devel
BuildRequires: rust-serde-devel
BuildRequires: rust-sha2-devel
BuildRequires: rust-similar-devel
BuildRequires: rust-strip-ansi-escapes-devel
BuildRequires: rust-strsim-devel
BuildRequires: rust-tempfile-devel
BuildRequires: rust-thiserror-devel
BuildRequires: rust-unindent-devel
BuildRequires: rust-yansi-devel

%global module          fapolicy_analyzer

# pep440 versions handle dev and rc differently, so we call them out explicitly here
%global module_version  %{lua: v = string.gsub(rpm.expand("%{?version}"), "~dev", ".dev"); \
                               v = string.gsub(v, "~rc",  "rc"); print(v) }

Requires:      %{name}-cli
Requires:      %{name}-gui

%description
Tools to assist with the configuration and management of fapolicyd.


%package cli
Summary:       File Access Policy Analyzer CLI

%description cli
CLI Tools to assist with the configuration and management of fapolicyd.


%package gui
Summary:       File Access Policy Analyzer GUI

Requires:      python3
Requires:      python3-gobject
Requires:      python3-configargparse
Requires:      python3-more-itertools
Requires:      python3-rx
Requires:      python3-tomli

Requires:      gtk3
Requires:      gtksourceview3
Requires:      gnome-icon-theme

# runtime required for rendering user guide
Requires:      webkit2gtk4.1
Requires:      mesa-dri-drivers

%description gui
GUI Tools to assist with the configuration and management of fapolicyd.

%prep

# An unprivileged user cannot write to the default registry location of
# /usr/share/cargo/registry so we work around this by copying the contents
# of the default registry into a new writable location, and then extracting
# the contents of the vendor tarball to this new writable dir.
# The extraction favors the system crates by untaring with --skip-old-files.
# The crates in the vendor tarball are collected from the latest stable fc.
CARGO_REG_DIR=%{_builddir}/vendor-rs
mkdir -p ${CARGO_REG_DIR}
for d in %{cargo_registry}/*; do cp -r ${d} ${CARGO_REG_DIR} || true; done
tar -xzf %{SOURCE2} -C ${CARGO_REG_DIR} --no-same-owner --skip-old-files --strip-components=2

touch ${CARGO_REG_DIR}/jiff-*/{README.md,PLATFORM.md,CHANGELOG.md,DESIGN.md}
touch ${CARGO_REG_DIR}/is_executable-*/README.md
touch ${CARGO_REG_DIR}/getrandom-*/README.md
touch ${CARGO_REG_DIR}/clap_builder-*/README.md
touch ${CARGO_REG_DIR}/clap_derive-*/README.md

%cargo_prep -v ${CARGO_REG_DIR}
%autosetup -n %{name}

%if %{without cli}
# disable the dev-tools crate
sed -i '/tools/d' Cargo.toml
%endif

# extract our doc sourcs
tar xvzf %{SOURCE1}

# patch pyproject.toml version
scripts/version.py --patch --toml pyproject.toml --version %{module_version}

# capture build info
scripts/build-info.py --os --time

%build
# ensure standard Rust compiler flags are set
export RUSTFLAGS="%{build_rustflags}"

%if %{with cli}
cargo build --release -p fapolicy-tools --bin tdb
cargo build --release -p fapolicy-tools --bin faprofiler
cargo build --release -p fapolicy-tools --bin rulec --features pretty
%endif

%if %{with gui}
pybabel compile -f -d locale -D fapolicy-analyzer
%{python3} help build
maturin build --release --skip-auditwheel -o dist
%endif


%install

%if %{with cli}
install -D target/release/tdb %{buildroot}/%{_sbindir}/%{name}-cli-trust
install -D target/release/faprofiler %{buildroot}/%{_sbindir}/%{name}-cli-profiler
install -D target/release/rulec %{buildroot}/%{_sbindir}/%{name}-cli-rules
%endif

%if %{with gui}
wheel=$(basename dist/*.whl)
%{py3_install_wheel $wheel}
%{python3} help install --dest %{buildroot}/%{_datadir}/help
install -D bin/%{name} %{buildroot}/%{_sbindir}/%{name}
install -D data/%{name}.8 -t %{buildroot}/%{_mandir}/man8/
install -D data/%{name}-cli-*.8 -t %{buildroot}/%{_mandir}/man8/
desktop-file-install data/%{name}.desktop
find locale -name %{name}.mo -exec cp --parents -rv {} %{buildroot}/%{_datadir} \;
%find_lang %{name} --with-gnome

# remove gui entrypoint
rm %{buildroot}/%{_bindir}/gui
%endif

%{cargo_license_summary}
%{cargo_license} > LICENSE.dependencies

%check
%if %{with gui}
desktop-file-validate %{buildroot}/%{_datadir}/applications/%{name}.desktop
%endif

%files cli
%attr(755,root,root) %{_sbindir}/%{name}-cli-trust
%attr(755,root,root) %{_sbindir}/%{name}-cli-profiler
%attr(755,root,root) %{_sbindir}/%{name}-cli-rules

%files gui
%{python3_sitearch}/%{module}
%{python3_sitearch}/%{module}-%{module_version}*
%attr(755,root,root) %{_sbindir}/%{name}
%attr(644,root,root) %{_mandir}/man8/%{name}.8*
%attr(644,root,root) %{_mandir}/man8/%{name}-cli-*.8*
%attr(755,root,root) %{_datadir}/applications/%{name}.desktop

%files -f %{name}.lang
%doc scripts/srpm/README
%license LICENSE

%changelog
* Tue Dec 31 2024 John Wass <jwass3@gmail.com> 1.5.0-1
- New release
