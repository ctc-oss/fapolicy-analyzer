Summary:       File Access Policy Analyzer
Name:          fapolicy-analyzer
Version:       1.0.0
Release:       1%{?dist}
License:       GPLv3+
URL:           https://github.com/ctc-oss/fapolicy-analyzer
Source0:       %{url}/releases/download/v%{version}/fapolicy-analyzer.tar.gz

# this tarball contains bundled crates not available in Fedora
# reference: https://bugzilla.redhat.com/show_bug.cgi?id=2124697#c5
Source1:       %{url}/releases/download/v%{version}/vendor-rs.tar.gz

# this tarball contains documentation used to generate help docs
Source2:       %{url}/releases/download/v%{version}/vendor-docs.tar.gz

# we need to provide some updates to python on el8
%if 0%{?rhel}
Source10:      %{pypi_source setuptools-rust 1.1.2}
Source11:      %{pypi_source pip 21.3.1}
Source12:      %{pypi_source setuptools 59.6.0}
Source13:      %{pypi_source wheel 0.37.0}
Source14:      %{pypi_source setuptools_scm 6.4.2}
Source15:      %{pypi_source semantic_version 2.8.2}
Source16:      %{pypi_source packaging 21.3}
Source17:      %{pypi_source pyparsing 2.1.0}
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
BuildRequires: desktop-file-utils

%if 0%{?rhel}
BuildRequires: rust-toolset
BuildRequires: python3dist(toml)
BuildRequires: python3dist(typing-extensions)
BuildRequires: git
%else
BuildRequires: rust-packaging
BuildRequires: python3dist(setuptools-rust)

# crates available for rawhide
BuildRequires: rust-arrayvec0.5-devel
BuildRequires: rust-autocfg-devel
BuildRequires: rust-bitflags-devel
BuildRequires: rust-bitvec-devel
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
BuildRequires: rust-dirs-sys-devel
BuildRequires: rust-either-devel
BuildRequires: rust-fastrand-devel
BuildRequires: rust-funty-devel
BuildRequires: rust-getrandom-devel
BuildRequires: rust-iana-time-zone-devel
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
BuildRequires: rust-syn-devel
BuildRequires: rust-tap-devel
BuildRequires: rust-tempfile-devel
BuildRequires: rust-thiserror-devel
BuildRequires: rust-thiserror-impl-devel
BuildRequires: rust-time0.1-devel
BuildRequires: rust-toml-devel
BuildRequires: rust-unicode-xid-devel
BuildRequires: rust-unindent-devel
BuildRequires: rust-untrusted-devel
BuildRequires: rust-version_check-devel
BuildRequires: rust-wyz-devel
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

# runtime required for rendering user guide
Requires:      webkit2gtk3
Requires:      mesa-dri-drivers

%if 0%{?rhel}
Requires:      python3-dataclasses
Requires:      python3-importlib-resources
%endif

%global module          fapolicy_analyzer
%global venv_dir        %{_builddir}/vendor-py
%global venv_py3        %{venv_dir}/bin/python3
%global venv_lib        %{venv_dir}/lib/python3.6/site-packages
%global venv_install    %{venv_py3} -m pip install --find-links=%{_sourcedir} --no-index --quiet
# pep440 versions handle dev and rc differently, so we call them out explicitly here
%global module_version  %{lua: v = string.gsub(rpm.expand("%{?version}"), "~dev", ".dev"); \
                               v = string.gsub(v, "~rc",  "rc"); print(v) }

%description
Tools to assist with the configuration and management of fapolicyd.

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

# disable dev-tools crate
sed -i '/tools/d' Cargo.toml

# our setup.py looks up the version from git describe
# this overrides that check to the RPM version
echo %{module_version} > VERSION

%build
%if 0%{?rhel}
# on rhel we want to use the prep'd venv
alias python3=%{venv_py3}
%endif

python3 setup.py compile_catalog -f
python3 help build
python3 setup.py bdist_wheel

%install
%{py3_install_wheel %{module}-%{module_version}*%{_arch}.whl}
%{python3} help install --dest %{buildroot}/%{_datadir}/help
install bin/%{name} %{buildroot}/%{_sbindir}/%{name} -D
install data/fapolicy-analyzer.8 %{buildroot}/%{_mandir}/man8/* -D
desktop-file-install data/fapolicy-analyzer.desktop
%find_lang %{name} --with-gnome

%post
update-desktop-database

%check

%files -n %{name} -f %{name}.lang
%doc scripts/srpm/README
%license LICENSE
%{python3_sitearch}/%{module}
%{python3_sitearch}/%{module}-%{module_version}*
%attr(755,root,root) %{_sbindir}/fapolicy-analyzer
%attr(755,root,root) %{_datadir}/applications/%{name}.desktop
%attr(644,root,root) %{_mandir}/man8/*

%changelog
* Fri Dec 16 2022 John Wass <jwass3@gmail.com> 1.0.0-1
- New release
