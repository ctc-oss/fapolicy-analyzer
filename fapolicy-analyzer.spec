%bcond_without check
%bcond_without cli
%bcond_without gui

Summary:       File Access Policy Analyzer
Name:          fapolicy-analyzer
Version:       1.4.0
Release:       1%{?dist}

SourceLicense: GPL-3.0-or-later
# Apache-2.0
# Apache-2.0 OR MIT
# Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT
# BSD-3-Clause
# ISC
# ISC AND OpenSSL AND MIT
# MIT
# MIT OR Apache-2.0
# MIT OR X11 OR Apache-2.0
# MPL-2.0
# Unlicense OR MIT
License:       GPL-3.0-or-later AND Apache-2.0 AND BSD-3-Clause AND ISC AND MIT AND MPL-2.0 AND OpenSSL AND (Apache-2.0 OR MIT) AND (Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT) AND (MIT OR X11 OR Apache-2.0) AND (Unlicense OR MIT)

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

BuildRequires: cargo-rpm-macros
BuildRequires: python3dist(setuptools-rust)

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
Requires:      mesa-dri-drivers
%if 0%{?fedora} < 40
Requires:      webkit2gtk3
%else
Requires:      webkit2gtk4.1
%endif

%global module          fapolicy_analyzer
# pep440 versions handle dev and rc differently, so we call them out explicitly here
%global module_version  %{lua: v = string.gsub(rpm.expand("%{?version}"), "~dev", ".dev"); \
                               v = string.gsub(v, "~rc",  "rc"); print(v) }

%description gui
GUI Tools to assist with the configuration and management of fapolicyd.

%prep
%autosetup -n %{name}
%cargo_prep

%if %{without cli}
# disable tools crate
sed -i '/tools/d' Cargo.toml
%endif

%if %{without gui}
# disable pyo3 crate
sed -i '/pyo3/d' Cargo.toml
%endif

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

%generate_buildrequires
%cargo_generate_buildrequires -a

%build

%if %{with cli}
cargo build --bin tdb --release
%endif

%if %{with gui}
# ensure standard Rust compiler flags are set
export RUSTFLAGS="%{build_rustflags}"

%{python3} setup.py compile_catalog -f
%{python3} help build
%{python3} setup.py bdist_wheel

%{cargo_license_summary}
%{cargo_license} > LICENSE.dependencies
%endif

%install

%if %{with cli}
install -D target/release/tdb %{buildroot}/%{_sbindir}/%{name}-trust
%endif

%if %{with gui}
%{py3_install_wheel %{module}-%{module_version}*%{_target_cpu}.whl}
%{python3} help install --dest %{buildroot}/%{_datadir}/help
install -D bin/%{name} %{buildroot}/%{_sbindir}/%{name}
install -D data/%{name}.8 -t %{buildroot}/%{_mandir}/man8/
install -D data/config.toml -t %{buildroot}%{_sysconfdir}/%{name}/
desktop-file-install data/%{name}.desktop
find locale -name %{name}.mo -exec cp --parents -rv {} %{buildroot}/%{_datadir} \;
%find_lang %{name} --with-gnome
%endif

%check
%if %{with gui}
desktop-file-validate %{buildroot}/%{_datadir}/applications/%{name}.desktop
%endif

%files cli
%attr(755,root,root) %{_sbindir}/%{name}-trust

%files gui
%{python3_sitearch}/%{module}
%{python3_sitearch}/%{module}-%{module_version}*
%attr(755,root,root) %{_sbindir}/%{name}
%attr(644,root,root) %{_mandir}/man8/%{name}.8*
%attr(755,root,root) %{_datadir}/applications/%{name}.desktop
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/%{name}/config.toml
%ghost %attr(640,root,root) %verify(not md5 size mtime) %{_localstatedir}/log/%{name}/%{name}.log

%files -f %{name}.lang
%doc scripts/srpm/README
%license LICENSE
%license LICENSE.dependencies

%changelog
* Sun Jul 28 2024 John Wass <jwass3@gmail.com> 1.4.0-1
- New release
