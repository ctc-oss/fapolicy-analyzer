Summary:       File Access Policy Analyzer
Name:          fapolicy-analyzer
Version:       1.1.0
Release:       1%{?dist}
License:       GPL-3.0-or-later
URL:           https://github.com/ctc-oss/fapolicy-analyzer
Source0:       %{url}/releases/download/v%{version}/%{name}-%{version}.tar.gz

# this tarball contains documentation used to generate help docs
Source1:       %{url}/releases/download/v%{version}/vendor-docs-%{version}.tar.gz

BuildRequires: python3-devel
BuildRequires: python3dist(setuptools)
BuildRequires: python3dist(pip)
BuildRequires: python3dist(wheel)
BuildRequires: python3dist(babel)
BuildRequires: dbus-devel
BuildRequires: gettext
BuildRequires: itstool
BuildRequires: desktop-file-utils

BuildRequires: clang
BuildRequires: audit-libs-devel

BuildRequires: rust-packaging
BuildRequires: python3dist(setuptools-rust)

BuildRequires: rust-assert_matches-devel
BuildRequires: rust-autocfg-devel
BuildRequires: (crate(bindgen/default) = 0.63.0)
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
%if 0%{?fedora} < 39
BuildRequires: (crate(directories/default) >= 0.4.0 with crate(directories/default) < 0.5.0)
%else
BuildRequires: rust-directories-devel
%endif
BuildRequires: rust-dirs-sys-devel
BuildRequires: rust-either-devel
BuildRequires: rust-fastrand-devel
BuildRequires: rust-getrandom-devel
BuildRequires: rust-iana-time-zone-devel
BuildRequires: rust-is_executable-devel
BuildRequires: rust-instant-devel
BuildRequires: rust-libloading-devel
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
BuildRequires: (crate(pyo3/default) >= 0.15.0 with crate(pyo3/default) < 0.16.0)
BuildRequires: (crate(pyo3-macros/default) >= 0.15.0 with crate(pyo3-macros/default) < 0.16.0)
BuildRequires: (crate(pyo3-build-config/default) >= 0.15.0 with crate(pyo3-build-config/default) < 0.16.0)
BuildRequires: (crate(pyo3-macros-backend/default) >= 0.15.0 with crate(pyo3-macros-backend/default) < 0.16.0)
BuildRequires: rust-pyo3-log-devel
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
BuildRequires: rust-which-devel
BuildRequires: rust-paste-devel
BuildRequires: rust-indoc-devel

Requires:      python3
Requires:      python3-gobject
Requires:      python3-events
Requires:      python3-configargparse
Requires:      python3-more-itertools
Requires:      python3-rx
Requires:      python3-importlib-metadata
Requires:      python3-toml

Requires:      gtk3
Requires:      gtksourceview3
Requires:      gnome-icon-theme

# runtime required for rendering user guide
Requires:      webkit2gtk3
Requires:      mesa-dri-drivers

# rust-ring-devel does not support s390x and ppc64le:
# https://bugzilla.redhat.com/show_bug.cgi?id=1869980
ExcludeArch:   s390x %{power64}

%global module          fapolicy_analyzer
# pep440 versions handle dev and rc differently, so we call them out explicitly here
%global module_version  %{lua: v = string.gsub(rpm.expand("%{?version}"), "~dev", ".dev"); \
                               v = string.gsub(v, "~rc",  "rc"); print(v) }

%description
Tools to assist with the configuration and management of fapolicyd.

%prep
%autosetup -n %{name}
%cargo_prep

# disable dev-tools crate
sed -i '/tools/d' Cargo.toml

# extract our doc sourcs
tar xvzf %{SOURCE1}

# our setup.py looks up the version from git describe
# this overrides that check to use the RPM version
echo %{module_version} > VERSION

# capture build info
scripts/build-info.py --os --time

# enable the audit feature for 39 and up
%if 0%{?fedora} >= 39
echo "audit" > FEATURES
%endif

%build
# ensure standard Rust compiler flags are set
export RUSTFLAGS="%{build_rustflags}"

%{python3} setup.py compile_catalog -f
%{python3} help build
%{python3} setup.py bdist_wheel

%install
%{py3_install_wheel %{module}-%{module_version}*%{_target_cpu}.whl}
%{python3} help install --dest %{buildroot}/%{_datadir}/help
install -D bin/%{name} %{buildroot}/%{_sbindir}/%{name}
install -D data/%{name}.8 -t %{buildroot}/%{_mandir}/man8/
install -D data/config.toml -t %{buildroot}%{_sysconfdir}/%{name}/
desktop-file-install data/%{name}.desktop
find locale -name %{name}.mo -exec cp --parents -rv {} %{buildroot}/%{_datadir} \;
%find_lang %{name} --with-gnome

%check
desktop-file-validate %{buildroot}/%{_datadir}/applications/%{name}.desktop

%files -n %{name} -f %{name}.lang
%doc scripts/srpm/README
%license LICENSE
%{python3_sitearch}/%{module}
%{python3_sitearch}/%{module}-%{module_version}*
%attr(755,root,root) %{_sbindir}/%{name}
%attr(644,root,root) %{_mandir}/man8/%{name}.8*
%attr(755,root,root) %{_datadir}/applications/%{name}.desktop
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/%{name}/config.toml
%ghost %attr(640,root,root) %verify(not md5 size mtime) %{_localstatedir}/log/%{name}/%{name}.log

%changelog
* Tue Jul 11 2023 John Wass <jwass3@gmail.com> 1.1.0-1
- New release
