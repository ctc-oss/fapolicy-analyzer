%define name fapolicy-analyzer
%define version 0.0.4
%define unmangled_version 0.0.4
%define unmangled_version 0.0.4
%define release 1

Summary: UNKNOWN
Name: %{name}
Version: %{version}
Release: %{release}
License: UNKNOWN
Group: Development/Libraries
Prefix: %{_prefix}
Vendor: UNKNOWN <UNKNOWN>
BuildRequires: python3 python3-devel

%description
UNKNOWN

%prep

%build
cp /usr/local/lib/python3.8/site-packages/ %{buildroot}%{python3_sitelib}
cd python
python setup.py build

%install
install * %{buildroot}%{python3_sitelib}

%clean

%files -f INSTALLED_FILES
%defattr(-,root,root)
