%define name fapolicy-analyzer
%define version 0.0.4
%define unmangled_version 0.0.4
%define unmangled_version 0.0.4
%define release 1

Summary: UNKNOWN
Name: %{name}
Version: %{version}
Release: %{release}
Source0: fapolicy_analyzer-%{unmangled_version}-cp38-cp38-linux_x86_64.whl
License: UNKNOWN
Group: Development/Libraries
Prefix: %{_prefix}
Vendor: UNKNOWN <UNKNOWN>

%description
UNKNOWN

%prep

%build

%install

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
