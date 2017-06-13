%global rhel 6

Name:           ocsinventory-release
%if %{rhel} == 7
Version:        7
Release:        4%{?dist}
%endif
%if %{rhel} == 6
Version:        6
Release:        4%{?dist}
%endif
Summary:        YUM configuration for OCS Inventory NG repository
Summary(fr):    Configuration de YUM pour le dépôt OCS Inventory NG

Group:          System Environment/Base
License:        GPL
URL:            http://www.ocsinventory-ng.org
Source0:        ocsinventory-el.repo
Source1:	RPM-GPG-KEY-ocs

BuildRoot:      %{_tmppath}/%{name}-%{version}
BuildArchitectures: noarch

Requires:       yum
# Sadly system-release and redhat-release are not versionned
Requires:       redhat-release
Requires:       epel-release   = %{rhel}
# Ensure not installable on Fedora
Conflicts:      fedora-release


%description
This package contains yum configuration for the OCS Inventory NG's RPM Repository.
The repository is not enabled after installation.

%description -l fr
Ce paquetage contient le fichier de configuration de YUM pour utiliser
les RPM du dépôt d'OCS Inventory NG.

%prep
%setup -c -T
sed -e "s/VERSION/%{rhel}/" %{SOURCE0} | tee ocsinventory.repo

%build
echo empty build

%install
rm -rf %{buildroot}
install -Dp -m 644 ocsinventory.repo %{buildroot}%{_sysconfdir}/yum.repos.d/ocsinventory.repo
install -Dp -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/pki/rpm-gpg/RPM-GPG-KEY-ocs

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/yum.repos.d/ocsinventory.repo
%{_sysconfdir}/pki/rpm-gpg/RPM-GPG-KEY-ocs

%changelog
* Mon Jan 23 2017 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 6-4 and 7-4
- Correction on repo definition

* Fri Jan 20 2017 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 6-3 and 7-3
- Correct in source include

* Thu Jan 19 2017 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 6-2 and 7-2
- Add GPG key

* Sat Jan 14 2017 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 6-1 and 7-1
- Initial release
