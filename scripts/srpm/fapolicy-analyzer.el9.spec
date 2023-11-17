Summary:       File Access Policy Analyzer
Name:          fapolicy-analyzer
Version:       1.2.1
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
BuildRequires: python3dist(tomli)
BuildRequires: python3dist(flit-core)
BuildRequires: python3dist(typing-extensions)
BuildRequires: python3dist(pytz)

BuildRequires: dbus-devel
BuildRequires: gettext
BuildRequires: itstool
BuildRequires: desktop-file-utils

BuildRequires: clang
BuildRequires: audit-libs-devel

BuildRequires: rust-packaging

BuildRequires: rust-assert_matches-devel
BuildRequires: rust-autocfg-devel
BuildRequires: rust-bitflags-devel
BuildRequires: rust-bumpalo-devel
BuildRequires: rust-byteorder-devel
BuildRequires: rust-cc-devel
BuildRequires: rust-cfg-if-devel
BuildRequires: rust-chrono-devel
#BuildRequires: rust-confy-devel
BuildRequires: rust-crossbeam-channel-devel
BuildRequires: rust-crossbeam-deque-devel
BuildRequires: rust-crossbeam-epoch-devel
BuildRequires: rust-crossbeam-utils-devel
BuildRequires: rust-data-encoding-devel
#BuildRequires: rust-dbus-devel
BuildRequires: rust-directories-devel
BuildRequires: rust-dirs-sys-devel
BuildRequires: rust-either-devel
BuildRequires: rust-fastrand-devel
BuildRequires: rust-getrandom-devel
BuildRequires: rust-iana-time-zone-devel
BuildRequires: rust-is_executable-devel
BuildRequires: rust-instant-devel
BuildRequires: rust-lazy_static-devel
BuildRequires: rust-libc-devel
#BuildRequires: rust-libdbus-sys-devel
#BuildRequires: rust-lmdb-devel
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
#BuildRequires: (crate(pyo3/default) >= 0.15.0 with crate(pyo3/default) < 0.16.0)
#BuildRequires: (crate(pyo3-macros/default) >= 0.15.0 with crate(pyo3-macros/default) < 0.16.0)
#BuildRequires: (crate(pyo3-build-config/default) >= 0.15.0 with crate(pyo3-build-config/default) < 0.16.0)
#BuildRequires: (crate(pyo3-macros-backend/default) >= 0.15.0 with crate(pyo3-macros-backend/default) < 0.16.0)
#BuildRequires: rust-pyo3-log-devel
BuildRequires: rust-quote-devel
BuildRequires: rust-rayon-devel
BuildRequires: rust-rayon-core-devel
BuildRequires: rust-remove_dir_all-devel
#BuildRequires: rust-ring-devel
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
#BuildRequires: rust-untrusted-devel
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

%global module          fapolicy_analyzer

%global venv_dir        %{_builddir}/vendor-py
%global venv_py3        %{venv_dir}/bin/python3
%global venv_lib        %{venv_dir}/lib/python3.9/site-packages
%global venv_install    %{venv_py3} -m pip install --find-links=%{_sourcedir} --no-index --quiet

# pep440 versions handle dev and rc differently, so we call them out explicitly here
%global module_version  %{lua: v = string.gsub(rpm.expand("%{?version}"), "~dev", ".dev"); \
                               v = string.gsub(v, "~rc",  "rc"); print(v) }

%description
Tools to assist with the configuration and management of fapolicyd.

%prep
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
# The extraction favor the system crates by untaring with --skip-old-files
# Later the Cargo config will be updated to point to this new registry dir
CARGO_REG_DIR=%{_builddir}/vendor-rs
mkdir -p ${CARGO_REG_DIR}
for d in %{cargo_registry}/*; do ln -sf ${d} ${CARGO_REG_DIR} || true; done
tar -xzf %{SOURCE2} -C ${CARGO_REG_DIR} --skip-old-files --strip-components=2

%cargo_prep

# here the Cargo config is updated to point to the new registry dir
sed -i "s#%{cargo_registry}#${CARGO_REG_DIR}#g" .cargo/config

%autosetup -n %{name}

rm Cargo.lock

# disable the dev-tools crate
sed -i '/tools/d' Cargo.toml

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

%{venv_py3} setup.py compile_catalog -f
%{venv_py3} help build
%{venv_py3} setup.py bdist_wheel

%install
%{py3_install_wheel %{module}-%{module_version}*%{_target_cpu}.whl}
%{python3} help install --dest %{buildroot}/%{_datadir}/help
install -D bin/%{name} %{buildroot}/%{_sbindir}/%{name}
install -D data/%{name}.8 -t %{buildroot}/%{_mandir}/man8/
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

%changelog
* Fri Nov 17 2023 John Wass <jwass3@gmail.com> 1.2.1-1
- New release
