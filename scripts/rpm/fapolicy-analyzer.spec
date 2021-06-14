Name:           fapolicy-analyzer
Version:        %{version}
Release:        %{release}
Summary:        GUI configuration for fapolicyd

License:        GPLv3+
URL:            https://github.com/ctc-oss/fapolicy-analyzer
Source0:        fapolicy_analyzer-%{version}-cp38-cp38-linux_x86_64.whl
Prefix:         %{_prefix}

BuildArch:      x86_64
BuildRequires:  python3.8
Requires:       python3.8
Requires:       dbus-libs
AutoReqProv:    no

%description
GUI and CLI tools to assist with the configuration and maintenance of fapolicyd

%install
pip install -v --target %{buildroot}%{python3_sitelib} %{_sourcedir}/fapolicy_analyzer-%{version}-cp38-cp38-linux_x86_64.whl

%files
%{python3_sitelib}/fapolicy_analyzer*

%defattr(-,root,root)
