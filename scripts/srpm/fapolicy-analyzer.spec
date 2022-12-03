Summary:       File Access Policy Analyzer
Name:          fapolicy-analyzer
Version:       1.0.0~rc2
Release:       1%{?dist}
License:       GPLv3+
URL:           https://github.com/ctc-oss/fapolicy-analyzer
Source0:       fapolicy-analyzer.tar.gz

# this tarball contains bundled crates not available in Fedora
# reference: https://bugzilla.redhat.com/show_bug.cgi?id=2124697#c5
Source1:       vendor-rs.tar.gz

# this tarball contains documentation used to generate help docs
Source2:       vendor-docs.tar.gz

# on copr the source containter is never el
# we check for low fc version here to remedy that
%if 0%{?rhel} || 0%{?fedora} < 37
Source10:       %{pypi_source setuptools-rust 1.1.2}
Source11:       %{pypi_source pip 21.3.1}
Source12:       %{pypi_source setuptools 59.6.0}
Source13:       %{pypi_source wheel 0.37.0}
Source14:       %{pypi_source setuptools_scm 6.4.2}
Source15:       %{pypi_source semantic_version 2.8.2}
Source16:       %{pypi_source packaging 21.3}
Source17:       %{pypi_source pyparsing 2.1.0}
Source18:      %{pypi_source tomli 1.2.3}
Source19:      %{pypi_source flit_core 3.7.1}
Source20:      %{pypi_source typing_extensions 3.7.4.3}
Source21:      https://files.pythonhosted.org/packages/source/p/pytz/pytz-2017.2.zip
%endif

BuildRequires: python3-devel
BuildRequires: python3dist(setuptools)
BuildRequires: python3dist(pip)
BuildRequires: python3dist(wheel)
BuildRequires: python3dist(babel)
BuildRequires: dbus-devel
BuildRequires: gettext
BuildRequires: itstool

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

# for rendering our html user guide documentation
# will be addressed with future upgrade of yelp
Requires:      webkit2gtk3
Requires:      mesa-dri-drivers

%if 0%{?rhel}
Requires:      python3-dataclasses
Requires:      python3-importlib-resources
%endif

%global module       fapolicy_analyzer
%global venv_dir     %{_builddir}/vendor-py
%global venv_py3     %{venv_dir}/bin/python3
%global venv_lib     %{venv_dir}/lib/python3.6/site-packages
%global venv_install %{venv_py3} -m pip install --find-links=%{_sourcedir} --no-index --quiet

%description
Tools to assist with the configuration and management of fapolicyd (File Access Policy Daemon).

%prep

%if 0%{?rhel}
# Python- on rhel we are missing setuptools-rust, and to get it requires
# upgrades of pip, setuptools, and wheel along with several other dependencies
# use a virtual environment to isolate changes, %venv_py3 is defined to use this
python3 -m venv %{venv_dir}

# the upgraded packages will not install with the older pip
%{venv_install} %{SOURCE11}

# there exists a circular dependency between setuptools <-> wheel
# by calling setuptools/setup.py before pip'ing we can bypass that
mkdir -p %{_builddir}/setuptools
tar xzf %{SOURCE12} -C %{_builddir}/setuptools --strip-components=1
%{venv_py3} %{_builddir}/setuptools/setup.py -q install
# now pip wheel, and setuptools again
%{venv_install} %{SOURCE13}
%{venv_install} %{SOURCE12}

# now pip install setuptools-rust and direct dependencies
%{venv_install} %{SOURCE10}

# pip install other dependencies
%{venv_install} %{SOURCE20}
%{venv_install} %{SOURCE21}

# babel can be linked from the system install
ln -sf  %{python3_sitelib}/{Babel*,babel} %{venv_lib}

# now that installs are completed we can switch the venv back to the original pip
# switching back will ensure the correct (patched) wheel packaging for use in our rpm
rm -rf %{venv_lib}/pip*
cp -r  %{python3_sitelib}/pip* %{venv_lib}

# Rust- on rhel we vendor everything
%cargo_prep -V1
%else
# Rust- on Fedora we use hybrid crate dependencies, that is mixing official packages and vendored crates
# Problem:  the /usr/share/cargo/registry location is not writable, blocking the install of vendored crates
# Solution: link the contents of the /usr/share/cargo/registry into a writable registry location
#           extract the contents of the vendored crate tarball to the writable registry
CARGO_REG_DIR=%{_builddir}/vendor-rs
mkdir -p ${CARGO_REG_DIR}
for d in %{cargo_registry}/*; do ln -sf ${d} ${CARGO_REG_DIR}; done
tar xzf %{SOURCE1} -C ${CARGO_REG_DIR} --strip-components=2

%cargo_prep

# remap the registry location in the .cargo/config to the writable registry
sed -i "s#%{cargo_registry}#${CARGO_REG_DIR}#g" .cargo/config
%endif

%autosetup -p0 -n %{name}
tar xvzf %{SOURCE2}

# throw out the checked-in lock
# this build will use whatever is available in the writable registry
rm Cargo.lock

# our setup.py looks up the version from git describe
# this overrides that check to the RPM version
echo %{version} > VERSION

%build

%if 0%{?rhel}
# on rhel we want to use the prep'd venv
alias python3=%{venv_py3}
%endif

python3 setup.py compile_catalog -f
python3 help build
python3 setup.py bdist_wheel

%install

%{py3_install_wheel %{module}-%{version}*%{_arch}.whl}
install bin/%{name} %{buildroot}%{_sbindir}/%{name} -D
mkdir -p %{buildroot}/%{_datadir}/help/{C,es}/%{name}/media
install -p -D build/help/C/%{name}/*.html   %{buildroot}/%{_datadir}/help/C/%{name}/
install -p -D build/help/C/%{name}/media/*  %{buildroot}/%{_datadir}/help/C/%{name}/media/
install -p -D build/help/es/%{name}/*.html  %{buildroot}/%{_datadir}/help/es/%{name}/
install -p -D build/help/es/%{name}/media/* %{buildroot}/%{_datadir}/help/es/%{name}/media/

%check

%files -n %{name}
%doc scripts/srpm/README
%license LICENSE
%{python3_sitearch}/%{module}
%{python3_sitearch}/%{module}-%{version}*
%attr(755,root,root) %{_sbindir}/fapolicy-analyzer
%{_datadir}/help/C/fapolicy-analyzer
%{_datadir}/help/es/fapolicy-analyzer

%changelog
* Fri Sep 09 2022 John Wass <jwass3@gmail.com> 0.6.1-1
- New release
