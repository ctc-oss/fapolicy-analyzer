%define release 1

Name:           fapolicy-analyzer
Version:        %{version}
Release:        %{release}
Summary:        GUI configuration for fapolicyd

License:        GPLv3+
URL:            https://github.com/ctc-oss/fapolicy-analyzer
Source0:        fapolicy_analyzer-%{version}-cp38-cp38-linux_x86_64.whl
Prefix:         %{_prefix}

BuildArch:      x86_64
BuildRequires:  python3
Requires:       python3
Requires:       dbus-libs

%description
GUI and CLI tools to assist with the configuration and maintenance of fapolicyd

%install
pip install -v --target %{buildroot}%{python3_sitelib} %{_sourcedir}/fapolicy_analyzer-%{version}-cp38-cp38-linux_x86_64.whl

%files
%{python3_sitelib}/fapolicy_analyzer*
%{python3_sitelib}/glade
%{python3_sitelib}/resources

%defattr(-,root,root)
