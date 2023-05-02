Summary:       File Access Policy Analyzer
Name:          fapolicy-analyzer
Version:       1.0.2
Release:       1%{?dist}
License:       GPL-3.0-or-later
URL:           https://github.com/ctc-oss/fapolicy-analyzer
Source0:       %{url}/releases/download/v%{version}/%{name}-%{version}.tar.gz

# this tarball contains documentation used to generate help docs
Source1:       %{url}/releases/download/v%{version}/vendor-docs-%{version}.tar.gz

# vendored dependencies for el9
Source2:       %{url}/releases/download/v%{version}/vendor-rs-%{version}.tar.gz

# Build-time python dependencies
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
Source21:      %{pypi_source pytz 2022.7.1}


BuildRequires: python3-devel
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

BuildRequires: rust-packaging

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

ln -sf  %{python3_sitelib}/tomli* %{venv_lib}

# there exists a circular dependency between setuptools <-> wheel,
# by calling setuptools/setup.py before pip'ing we can bypass that
mkdir -p %{_builddir}/setuptools
tar -xzf %{SOURCE12} -C %{_builddir}/setuptools --strip-components=1
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

# An issue with unpacking the vendored crates is that an unprivileged user
# cannot write to the default registry at /usr/share/cargo/registry
# To unblock this, we link the contents of the /usr/share/cargo/registry
# into a new writable registry location, and then extract the contents of the
# vendor tarball to this new writable dir.
# Later the Cargo config will be updated to point to this new registry dir
CARGO_REG_DIR=%{_builddir}/vendor-rs
mkdir -p ${CARGO_REG_DIR}
for d in %{cargo_registry}/*; do ln -sf ${d} ${CARGO_REG_DIR}; done
tar -xzf %{SOURCE2} -C ${CARGO_REG_DIR} --strip-components=2

%cargo_prep

# here the Cargo config is updated to point to the new registry dir
sed -i "s#%{cargo_registry}#${CARGO_REG_DIR}#g" .cargo/config

%autosetup -n %{name}

rm Cargo.lock

# disable dev-tools crate
sed -i '/tools/d' Cargo.toml

# extract our doc sourcs
tar xvzf %{SOURCE1}

# our setup.py looks up the version from git describe
# this overrides that check to use the RPM version
echo %{module_version} > VERSION

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
* Mon Apr 10 2023 John Wass <jwass3@gmail.com> 1.0.2-1
- New release
