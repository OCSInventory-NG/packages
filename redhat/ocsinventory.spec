# spec file for ocsinventory
#
# Copyright (c) 2008-2014 Remi Collet
# Copyright (c) 2016-2021 Philippe Beaumont
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/3.0/
#
# Please, preserve the changelog entries
#
%global useselinux 1

# Remember to change this and Source0 for each release. thanks to launchpad :(
%global tarname OCSNG_UNIX_SERVER

# Use Official release version
%global official_version 2.9.1

Name:        ocsinventory
Summary:     Open Computer and Software Inventory Next Generation

Version:     2.9.1
Release:     1%{?dist}

Group:       Applications/Internet
License:     GPLv2
URL:         http://www.ocsinventory-ng.org/

Source0:     https://github.com/OCSInventory-NG/OCSInventory-ocsreports/releases/download/%{official_version}/%{tarname}-%{official_version}.tar.gz
Source1:     ocsreports.user.ini


BuildArch:   noarch
BuildRoot:   %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: make
BuildRequires: perl-macros
BuildRequires: perl(ExtUtils::MakeMaker)
BuildRequires: perl(Apache::DBI)
BuildRequires: perl(DBD::mysql)
BuildRequires: perl(Net::IP)
BuildRequires: perl(XML::Simple)
BuildRequires: perl(SOAP::Lite)
BuildRequires: perl(Archive::Zip)

# Main package is a dummy package
Requires:    ocsinventory-server  = %{version}-%{release}
Requires:    ocsinventory-reports = %{version}-%{release}
Requires:    mariadb-server


%description
Open Computer and Software Inventory Next Generation is an application
designed to help a network or system administrator keep track of the
computers configuration and software that are installed on the network.

OCS Inventory is also able to detect all active devices on your network,
such as switch, router, network printer and unattended devices.

OCS Inventory NG includes package deployment feature on client computers.

ocsinventory is a meta-package that will install the communication server,
the administration console and the database server (MySQL).

%description -l fr
Open Computer and Software Inventory Next Generation est une application 
destinée à aider l'administrateur système ou réseau à surveiller la
configuration des machines du réseau et les logiciels qui y sont installés.

OCS Inventory est aussi capable de détecter tout périphérique actif sur
le réseau, comme les commutateurs, routeurs, imprimantes et autres matériels
autonomes.

OCS Inventory NG intègre des fonctionnalités de télédiffusion de paquets
sur les machines clients.

ocsinventory est un méta-paquet qui installera le serveur de communication, 
la console d'administration et le serveur de base de données (MySQL).


%package server
Group:    Applications/Internet
Summary:  OCS Inventory NG - Communication server
Requires: mod_perl
Requires: perl(SOAP::Transport::HTTP2)
Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
Requires: perl(Archive::Zip)
Requires: perl(XML::Simple)
# Required by the original setup script, but not detected automatically :
# Apache::DBI drags in DBI
Requires: perl(Apache::DBI)
Requires: perl(Net::IP)
Requires: perl(DBD::mysql)
# Optional, not detected automatically :
Requires: perl(SOAP::Lite)
Requires: perl(XML::Entities)
%if %{useselinux}
Requires(post):   /sbin/restorecon
Requires(post):   /usr/sbin/semanage
Requires(postun): /usr/sbin/semanage
%endif
# Needed for the API
Requires: perl(Mojolicious)
Requires: perl(Plack)
Requires: perl(Switch)

%description server
This package provides the Communication server, which will handle HTTP
communications between database server and agents.

%description -l fr server
Ce paquet fournit le serveur de communication (Communication server), 
qui gère les communications HTTP entre les agents et le serveur de base
de données.


%package reports
Group:    Applications/Internet
Summary:  OCS Inventory NG - Communication server
# From phpci : curl, date, dom, ldap, mysql, openssl, pcre, session, xml, zlib
Requires: php >= 7.2
Requires: php-mysqli php-gd php-xml php-ldap php-mbstring php-soap
Requires: php-pear-CAS php-phpmailer6
# Required by the original setup script, but not detected automatically :
Requires: perl(DBD::mysql)
# Required by ipdiscover-util.pl (nmap and nmblookup)
Requires: nmap
# nmblookup is provided by samba or samba3x (EL-5)
Requires: %{_bindir}/nmblookup
# phpmailer dependancies
Requires: php-ctype php-filter php-hash php-intl php-openssl php-pcre
# Remi repo is needed
%if 0%{?rhel} >= 7
Requires: remi-release epel-release
%endif
%if %{useselinux}
Requires(post):   /sbin/restorecon
Requires(post):   /usr/sbin/semanage
Requires(postun): /usr/sbin/semanage
%endif

