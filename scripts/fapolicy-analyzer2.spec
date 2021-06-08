%define name fapolicy-analyzer
%define version 0.0.4
%define unmangled_version 0.0.4
%define unmangled_version 0.0.4
%define release 1

Summary: UNKNOWN
Name: %{name}
Version: %{version}
Release: %{release}
Source0: fapolicy-analyzer-master.zip
License: UNKNOWN
Group: Development/Libraries
Prefix: %{_prefix}
Vendor: UNKNOWN <UNKNOWN>

%description
UNKNOWN

%prep
unzip %{_sourcedir}/fapolicy-analyzer-master.zip

%build
cd fapolicy-analyzer-master/python
python setup.py build

%install
cd fapolicy-analyzer-master/python
python setup.py install

%clean

%files
%defattr(-,root,root)
