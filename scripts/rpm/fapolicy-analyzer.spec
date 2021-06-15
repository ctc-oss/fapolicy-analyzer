Name:           fapolicy-analyzer
Version:        %{version}
Release:        %{releaseid}%{?dist}
Summary:        GUI configuration for fapolicyd

License:        GPLv3+
URL:            https://github.com/ctc-oss/fapolicy-analyzer
Source0:        %{wheel}
Prefix:         %{_prefix}

BuildArch:      x86_64
BuildRequires:  python3 >= 3.8
Requires:       python3 >= 3.8, gtk3, python3-gobject
Requires:       dbus-libs
AutoReqProv:    no

%description
GUI and CLI tools to assist with the configuration and maintenance of fapolicyd

%install
pip install -v --target %{buildroot}%{python3_sitelib} %{_sourcedir}/%{wheel}
install %{_sourcedir}/fapolicy-analyzer %{buildroot}%{_sbindir}/fapolicy-analyzer -D

%files
%{python3_sitelib}/fapolicy_analyzer*
%{_sbindir}/fapolicy-analyzer

%defattr(-,root,root)
