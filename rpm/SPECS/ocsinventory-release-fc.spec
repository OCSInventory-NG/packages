Name:           ocsinventory-release
Version:        %{fedora}
Release:        5%{?dist}
Summary:        YUM configuration for OCS Inventory NG repository
Summary(fr):    Configuration de YUM pour le dépôt OCS Inventory NG

Group:          System Environment/Base
License:        GPL
URL:            http://www.ocsinventory-ng.org
Source0:        ocsinventory-fc.repo
Source1:	RPM-GPG-KEY-ocs

BuildRoot:      %{_tmppath}/%{name}-%{version}
BuildArch:	noarch

Requires:       /etc/yum.repos.d
Requires:       fedora-release >= %{fedora}


%description
This package contains yum configuration for the OCS Inventory NG's RPM Repository.
The repository is not enabled after installation.

%description -l fr
Ce paquetage contient le fichier de configuration de YUM pour utiliser
les RPM du dépôt d'OCS Inventory NG.

%prep
%setup -c -T
sed -e "s/VERSION/%{version}/" %{SOURCE0} | tee ocsinventory.repo

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
* Tue May 14 2019 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 28-5, 29-5 and 30-5
- Add version auto configure
- Remove Fedora 25, 26 and 27

* Mon Feb 5 2018 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 25-4, 26-4 and 27-4
- Add Fedora 27
- Remove Fedora 23 and 24

* Tue Aug 8 2017 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 23-3, 24-3, 25-3 and 26-2
- Add Fedora 26

* Sun Jun 11 2017 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 23-2, 24-2 and 25-2
- Correct installation bug

* Tue Jan 31 2017 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 23-1, 24-1 and 25-1
- Initial release
