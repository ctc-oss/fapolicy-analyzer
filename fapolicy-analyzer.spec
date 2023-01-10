Summary:       File Access Policy Analyzer
Name:          fapolicy-analyzer
Version:       0.6.5
Release:       1%{?dist}
License:       GPLv3+
URL:           https://github.com/ctc-oss/fapolicy-analyzer
Source0:       %{url}/releases/download/v%{version}/fapolicy-analyzer.tar.gz

BuildRequires: python3-devel
BuildRequires: python3dist(setuptools)
BuildRequires: python3dist(pip)
BuildRequires: python3dist(wheel)
BuildRequires: python3dist(babel)
BuildRequires: dbus-devel
BuildRequires: gettext
BuildRequires: itstool
BuildRequires: desktop-file-utils

BuildRequires: rust-packaging
BuildRequires: python3dist(setuptools-rust)

BuildRequires: rust-autocfg-devel
BuildRequires: rust-bitflags-devel
BuildRequires: rust-bumpalo-devel
BuildRequires: rust-byteorder-devel
BuildRequires: rust-cc-devel
BuildRequires: rust-cfg-if-devel
BuildRequires: rust-chrono-devel
BuildRequires: rust-confy-devel
BuildRequires: rust-crossbeam-channel-devel
BuildRequires: rust-crossbeam-deque-devel
BuildRequires: rust-crossbeam-epoch-devel
BuildRequires: rust-crossbeam-utils-devel
BuildRequires: rust-data-encoding-devel
BuildRequires: rust-dbus-devel
BuildRequires: rust-directories-devel
BuildRequires: rust-dirs-sys-devel
BuildRequires: rust-either-devel
BuildRequires: rust-fastrand-devel
BuildRequires: rust-getrandom-devel
BuildRequires: rust-iana-time-zone-devel
BuildRequires: rust-instant-devel
BuildRequires: rust-lazy_static-devel
BuildRequires: rust-libc-devel
BuildRequires: rust-libdbus-sys-devel
BuildRequires: rust-lmdb-devel
BuildRequires: rust-lock_api-devel
BuildRequires: rust-log-devel
BuildRequires: rust-memchr-devel
BuildRequires: rust-memoffset-devel
BuildRequires: rust-minimal-lexical-devel
BuildRequires: rust-nom-devel
BuildRequires: rust-num-integer-devel
BuildRequires: rust-num-traits-devel
BuildRequires: rust-num_cpus-devel
BuildRequires: rust-once_cell-devel
BuildRequires: rust-parking_lot-devel
BuildRequires: rust-parking_lot_core-devel
BuildRequires: rust-pkg-config-devel
BuildRequires: rust-proc-macro-hack-devel
BuildRequires: rust-proc-macro2-devel
BuildRequires: rust-pyo3-devel
BuildRequires: rust-pyo3-build-config-devel
BuildRequires: rust-pyo3-macros-devel
BuildRequires: rust-pyo3-macros-backend-devel
BuildRequires: rust-quote-devel
BuildRequires: rust-rayon-devel
BuildRequires: rust-rayon-core-devel
BuildRequires: rust-remove_dir_all-devel
BuildRequires: rust-ring-devel
BuildRequires: rust-scopeguard-devel
BuildRequires: rust-serde-devel
BuildRequires: rust-serde_derive-devel
BuildRequires: rust-similar-devel
BuildRequires: rust-smallvec-devel
BuildRequires: rust-spin-devel
BuildRequires: rust-syn-devel
BuildRequires: rust-tempfile-devel
BuildRequires: rust-thiserror-devel
BuildRequires: rust-thiserror-impl-devel
BuildRequires: rust-time0.1-devel
BuildRequires: rust-toml-devel
BuildRequires: rust-unicode-xid-devel
BuildRequires: rust-unindent-devel
BuildRequires: rust-untrusted-devel
BuildRequires: rust-paste-devel
BuildRequires: rust-indoc-devel

Requires:      python3
Requires:      python3-gobject
Requires:      python3-events
Requires:      python3-configargparse
Requires:      python3-more-itertools
Requires:      python3-rx
Requires:      python3-importlib-metadata
Requires:      gtk3
Requires:      gtksourceview3

%global module fapolicy_analyzer

%description
Tools to assist with the configuration and management of fapolicyd.

%prep
%cargo_prep

%autosetup -n %{name}

# throw out the checked-in lock
# this build will use what is available from the local registry
rm Cargo.lock

# disable dev-tools crate
sed -i '/tools/d' Cargo.toml

# our setup.py looks up the version from git describe
# this overrides that check to the RPM version
echo %{version} > VERSION

%build
%{python3} setup.py compile_catalog -f
%{python3} setup.py bdist_wheel

%install
%{py3_install_wheel %{module}-%{version}*%{_arch}.whl}
install -D bin/%{name} %{buildroot}/%{_sbindir}/%{name}
install -D data/fapolicy-analyzer.8 -t %{buildroot}/%{_mandir}/man8/
desktop-file-install data/fapolicy-analyzer.desktop
find locale -name %{name}.mo -exec cp --parents -rv {} %{buildroot}/%{_datadir} \;
%find_lang %{name}

%check
desktop-file-validate %{buildroot}/%{_datadir}/applications/%{name}.desktop

%files -n %{name} -f %{name}.lang
%doc scripts/srpm/README
%license LICENSE
%{python3_sitearch}/%{module}
%{python3_sitearch}/%{module}-%{version}*
%attr(755,root,root) %{_sbindir}/fapolicy-analyzer
%attr(644,root,root) %{_mandir}/man8/fapolicy-analyzer.8*
%attr(755,root,root) %{_datadir}/applications/%{name}.desktop

%changelog
* Fri Jan 06 2023 John Wass <jwass3@gmail.com> 0.6.5-1
- New release