%description reports
This package provides the Administration console, which will allow 
administrators to query the database server through their favorite browser.

%description -l fr reports
Ce paquet fournit la console d'administration (Administration console), 
qui autorise les administrateurs à interroger la base de données via leur
navigateur favori.


%prep
%setup -q -n %{tarname}-%{official_version}

chmod -x binutils/ocs-errors

# remvoe Bundled libs
rm -rf ocsreports/backend/require/lib


%build
cd Apache
%{__perl} Makefile.PL INSTALLDIRS=vendor
make %{?_smp_mflags}


%install
rm -rf %{buildroot}

# --- ocsinventory-server --- communication server
mkdir -p %{buildroot}%{perl_vendorlib}
cp -ar  Api %{buildroot}%{perl_vendorlib}
mkdir -p %{buildroot}%{_sysconfdir}/httpd/conf.d
sed -e "s;REST_API_PATH;%{perl_vendorlib};g" \
    -e "s;REST_API_LOADER_PATH;%{perl_vendorlib}/Api/Ocsinventory/Restapi/Loader.pm;g" \
     etc/ocsinventory/ocsinventory-restapi.conf \
     >%{buildroot}%{_sysconfdir}/httpd/conf.d/ocsinventory-restapi.conf

cd Apache
make pure_install PERL_INSTALL_ROOT=%{buildroot}
find %{buildroot} -type f -name .packlist -exec rm -f {} ';'
find %{buildroot} -type d -depth -exec rmdir {} 2>/dev/null ';'

