%bcond_without cli
%bcond_without gui

Summary:       File Access Policy Analyzer
Name:          fapolicy-analyzer
Version:       1.4.0
Release:       1%{?dist}
License:       GPL-3.0-or-later
URL:           https://github.com/ctc-oss/fapolicy-analyzer
Source0:       %{url}/releases/download/v%{version}/%{name}-%{version}.tar.gz

# vendored documentation sources, used to generate help docs
Source1:       %{url}/releases/download/v%{version}/vendor-docs-%{version}.tar.gz

# vendored rust dependencies
Source2:       %{url}/releases/download/v%{version}/vendor-rs-%{version}.tar.gz

# Build-time python dependencies for setuptools-rust
Source10:      %{pypi_source setuptools-rust 1.1.2}
Source12:      %{pypi_source setuptools 59.6.0}
Source13:      %{pypi_source wheel 0.37.0}
Source14:      %{pypi_source setuptools_scm 6.4.2}
Source15:      %{pypi_source semantic_version 2.8.2}
Source16:      %{pypi_source packaging 21.3}
Source17:      %{pypi_source pyparsing 2.1.0}
Source18:      %{pypi_source tomli 1.2.3}
Source19:      %{pypi_source flit_core 3.7.1}
Source20:      %{pypi_source typing_extensions 3.7.4.3}

BuildRequires: python3-devel
BuildRequires: python3dist(pip)
BuildRequires: python3dist(babel)
BuildRequires: python3dist(packaging)
BuildRequires: python3dist(pyparsing)
BuildRequires: python3dist(pytz)

BuildRequires: dbus-devel
BuildRequires: gettext
BuildRequires: itstool
BuildRequires: desktop-file-utils

BuildRequires: clang
BuildRequires: audit-libs-devel
BuildRequires: lmdb-devel

BuildRequires: rust-packaging

BuildRequires: rust-arc-swap-devel
BuildRequires: rust-assert_matches-devel
BuildRequires: rust-autocfg-devel
BuildRequires: rust-bindgen-devel
BuildRequires: rust-block-buffer-devel
BuildRequires: rust-bumpalo-devel
BuildRequires: rust-cc-devel
BuildRequires: rust-cexpr-devel
BuildRequires: rust-cfg-if-devel
BuildRequires: rust-chrono-devel
BuildRequires: rust-clang-sys-devel
BuildRequires: rust-confy-devel
BuildRequires: rust-cpufeatures-devel
BuildRequires: rust-crossbeam-epoch-devel
BuildRequires: rust-crossbeam-utils-devel
BuildRequires: rust-crypto-common-devel
BuildRequires: rust-digest-devel
BuildRequires: rust-directories-devel
BuildRequires: rust-dirs-sys-devel
BuildRequires: rust-either-devel
BuildRequires: rust-generic-array-devel
BuildRequires: rust-getrandom-devel
BuildRequires: rust-glob-devel
BuildRequires: rust-heck-devel
BuildRequires: rust-indoc-devel
BuildRequires: rust-instant-devel
BuildRequires: rust-is_executable-devel
BuildRequires: rust-lazy_static-devel
BuildRequires: rust-libc-devel
BuildRequires: rust-libloading-devel
BuildRequires: rust-lock_api-devel
BuildRequires: rust-log-devel
BuildRequires: rust-memchr-devel
BuildRequires: rust-memoffset-devel
BuildRequires: rust-nom-devel
BuildRequires: rust-num-integer-devel
BuildRequires: rust-num-traits-devel
BuildRequires: rust-num_cpus-devel
BuildRequires: rust-option-ext-devel
BuildRequires: rust-parking_lot-devel
BuildRequires: rust-pkg-config-devel
BuildRequires: rust-proc-macro2-devel
BuildRequires: rust-rayon-devel
BuildRequires: rust-regex-devel
BuildRequires: rust-regex-syntax-devel
BuildRequires: rust-rustc-hash-devel
BuildRequires: rust-sha2-devel
BuildRequires: rust-shlex-devel
BuildRequires: rust-similar-devel
BuildRequires: rust-smallvec-devel
BuildRequires: rust-syn-devel
BuildRequires: rust-target-lexicon-devel
BuildRequires: rust-thiserror-devel
BuildRequires: rust-typenum-devel
BuildRequires: rust-unicode-ident-devel
BuildRequires: rust-unindent-devel
BuildRequires: rust-version_check-devel
BuildRequires: rust-which-devel

%global module          fapolicy_analyzer

%global venv_dir        %{_builddir}/vendor-py
%global venv_py3        %{venv_dir}/bin/python3
%global venv_lib        %{venv_dir}/lib/python3.9/site-packages
%global venv_install    %{venv_py3} -m pip install --find-links=%{_sourcedir} --no-index --quiet

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

%description gui
GUI Tools to assist with the configuration and management of fapolicyd.

%prep

%if %{with gui}
# setuptools-rust is not available as a package. installing it requires
# upgrades of pip, setuptools, wheel, and some transient dependencies.
# install these to a virtual environment to isolate changes, and
# define venv_py3 for accessing the venv python3 interpreter.
%{python3} -m venv %{venv_dir}

# there exists a circular dependency between setuptools <-> wheel,
# by calling setuptools/setup.py before pip'ing we can bypass that
mkdir -p %{_builddir}/setuptools
tar -xzf %{SOURCE12} -C %{_builddir}/setuptools --strip-components=1
%{venv_py3} %{_builddir}/setuptools/setup.py -q install

# now pip install wheel, and setuptools again
%{venv_install} %{SOURCE13}
%{venv_install} %{SOURCE12}

# install setuptools-rust
%{venv_install} %{SOURCE10}

# post install deps linked from system site-packages
ln -sf  %{python3_sitelib}/pytz* %{venv_lib}
ln -sf  %{python3_sitelib}/{Babel*,babel} %{venv_lib}

# An unprivileged user cannot write to the default registry location of
# /usr/share/cargo/registry so we work around this by linking the contents
# of the default registry into a new writable location, and then extract
# the contents of the vendor tarball to this new writable dir.
# The extraction favors the system crates by untaring with --skip-old-files
# Later the Cargo config will be updated to point to this new registry dir
# The crates in the vendor tarball are collected from Rawhide.
CARGO_REG_DIR=%{_builddir}/vendor-rs
mkdir -p ${CARGO_REG_DIR}
for d in %{cargo_registry}/*; do ln -sf ${d} ${CARGO_REG_DIR} || true; done
tar -xzf %{SOURCE2} -C ${CARGO_REG_DIR} --skip-old-files --strip-components=2
%endif

%cargo_prep -v ${CARGO_REG_DIR}

%autosetup -n %{name}

rm Cargo.lock

%if %{without cli}
# disable the dev-tools crate
sed -i '/tools/d' Cargo.toml
%endif

# extract our doc sourcs
tar xvzf %{SOURCE1}

# our setup.py looks up the version from git describe
# this overrides that check to use the RPM version
echo %{module_version} > VERSION

# capture build info
scripts/build-info.py --os --time

%build
# ensure standard Rust compiler flags are set
export RUSTFLAGS="%{build_rustflags}"

%if %{with cli}
cargo build --bin tdb --release
%endif

%if %{with gui}
%{venv_py3} setup.py compile_catalog -f
%{venv_py3} help build
%{venv_py3} setup.py bdist_wheel
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

%files -f %{name}.lang
%doc scripts/srpm/README
%license LICENSE

%changelog
* Sun Jul 28 2024 John Wass <jwass3@gmail.com> 1.4.0-1
- New release
