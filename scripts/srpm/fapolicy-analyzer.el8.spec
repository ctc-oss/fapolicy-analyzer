Summary:       File Access Policy Analyzer
Name:          fapolicy-analyzer
Version:       1.2.0~rc1
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

BuildRequires: rust-toolset
BuildRequires: python3dist(toml)
BuildRequires: python3dist(typing-extensions)

Requires:      python3
Requires:      python3-gobject
Requires:      python3-events
Requires:      python3-configargparse
Requires:      python3-more-itertools
Requires:      python3-rx
Requires:      python3-importlib-metadata
Requires:      python3-dataclasses
Requires:      python3-importlib-resources
Requires:      python3-toml
Requires:      gtk3
Requires:      dbus-libs
Requires:      gtksourceview3

# runtime required for rendering user guide
Requires:      webkit2gtk3
Requires:      mesa-dri-drivers

# rust-ring-devel does not support s390x and ppc64le:
# https://bugzilla.redhat.com/show_bug.cgi?id=1869980
ExcludeArch:   s390x %{power64}

%global module          fapolicy_analyzer

%global venv_dir        %{_builddir}/vendor-py
%global venv_py3        %{venv_dir}/bin/python3
%global venv_lib        %{venv_dir}/lib/python3.6/site-packages
%global venv_install    %{venv_py3} -m pip install --find-links=%{_sourcedir} --no-index --quiet

%global build_rustflags -Copt-level=3 -Cdebuginfo=2 -Ccodegen-units=1 -Clink-arg=-Wl,-z,relro -Clink-arg=-Wl,-z,now --cap-lints=warn

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

# the upgraded packages will not install with the older pip
%{venv_install} %{SOURCE11}

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

%autosetup -n %{name}
%cargo_prep -V2

tar -xzf %{SOURCE1}

# disable the dev-tools crate
sed -i '/tools/d' Cargo.toml

# setup.py looks up the version from git describe
# this overrides that check to the RPM version
echo %{module_version} > VERSION

# capture build info
scripts/build-info.py --os --time

%build
# ensure standard Rust compiler flags are set
export RUSTFLAGS="%{build_rustflags}"

# use the venv to build
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
* Tue Jul 11 2023 John Wass <jwass3@gmail.com> 1.1.0-1
- New release
