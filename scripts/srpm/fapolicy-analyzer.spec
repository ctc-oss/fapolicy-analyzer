Summary:       File Access Policy Analyzer
Name:          fapolicy-analyzer
Version:       0.6.1
Release:       1%{?dist}
License:       GPLv3+
URL:           https://github.com/ctc-oss/fapolicy-analyzer
Source0:       fapolicy-analyzer.tar.gz
Source1:       vendor-rs.tar.gz

# on copr the source containter is never el
%if 0%{?rhel} || 0%{?fedora} < 37
Source2:       %{pypi_source setuptools-rust 1.1.2}
Source3:       %{pypi_source pip 21.3.1}
Source4:       %{pypi_source setuptools 59.6.0}
Source5:       %{pypi_source wheel 0.37.0}
Source6:       %{pypi_source setuptools_scm 6.4.2}
Source7:       %{pypi_source semantic_version 2.8.2}
Source8:       %{pypi_source packaging 21.3}
Source9:       %{pypi_source pyparsing 2.1.0}
Source10:      %{pypi_source tomli 1.2.3}
Source11:      %{pypi_source flit_core 3.7.1}
Source12:      %{pypi_source typing_extensions 3.7.4.3}
Source13:      https://files.pythonhosted.org/packages/source/p/pytz/pytz-2017.2.zip
%endif

BuildRequires: python3-devel
BuildRequires: python3dist(setuptools)
BuildRequires: python3dist(pip)
BuildRequires: python3dist(wheel)
BuildRequires: python3dist(babel)
BuildRequires: dbus-devel

%if 0%{?rhel}
BuildRequires: rust-toolset
BuildRequires: python3dist(toml)
BuildRequires: python3dist(typing-extensions)
BuildRequires: git
%else
BuildRequires: rust-packaging
BuildRequires: python3dist(setuptools-rust)

# crates
BuildRequires: rust-arrayvec0.5-devel
BuildRequires: rust-atty-devel
BuildRequires: rust-autocfg-devel
BuildRequires: rust-bitflags-devel
BuildRequires: rust-bitvec-devel
BuildRequires: rust-bumpalo-devel
BuildRequires: rust-byteorder-devel
BuildRequires: rust-cc-devel
BuildRequires: rust-cfg-if-devel
BuildRequires: rust-chrono-devel
BuildRequires: rust-clap-devel
BuildRequires: rust-clap_derive-devel
BuildRequires: rust-confy-devel
BuildRequires: rust-crossbeam-channel-devel
BuildRequires: rust-crossbeam-deque-devel
BuildRequires: rust-crossbeam-epoch-devel
BuildRequires: rust-crossbeam-utils-devel
BuildRequires: rust-data-encoding-devel
BuildRequires: rust-dbus-devel
BuildRequires: rust-dirs-sys-devel
BuildRequires: rust-either-devel
BuildRequires: rust-fastrand-devel
BuildRequires: rust-funty-devel
BuildRequires: rust-getrandom-devel
BuildRequires: rust-hashbrown-devel
BuildRequires: rust-heck-devel
BuildRequires: rust-iana-time-zone-devel
BuildRequires: rust-indexmap-devel
BuildRequires: rust-instant-devel
BuildRequires: rust-lazy_static-devel
BuildRequires: rust-lexical-core-devel
BuildRequires: rust-libc-devel
BuildRequires: rust-libdbus-sys-devel
BuildRequires: rust-lock_api-devel
BuildRequires: rust-log-devel
BuildRequires: rust-memchr-devel
BuildRequires: rust-memoffset-devel
BuildRequires: rust-num-integer-devel
BuildRequires: rust-num-traits-devel
BuildRequires: rust-num_cpus-devel
BuildRequires: rust-once_cell-devel
BuildRequires: rust-parking_lot-devel
BuildRequires: rust-parking_lot_core-devel
BuildRequires: rust-pkg-config-devel
BuildRequires: rust-proc-macro-error-devel
BuildRequires: rust-proc-macro-error-attr-devel
BuildRequires: rust-proc-macro-hack-devel
BuildRequires: rust-proc-macro2-devel
BuildRequires: rust-pyo3-devel
BuildRequires: rust-pyo3-build-config-devel
BuildRequires: rust-pyo3-macros-devel
BuildRequires: rust-pyo3-macros-backend-devel
BuildRequires: rust-quote-devel
BuildRequires: rust-radium-devel
BuildRequires: rust-rayon-devel
BuildRequires: rust-rayon-core-devel
BuildRequires: rust-remove_dir_all-devel
BuildRequires: rust-ring-devel
BuildRequires: rust-ryu-devel
BuildRequires: rust-scopeguard-devel
BuildRequires: rust-serde-devel
BuildRequires: rust-serde_derive-devel
BuildRequires: rust-similar-devel
BuildRequires: rust-smallvec-devel
BuildRequires: rust-spin-devel
BuildRequires: rust-static_assertions-devel
BuildRequires: rust-strsim-devel
BuildRequires: rust-syn-devel
BuildRequires: rust-tap-devel
BuildRequires: rust-tempfile-devel
BuildRequires: rust-termcolor-devel
BuildRequires: rust-textwrap-devel
BuildRequires: rust-thiserror-devel
BuildRequires: rust-thiserror-impl-devel
BuildRequires: rust-time0.1-devel
BuildRequires: rust-toml-devel
BuildRequires: rust-unicode-segmentation-devel
BuildRequires: rust-unicode-width-devel
BuildRequires: rust-unicode-xid-devel
BuildRequires: rust-unindent-devel
BuildRequires: rust-untrusted-devel
BuildRequires: rust-vec_map-devel
BuildRequires: rust-version_check-devel
BuildRequires: rust-wyz-devel
BuildRequires: rust-yansi-devel
BuildRequires: rust-paste-devel
BuildRequires: rust-indoc-devel
%endif

