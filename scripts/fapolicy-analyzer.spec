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
rm -rf %{buildroot}
mkdir -p %{buildroot}%{python3_sitelib}

%build
unzip %{_sourcedir}/fapolicy_analyzer-0.0.4-cp38-cp38-linux_x86_64.whl

%install
install * %{buildroot}%{python3_sitelib}

%clean

%files -f INSTALLED_FILES
%defattr(-,root,root)


fapolicy_analyzer  fapolicy_analyzer-0.0.4.dist-info  glade  resources
[root@65545523ab8b python]# ls /root/rpmbuild/BUILD/glade/
analyzer_selection_dialog.glade       deploy_confirm_dialog.glade  system_trust_database_admin.glade  trust_file_list.glade
ancillary_trust_database_admin.glade  main_window.glade            trust_file_details.glade           unapplied_changes_dialog.glade
