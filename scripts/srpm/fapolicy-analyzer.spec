%global debug_package %{nil}
%global appname fapolicy-analyzer
%global sum     File Access rule compiler with validation

Name:           %{appname}
Version:        0.6.0
Release:        1%{?dist}
Summary:        %{sum}

License:        GPLv3
URL:            https://github.com/ctc-oss/fapolicy-analyzer
Source0:        %{appname}.tar.gz
Source1:        crates.tar.gz

BuildArch:      x86_64
BuildRequires:  python3-devel
BuildRequires:  python3dist(wheel)
BuildRequires:  python3dist(babel)
BuildRequires:  python3dist(setuptools-rust)
BuildRequires:  gettext

BuildRequires:  rust-packaging
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
# Overridden to rpms due to Fedora version patching
BuildRequires: rust-paste-devel
BuildRequires: rust-indoc-devel

Requires: python%{python3_pkgversion}
Requires: python%{python3_pkgversion}-gobject
Requires: python%{python3_pkgversion}-events
Requires: python%{python3_pkgversion}-configargparse
Requires: python%{python3_pkgversion}-more-itertools
Requires: python%{python3_pkgversion}-rx
Requires: python%{python3_pkgversion}-importlib-resources
Requires: python%{python3_pkgversion}-importlib-metadata
Requires: python%{python3_pkgversion}-dataclasses
Requires: gtk3
Requires: dbus-libs
Requires: gtksourceview3

%description
%{sum}.

%prep
# Problem:  the registry location is not writable, blocking extraction of vendored crates
# Solution: link the contents of the official package registry into a new registry
#           and then extract the vendored crates tarball into the new registry
#           after a little mapping and unmapping of that location while building, Success
CARGO_REG_DIR=%{_sourcedir}/registry
%{__mkdir} -p ${CARGO_REG_DIR}
for d in %{cargo_registry}/*; do ln -sf ${d} ${CARGO_REG_DIR}; done
%{__tar} xzf %{_sourcedir}/crates.tar.gz -C ${CARGO_REG_DIR}

# use the rust2rpm cargo_prep to update our cargo conf
%cargo_prep

# now we need to tweak the registry location to BUILDROOT before building
sed -i "s#%{cargo_registry}#${CARGO_REG_DIR}#g" .cargo/config
# have to undo the tweak in the shared library, otherwise rpm check will balk
sed -i "/\[build\]/a rustflags = [\"--remap-path-prefix\", \"${CARGO_REG_DIR}=%{cargo_registry}\"]" .cargo/config

%autosetup -p0 -n %{appname}

# get rid of the cargo lock, we will use whatever is available in the registry
rm Cargo.lock

# for setuptools, set the version of the library to the rpm version
echo %{version} > VERSION

%generate_buildrequires
%pyproject_buildrequires

# build internationalizations with msgfmt to avoid babel dependency
./scripts/i18n.py

%build
python3 setup.py compile_catalog -f
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files fapolicy_analyzer

%check

%files -n %{appname} -f %{pyproject_files}

%doc README.md

%changelog
