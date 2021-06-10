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
BuildRequires: python3

%description
UNKNOWN

%prep

%build

%install
pip install -v --root %{buildroot} %{_sourcedir}/fapolicy_analyzer-0.0.4-cp38-cp38-linux_x86_64.whl

%clean

%files
/usr/lib64/python3.8/site-packages/fapolicy_analyzer*
/usr/lib64/python3.8/site-packages/glade
/usr/lib64/python3.8/site-packages/resources

%defattr(-,root,root)
