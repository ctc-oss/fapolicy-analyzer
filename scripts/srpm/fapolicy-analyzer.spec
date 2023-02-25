Summary:       File Access Policy Analyzer
Name:          fapolicy-analyzer
Version:       0.6.8
Release:       3%{?dist}
License:       GPLv3+
URL:           https://github.com/ctc-oss/fapolicy-analyzer
Source0:       %{url}/releases/download/v%{version}/%{name}.tar.gz

# vendored dependencies for EPEL
Source1:       %{url}/releases/download/v%{version}/vendor-rs.tar.gz

# we need to provide some updates to python on el8
# for compatibility with setuptools-rust
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

BuildRequires: python3-devel
BuildRequires: python3dist(setuptools)
BuildRequires: python3dist(pip)
BuildRequires: python3dist(wheel)
BuildRequires: python3dist(babel)
BuildRequires: dbus-devel
BuildRequires: gettext
BuildRequires: itstool
BuildRequires: desktop-file-utils

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
Requires:      gtk3
Requires:      dbus-libs
Requires:      gtksourceview3
Requires:      python3-dataclasses
Requires:      python3-importlib-resources

%global module       fapolicy_analyzer
%global venv_dir     %{_builddir}/vendor-py
%global venv_py3     %{venv_dir}/bin/python3
%global venv_lib     %{venv_dir}/lib/python3.6/site-packages
%global venv_install %{venv_py3} -m pip install --find-links=%{_sourcedir} --no-index --quiet

%description
Tools to assist with the configuration and management of fapolicyd.

%prep
# Python- on rhel we are missing setuptools-rust, and to get it requires
# upgrades of pip, setuptools, and wheel along with several other dependencies
# use a virtual environment to isolate changes, %venv_py3 is defined to use this
python3 -m venv %{venv_dir}

# the upgraded packages will not install with the older pip
%{venv_install} %{SOURCE3}

# there exists a circular dependency between setuptools <-> wheel
# by calling setuptools/setup.py before pip'ing we can bypass that
mkdir -p %{_builddir}/setuptools
tar xzf %{SOURCE4} -C %{_builddir}/setuptools --strip-components=1
%{venv_py3} %{_builddir}/setuptools/setup.py -q install
# now pip wheel, and setuptools again
%{venv_install} %{SOURCE5}
%{venv_install} %{SOURCE4}

# now pip install setuptools-rust and direct dependencies
%{venv_install} %{SOURCE2}

# pip install other dependencies
%{venv_install} %{SOURCE12}
%{venv_install} %{SOURCE13}

# babel can be linked from the system install
ln -sf  %{python3_sitelib}/{Babel*,babel} %{venv_lib}

# now that installs are completed we can switch the venv back to the original pip
# switching back will ensure the correct (patched) wheel packaging for use in our rpm
rm -rf %{venv_lib}/pip*
cp -r  %{python3_sitelib}/pip* %{venv_lib}

%autosetup -n %{name}
%cargo_prep -V1

tar xvzf %{SOURCE2}

# disable dev-tools crate
sed -i '/tools/d' Cargo.toml

# our setup.py looks up the version from git describe
# this overrides that check to the RPM version
echo %{version} > VERSION

%build
# use the venv to build
%{venv_py3} setup.py compile_catalog -f
%{venv_py3} setup.py bdist_wheel

%install
%{py3_install_wheel %{module}-%{version}*%{_target_cpu}.whl}
install -D bin/%{name} %{buildroot}/%{_sbindir}/%{name}
install -D data/%{name}.8 -t %{buildroot}/%{_mandir}/man8/
desktop-file-install data/%{name}.desktop
find locale -name %{name}.mo -exec cp --parents -rv {} %{buildroot}/%{_datadir} \;
%find_lang %{name}

%check
desktop-file-validate %{buildroot}/%{_datadir}/applications/%{name}.desktop

%files -n %{name} -f %{name}.lang
%doc scripts/srpm/README
%license LICENSE
%{python3_sitearch}/%{module}
%{python3_sitearch}/%{module}-%{version}*
%attr(755,root,root) %{_sbindir}/%{name}
%attr(644,root,root) %{_mandir}/man8/%{name}.8*
%attr(755,root,root) %{_datadir}/applications/%{name}.desktop

%changelog
* Fri Feb 24 2023 John Wass <jwass3@gmail.com> 0.6.8-3
- New release