chmod -R u+rwX,go+rX,go-w %{buildroot}/*
find %{buildroot}%{perl_vendorlib}/Apache -name \*.pm -exec chmod -x {} \;

# To avoid bad dependency on perl(mod_perl) : RHEL >= 5 && Fedora >= 4
rm -f %{buildroot}%{perl_vendorlib}/Apache/Ocsinventory/Server/Modperl1.pm

cd ..

mkdir -p %{buildroot}%{_localstatedir}/log/ocsinventory-server

mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
sed -e 's;PATH_TO_LOG_DIRECTORY;%{_localstatedir}/log/ocsinventory-server;' \
   ./etc/logrotate.d/ocsinventory-server >%{buildroot}%{_sysconfdir}/logrotate.d/ocsinventory-server

# default configuration (localhost) should work on "simple" installation
mkdir -p %{buildroot}%{_sysconfdir}/httpd/conf.d
sed -e "s;DATABASE_SERVER;localhost;g" \
    -e "s;DATABASE_PORT;3306;g" \
    -e "s;VERSION_MP;2;g" \
    -e "s;PATH_TO_LOG_DIRECTORY;%{_localstatedir}/log/ocsinventory-server;g" \
    -e "s;APACHE_AUTH_USER_FILE;%{_sysconfdir}/ocsinventory/ocsinventory-server/htpasswd;g" \
    -e "s;PATH_TO_PLUGINS_CONFIG_DIRECTORY;%{_sysconfdir}/ocsinventory/ocsinventory-server/plugins;" \
    -e "s;PATH_TO_PLUGINS_PERL_DIRECTORY;%{_sysconfdir}/ocsinventory/ocsinventory-server/perl;" \
    etc/ocsinventory/ocsinventory-server.conf \
    >%{buildroot}%{_sysconfdir}/httpd/conf.d/ocsinventory-server.conf

mkdir -p %{buildroot}%{_sysconfdir}/ocsinventory/ocsinventory-server/{plugins,perl}
touch    %{buildroot}%{_sysconfdir}/ocsinventory/ocsinventory-server/htpasswd

# --- ocsinventory-reports --- administration console

mkdir -p %{buildroot}%{_datadir}/ocsinventory-reports
cp -ar ocsreports %{buildroot}%{_datadir}/ocsinventory-reports
find %{buildroot}%{_datadir}/ocsinventory-reports \
     -type f -exec chmod -x {} \;

mkdir -p %{buildroot}%{_sysconfdir}/ocsinventory/ocsinventory-reports

sed -e '/CONF_MYSQL_DIR/s;ETC_DIR;"%{_sysconfdir}/ocsinventory/ocsinventory-reports";' \
    -e "/CONFIG_DIR/s;__DIR__ . ';'/var/lib/ocsinventory-reports;" \
    -e "/PLUGINS_DIR/s;__DIR__ . ';'%{buildroot}%{_datadir}/ocsinventory-reports/ocsreports/;" \
    -e "/EXT_DL_DIR/s;__DIR__ . ';'/var/lib/ocsinventory-reports;" \
    -i %{buildroot}%{_datadir}/ocsinventory-reports/ocsreports/var.php

mkdir -p %{buildroot}%{_localstatedir}/lib/ocsinventory-reports/{download,ipd,snmp,logs}
mkdir -p %{buildroot}%{_bindir}

mv %{buildroot}%{_datadir}/ocsinventory-reports/ocsreports/config %{buildroot}%{_localstatedir}/lib/ocsinventory-reports/config

mv %{buildroot}%{_datadir}/ocsinventory-reports/ocsreports/extensions %{buildroot}%{_localstatedir}/lib/ocsinventory-reports/extensions

install -pm 755 binutils/ipdiscover-util.pl       %{buildroot}%{_datadir}/ocsinventory-reports/ocsreports/ipdiscover-util.pl
install -pm 755 binutils/ocsinventory-injector.pl %{buildroot}%{_bindir}/ocsinventory-injector
install -pm 755 binutils/ocsinventory-log.pl      %{buildroot}%{_bindir}/ocsinventory-log

echo '
# Patch from RPM : allow apache to serv plugins directory
<Directory /var/lib/ocsinventory-reports/plugins>
   <IfModule mod_authz_core.c>
     # Apache 2.4
     Require all granted
   </IfModule>
   <IfModule !mod_authz_core.c>
     Order deny,allow
     Allow from all
   </IfModule>
</Directory>
Alias /plugins /var/lib/ocsinventory-reports/plugins' >> etc/ocsinventory/ocsinventory-reports.conf 

mkdir -p %{buildroot}%{_sysconfdir}/httpd/conf.d
sed -e "s;OCSREPORTS_ALIAS;/ocsreports;g" \
    -e "s;PATH_TO_OCSREPORTS_DIR;%{_datadir}/ocsinventory-reports/ocsreports;g" \
    -e "s;PACKAGES_ALIAS;/download;g" \
    -e "s;PATH_TO_PACKAGES_DIR;%{_localstatedir}/lib/ocsinventory-reports/download;g" \
    -e "s;PATH_TO_SNMP_DIR;%{_localstatedir}/lib/ocsinventory-reports/snmp;g" \
    -e "s;SNMP_ALIAS;/snmp;g" \
    etc/ocsinventory/ocsinventory-reports.conf \
    >%{buildroot}%{_sysconfdir}/httpd/conf.d/ocsinventory-reports.conf

mv %{SOURCE1} %{buildroot}%{_datadir}/ocsinventory-reports/.user.ini

%clean
rm -rf %{buildroot}


%post server
%if %{useselinux}
(
# New File context
semanage fcontext -a -s system_u -t httpd_log_t -r s0 "%{_localstatedir}/log/ocsinventory-server(/.*)?" 
# files created by app
restorecon -R %{_localstatedir}/log/ocsinventory-server
) &>/dev/null ||:
%endif
/sbin/service httpd condrestart > /dev/null 2>&1 || :


%post reports
%if %{useselinux}
(
# New File context
semanage fcontext -a -s system_u -t httpd_sys_rw_content_t -r s0 "%{_sysconfdir}/ocsinventory/ocsinventory-reports(/.*)?"
semanage fcontext -a -s system_u -t httpd_sys_rw_content_t -r s0 "%{_localstatedir}/lib/ocsinventory-reports(/.*)?"
# files created by app
restorecon -R %{_sysconfdir}/ocsinventory/ocsinventory-reports
restorecon -R %{_localstatedir}/lib/ocsinventory-reports
# Move plugins folder on the right folder
mv %{buildroot}%{_localstatedir}/lib/ocsinventory-reports/plugins %{buildroot}%{_datadir}/ocsinventory-reports/ocsreports/plugins
# Remove useless conf file
rm %{buildroot}%{_sysconfdir}/httpd/conf.d/ocsinventory-lang-reports.conf
) &>/dev/null ||:
%endif


%postun server
if [ "$1" -eq "0" ]; then
%if %{useselinux}
    # Remove the File Context
    semanage fcontext -d "%{_localstatedir}/log/ocsinventory-server(/.*)?" &>/dev/null || :
%endif
    /sbin/service httpd condrestart > /dev/null 2>&1 || :
fi


%postun reports
%if %{useselinux}
if [ "$1" -eq "0" ]; then
    # Remove the File Context
    semanage fcontext -d "%{_sysconfdir}/ocsinventory/ocsinventory-reports(/.*)?" &>/dev/null ||:
    semanage fcontext -d "%{_localstatedir}/lib/ocsinventory-reports(/.*)?" &>/dev/null ||:
fi
%endif


%files
%defattr(-, root, root, -)


%files server
%defattr(-, root, root, -)
%doc LICENSE README.md Apache/Changes
%doc binutils/*.README
%doc binutils/{ocs-errors,soap-client.pl}
%dir %{_sysconfdir}/ocsinventory/ocsinventory-server
%dir %{_sysconfdir}/ocsinventory/ocsinventory-server/plugins
%dir %{_sysconfdir}/ocsinventory/ocsinventory-server/perl
%config(noreplace) %{_sysconfdir}/ocsinventory/ocsinventory-server/htpasswd
%config(noreplace) %{_sysconfdir}/logrotate.d/ocsinventory-server
%config(noreplace) %{_sysconfdir}/httpd/conf.d/ocsinventory-server.conf
%config(noreplace) %{_sysconfdir}/httpd/conf.d/ocsinventory-restapi.conf
%attr(755,apache,root) %{_localstatedir}/log/ocsinventory-server
%{_bindir}/ocsinventory-injector
%{_bindir}/ocsinventory-log
%{perl_vendorlib}/Apache
%{perl_vendorlib}/Api

%files reports
%defattr(-, root, root, -)
%doc LICENSE README.md
%dir %{_sysconfdir}/ocsinventory
%attr(750,apache,root) %dir %{_sysconfdir}/ocsinventory/ocsinventory-reports
%attr(640,apache,root) %config(noreplace)
%config(noreplace) %{_sysconfdir}/httpd/conf.d/ocsinventory-reports.conf
%config(noreplace) %{_sysconfdir}/httpd/conf.d/ocsinventory-lang-reports.conf
%{_datadir}/ocsinventory-reports
%attr(755,root,root)%{_datadir}/ocsinventory-reports/ocsreports/tools/cron_mailer.php
%attr(755,apache,root) %dir %{_localstatedir}/lib/ocsinventory-reports
%attr(755,apache,root) %dir %{_localstatedir}/lib/ocsinventory-reports/ipd
%attr(755,apache,root) %dir %{_localstatedir}/lib/ocsinventory-reports/download
%attr(755,apache,root) %dir %{_localstatedir}/lib/ocsinventory-reports/snmp
%attr(755,apache,root) %dir %{_localstatedir}/lib/ocsinventory-reports/logs
%attr(755,apache,root) %{_localstatedir}/lib/ocsinventory-reports/config
%attr(755,apache,root) %{_localstatedir}/lib/ocsinventory-reports/extensions

%changelog
* Mon Aug 30 2021 Charlene Auger <charlene.auger@ocsinventory-ng.org> - 2.9.1-1
- Update to 2.9.1
- Fix wrong plugins folder path

* Wed Jun 16 2021 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.9.0-3
- Add patch to correct hardlink in crontab

* Mon May 31 2021 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.9.0-2
- remove php-imap from dependancies
- push minimal needed php version to 7.2

* Thu May 27 2021 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.9.0-1
- Update to 2.9.0

* Fri Apr 02 2021 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.8.1-1
- Update to 2.8.1

* Fri Sep 25 2020 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.8.0-1
- Update to 2.8.0

* Sun Mar 29 2020 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.7.0-1
- Update to 2.7.0

* Mon May 13 2019 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.6.0-2
- Remove external libs and put it in dependancies
- Use Remi repo for external libs
- Upgrade php needed version
- Add patch for mail cron

* Tue May 07 2019 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.6.0-1
- Update to 2.6.0

* Wed Apr 11 2018 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.4.1-1
- Update to 2.4.1
- Enable Rest Api on EL

* Sat Dec 30 2017 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.4.0-2
- Add user.ini to allow use php-fpm

* Tue Dec 19 2017 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.4.0-1
- Update to 2.4
- Add Rest Api on Fedora

* Wed Sep 20 2017 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.3.1-8
- Correct depence issue

* Mon Aug 07 2017 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.3.1-7
- Correct issue #275 : Hard link on profiles

* Mon Jun 19 2017 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.3.1-6
- Syntax correction

* Sat Jun 17 2017 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.3.1-5
- Correct plugins access

* Fri Apr 21 2017 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.3.1-4
- Remove hardcoded link
- Add SNMP support in ocsreports configuration
- Add ocsinventory-lang-reports.conf

* Tue Apr 04 2017 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.3.1-3
- Clean header.php

* Tue Mar 21 2017 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.3.1-2
- Remove hardcoded link

* Thu Mar 16 2017 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.3.1-1
- Update to 2.3.1
- Remove ugly link

* Mon Feb 06 2017 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.3.0-2
- Migrate php-mysql to php-mysqli

* Thu Jan 12 2017 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.3.0-1
- update to 2.3.0
- remove dbconfig.php
- remove patch for apache 2.4 (not needed anymore)
- move plugins directory outside of ocsreports
- add perl(Archive::Zip) in RequireBuild
- rename LICENSE.txt into LICENSE

* Mon Aug 18 2014 Remi Collet <remi@fedoraproject.org> - 2.1.2-3
- fix SELinux context
  use httpd_sys_rw_content_t instead of httpd_sys_script_rw_t
- requires mariadb-server to avoid pulling mysql-galera (EL-7)

* Tue Jul 15 2014 Remi Collet <remi@fedoraproject.org> - 2.1.2-2
- refresh sources

* Wed Jul 09 2014 Remi Collet <remi@fedoraproject.org> - 2.1.2-1
- update to 2.1.2

* Wed Jul 09 2014 Remi Collet <remi@fedoraproject.org> - 2.1.1-3
- XSS security fix for CVE-2014-4722

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu May 22 2014 Remi Collet <remi@fedoraproject.org> - 2.1.1-1
- update to 2.1.1

* Mon Feb 17 2014 Remi Collet <remi@fedoraproject.org> - 2.1-2
- Requires: mysql-compat-server in EPEL-7

* Thu Feb 13 2014 Remi Collet <remi@fedoraproject.org> - 2.1-1
- update to 2.0.5
- drop external-agents.conf (not supported)
- add /etc/ocsinventory/ocsinventory-server/plugins and perl folder

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.5-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Jul 25 2013 Petr Pisar <ppisar@redhat.com> - 2.0.5-6
- Perl 5.18 rebuild

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.5-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.5-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sun Jun 17 2012 Petr Pisar <ppisar@redhat.com> - 2.0.5-3
- Perl 5.16 rebuild

* Wed Apr 18 2012 Remi Collet <remi@fedoraproject.org> - 2.0.5-2
- fix config for httpd 2.4

* Thu Apr 05 2012 Remi Collet <remi@fedoraproject.org> - 2.0.5-1
- update to 2.0.5 (security fixes)
- add missing /var/lib/ocsinventory-reports/logs
- fix config for httpd 2.4
- clean EL-4 stuff

* Sat Feb 25 2012 Remi Collet <remi@fedoraproject.org> - 2.0.4-2
- unbundled phpcas

* Mon Feb 13 2012 Remi Collet <remi@fedoraproject.org> - 2.0.4-1
- update to 2.0.4

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.3-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Oct 25 2011 Remi Collet <Fedora@famillecollet.com> - 1.3.3-5
- fix XSS vulnerabity (Bug #748072, CVE-2011-4024)

* Tue Jul 19 2011 Petr Sabata <contyk@redhat.com> - 1.3.3-4
- Perl mass rebuild

* Sat Apr 09 2011 Xavier Bachelot <xavier@bachelot.org> 1.3.3-3
- Don't require php-zip for F16 and up.

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Nov 24 2010 Remi Collet <Fedora@famillecollet.com> - 1.3.3-1
- update to 1.3.3 (bugfix)
- clean applied patches
- requires nbmlookup instead of samba-client, fix #654252

* Sat Jun 19 2010 Remi Collet <Fedora@famillecollet.com> - 1.3.2-4
- upstream patch to set XML default parser
  (workaround XML::SAX issue on EL5, see #641735)

* Sat Jun 19 2010 Remi Collet <Fedora@famillecollet.com> - 1.3.2-3
- upstream patches

* Tue Jun 01 2010 Marcela Maslanova <mmaslano@redhat.com> - 1.3.2-2
- Mass rebuild with perl-5.12.0

* Thu May 13 2010 Remi Collet <Fedora@famillecollet.com> 1.3.2-1
- update to new version
- remove schema patch (upstream)
- remove shorttag option

* Thu Feb 18 2010 Remi Collet <Fedora@famillecollet.com> 1.3.1-1
- update to new version
- improved patch for schema

* Sun Feb 07 2010 Remi Collet <Fedora@famillecollet.com> 1.3-1
- update to new version
- add a patch to improve schema check (when install / upgrade needed)

* Fri Feb 05 2010 Remi Collet <Fedora@famillecollet.com> 1.02.3-1
- Security Fixes - Bug #560737

* Mon Aug 17 2009 Remi Collet <Fedora@famillecollet.com> 1.02.1-3
- add ChangeLog
- Security Fixes (internal version 5003) Bug #517837

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.02.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sat May 30 2009 Remi Collet <Fedora@famillecollet.com> 1.02.1-1
- update to OCS Inventory NG 1.02.1 - Security Fixes (internal version 5003)

* Mon Apr 20 2009 Remi Collet <Fedora@famillecollet.com> 1.02-1
- update to OCS Inventory NG 1.02 final release (internal version 5003)

* Sun Jan 18 2009 Remi Collet <Fedora@famillecollet.com> 1.02-0.10.rc3.el4.1
- fix php-xml > php-domxml in EL-4

* Sun Jan 11 2009 Remi Collet <Fedora@famillecollet.com> 1.02-0.10.rc3
- add r1447 and r1462 patch
- change log selinux context (httpd_log_t)

* Fri Oct 17 2008 Remi Collet <Fedora@famillecollet.com> 1.02-0.9.rc3
- upstream r1423 patch - migration script

* Sat Oct 11 2008 Remi Collet <Fedora@famillecollet.com> 1.02-0.8.rc3
- upstream r1413 patch - database schema

* Sat Oct 11 2008 Remi Collet <Fedora@famillecollet.com> 1.02-0.7.rc3
- update to RC3

* Tue Jul 22 2008 Remi Collet <Fedora@famillecollet.com> 1.02-0.6.rc2
- add missing requires perl(SOAP::Transport::HTTP2) (with mod_perl2)
- AddDefaultCharset ISO-8859-1 in httpd config
- fix SElinux path

* Sat Jun 14 2008 Remi Collet <Fedora@famillecollet.com> 1.02-0.5.rc2
- change dir from /var/lib/ocsinventory-server to /var/lib/ocsinventory-reports
- add Requires nmap and samba-client (nmblookup)

* Sun May 18 2008 Remi Collet <Fedora@famillecollet.com> 1.02-0.4.rc2
- remove <IfModule> from ocsinventory-server.conf
- change perm to 755 on /var/lib/ocsinventory-server
- metapackage description closer to upstream components name
- add BR perl(DBD::mysql) to avoid build warning

* Fri May 16 2008 Xavier Bachelot <xavier@bachelot.org> 1.02-0.3.rc2.1
- Fix BuildRequires and Requires.
- Fix %%description french translations and a few typos.
- Rename apache confs.

* Sat May 10 2008 Remi Collet <Fedora@famillecollet.com> 1.02-0.3.rc2
- add missing requires for php extensions (from PHP_Compat result)
- add selinux stuff

* Thu May 08 2008 Remi Collet <Fedora@famillecollet.com> 1.02-0.2.rc2
- update to RC2

* Sat Mar 15 2008 Remi Collet <Fedora@famillecollet.com> 1.02-0.2.rc1
- fix download dir

* Sat Mar  8 2008 Remi Collet <Fedora@famillecollet.com> 1.02-0.1.rc1
- Initial RPM