Requires:      python3
Requires:      python3-gobject
Requires:      python3-events
Requires:      python3-configargparse
Requires:      python3-more-itertools
Requires:      python3-rx
Requires:      python3-importlib-metadata
Requires:      gtk3
Requires:      dbus-libs
Requires:      gtksourceview3

%if 0%{?rhel}
Requires:      python3-dataclasses
Requires:      python3-importlib-resources
%endif

%global modname fapolicy_analyzer

%description
Tools to assist with the configuration and maintenance of Fapolicyd (File Access Policy Daemon).

%prep

%if 0%{?rhel}
# on rhel we vendor everything
%cargo_prep -V1
%else
# Goal:     Hybrid crate dependencies, mixing packages and vendored
# Problem:  the /usr/share/cargo/registry location is not writable, blocking the install of vendored crates
# Solution: link the contents of the /usr/share/cargo/registry into a replacement writable registry
#           extract the contents of the vendored crate tarball to the replacement writable registry
CARGO_REG_DIR=%{_sourcedir}/vendor
mkdir -p ${CARGO_REG_DIR}
for d in %{cargo_registry}/*; do ln -sf ${d} ${CARGO_REG_DIR}; done
tar xzf %{_sourcedir}/vendor-rs.tar.gz -C ${CARGO_REG_DIR} --strip-components=2

%cargo_prep
%endif

# remap the registry location in the .cargo/config to the replacement registry
sed -i "s#%{cargo_registry}#${CARGO_REG_DIR}#g" .cargo/config

# on rhel we are missing setuptools-rust, and to get it requires
# upgrades of pip, setuptools, and wheel along with several other dependencies
%if 0%{?rhel}
python3 -m venv /tmp/v
alias python3=/tmp/v/bin/python3

# the offline installs seem to require upgraded pip
python3 -m pip install %{SOURCE3} --no-index --quiet

# the following breaks the setuptools <-> wheel circular dependency
# by calling setuptools/setup.py before calling pip install on either
mkdir -p %{_builddir}/setuptools
tar xzf %{SOURCE4} -C %{_builddir}/setuptools --strip-components=1
cd %{_builddir}/setuptools
python3 setup.py -q install
python3 -m pip install %{SOURCE5} --find-links=%{_sourcedir} --no-index --quiet
python3 -m pip install %{SOURCE4} --find-links=%{_sourcedir} --no-index --quiet

# install setuptools-rust, the known dependencies will install with it
python3 -m pip install %{SOURCE2} --find-links=%{_sourcedir} --no-index --quiet

# other dependencies
ln -sf /usr/lib/python3.6/site-packages/{Babel*,babel} /tmp/v/lib/python3.6/site-packages
python3 -m pip install %{SOURCE12} --find-links=%{_sourcedir} --no-index --quiet
python3 -m pip install %{SOURCE13} --find-links=%{_sourcedir} --no-index --quiet

# switch venv back to original pip to ensure packaging
rm -rf /tmp/v/lib/python3.6/site-packages/pip*
cp -r  /usr/lib/python3.6/site-packages/pip* /tmp/v/lib/python3.6/site-packages

%endif

%autosetup -p0 -n %{name}

# throw out the checked-in lock
# this build will use whatever is available in the replacement registry
rm Cargo.lock

# our setup.py looks up the version from git describe
# this overrides that check to the RPM version
echo %{version} > VERSION

%build

%if 0%{?rhel}
alias python3=/tmp/v/bin/python3
%endif

python3 setup.py compile_catalog -f
python3 setup.py bdist_wheel

%install

install bin/%{name} %{buildroot}%{_sbindir}/%{name} -D
%{py3_install_wheel %{modname}-%{version}*%{_arch}.whl}

%check

%files -n %{name}
%doc README.md
%license LICENSE
%{python3_sitearch}/%{modname}
%{python3_sitearch}/%{modname}-%{version}*
%attr(755,root,root) %{_sbindir}/fapolicy-analyzer

%changelog
* Fri Sep 09 2022 John Wass <jwass3@gmail.com> 0.6.1-1
- New release
