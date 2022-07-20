# spec file for ocsinventory-agent
#
# Copyright (c) 2007-2014 Remi Collet
# Copyright (c) 2016-2017 Philippe Beaumont
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/3.0/
#
# Please, preserve the changelog entries
#

# Can, optionaly, be define at build time (see README.RPM)
# - ocstag    : administrative tag
# - ocsserver : OCS Inventory NG communication serveur

# Avoid empty debuginfo package, arched only for dep
%global debug_package %{nil}

# Official release version
%global official_version 2.9.3

Name:      ocsinventory-agent
Summary:   Open Computer and Software Inventory Next Generation client

Version:   2.9.3
Release:   2%{?dist}%{?ocstag:.%{ocstag}}

Source0:   https://github.com/OCSInventory-NG/UnixAgent/releases/download/%{official_version}/Ocsinventory-Unix-Agent-%{official_version}.tar.gz

Source1:   %{name}.logrotate
Source2:   %{name}.cron

Source11:   %{name}.README
Source12:   %{name}.README.fr

Group:     Applications/System
License:   GPLv2+
URL:       http://www.ocsinventory-ng.org/

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: perl(Module::Install)
BuildRequires: perl(XML::Simple)
BuildRequires: perl(LWP)
BuildRequires: perl(Net::IP)
BuildRequires: perl(Digest::MD5)
BuildRequires: perl(File::Temp)

Requires: perl(XML::Simple)
Requires: perl(LWP)
Requires: perl(Net::IP)
Requires: perl(Digest::MD5)
Requires: perl(File::Temp)
Requires: perl-Ocsinventory-Agent = %{version}-%{release}
Requires: crontabs
Requires: perl(LWP::Protocol)
Requires: perl(LWP::Protocol::http)
Requires: perl(LWP::Protocol::https)
Requires: perl(Proc::Daemon)

Recommends:Requires: perl(Net::SNMP)
Suggests: perl(Parse::EDID)
Suggests: nmap
Suggests: smartmontools

Obsoletes: ocsinventory-client < %{version}
Obsoletes: ocsinventory-agent-core < %{version}
Provides:  ocsinventory-client = %{version}-%{release}
Obsoletes: ocsinventory-agent-core = %{version}-%{release}

%description
Open Computer and Software Inventory Next Generation is an application
designed to help a network or system administrator keep track of computer
configuration and software installed on the network.

It also allows deploying software, commands or files on Windows and
Linux client computers.

%{name} provides the client for Linux (Unified Unix Agent).


%description -l fr
Open Computer and Software Inventory Next Generation est une application
destinée à aider l'administrateur système ou réseau à garder un oeil sur
la configuration des machines du réseau et sur les logiciels qui y sont
installés.

Elle autorise aussi la télédiffusion (ou déploiement) de logiciels,
de commandes ou de fichiers sur les clients Windows ou Linux.

%{name} fournit le client pour Linux (Agent Unix Unifié)


%package -n perl-Ocsinventory-Agent
Summary:   Libraries %{name}
Group:     Development/Libraries
BuildArch: noarch
Requires:  perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
Requires:  perl(HTTP::Request)
Requires:  perl(Net::IP)
Requires:  perl(Net::Netmask)
Requires:  perl(Net::SSLeay)
Requires:  perl(Data::UUID)
Requires:  net-tools
Requires:  pciutils
Requires:  which
%ifarch %{ix86} x86_64 ia64
Requires: dmidecode
%endif
Requires:  %{_sysconfdir}/logrotate.d
Conflicts: %{name} < %{version}

%description  -n perl-Ocsinventory-Agent
Perl libraries for %{name}

%{?perl_default_filter}

%prep
%setup -q -n Ocsinventory-Unix-Agent-%{version}
%autopatch -p1

sed -e 's/\r//' -i snmp/mibs/local/6876.xml

cat <<EOF >%{name}.conf
#
# OCS Inventory "Unix Unified Agent" Configuration File
# used by hourly cron job
#

# Add tools directory if needed (tw_cli, hpacucli, ipssend, ...)
PATH=/sbin:/bin:/usr/sbin:/usr/bin

%if 0%{?ocsserver:1}
# Mode, change to "none" to disable
OCSMODE[0]=cron

# used to override the %{name}.cfg setup.
OCSSERVER[0]=%{ocsserver}
%else
# Mode, change to "cron" to activate
OCSMODE[0]=none

# can be used to override the %{name}.cfg setup.
# OCSSERVER[0]=your.ocsserver.name
#
# corresponds with --local=%{_localstatedir}/lib/%{name}
# OCSSERVER[0]=local
%endif

# Wait before inventory
OCSPAUSE[0]=100

# Administrative TAG (optional, must be filed before first inventory)
OCSTAG[0]=%{?ocstag}
EOF

cat <<EOF >%{name}.cfg
#
# OCS Inventory "Unix Unified Agent" Configuration File
#
# options used by cron job overides this (see /etc/sysconfig/%{name})
#

# Server URL, unconmment if needed
# server = your.ocsserver.name
local = %{_localstatedir}/lib/%{name}

# Administrative TAG (optional, must be filed before first inventory)
# tag = your_tag

# How to log, can be File,Stderr,Syslog
logger = Stderr
logfile = %{_localstatedir}/log/%{name}/%{name}.log
EOF

cp %{SOURCE11} README.RPM
cp %{SOURCE12} README.RPM.fr


%build
%{__perl} Makefile.PL INSTALLDIRS=vendor
make %{?_smp_mflags}


%install
rm -rf %{buildroot}

make pure_install PERL_INSTALL_ROOT=%{buildroot}
find %{buildroot} -type f -name .packlist -exec rm -f {} ';'
find %{buildroot} -type d -depth -exec rmdir {} 2>/dev/null ';'

chmod -R u+rwX,go+rX,go-w %{buildroot}/*

# Move exe to root directory
mv %{buildroot}%{_bindir} %{buildroot}%{_sbindir}

mkdir -p %{buildroot}%{_localstatedir}/{log,lib}/%{name}
mkdir -p %{buildroot}%{_sysconfdir}/{logrotate.d,sysconfig,cron.hourly,ocsinventory/softwares}

mkdir %{buildroot}%{_localstatedir}/lib/%{name}/download
cp -pr snmp %{buildroot}%{_localstatedir}/lib/%{name}/snmp

install -pm 644 %{SOURCE1}   %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
install -pm 644 %{name}.conf %{buildroot}%{_sysconfdir}/sysconfig/%{name}

sed -e 's;/etc/;%{_sysconfdir}/;' \
    -e 's;/var/;%{_localstatedir}/;' \
    -e 's;/usr/sbin/;%{_sbindir}/;' \
    %{SOURCE2} > %{buildroot}%{_sysconfdir}/cron.hourly/%{name}
chmod +x %{buildroot}%{_sysconfdir}/cron.hourly/%{name}

install -m 600 %{name}.cfg %{buildroot}%{_sysconfdir}/ocsinventory/%{name}.cfg
install -m 644 etc/ocsinventory-agent/modules.conf %{buildroot}%{_sysconfdir}/ocsinventory/modules.conf

# Remove some unusefull files (which brings unresolvable deps)
rm -rf %{buildroot}%{perl_vendorlib}/Ocsinventory/Agent/Backend/OS/Win32*

# Only need for manual installation
rm %{buildroot}%{perl_vendorlib}/Ocsinventory/Unix/postinst.pl

# Provided by ocsinventtory-ipdiscover
rm %{buildroot}%{_sbindir}/ipdiscover


%clean
rm -rf %{buildroot}

%post
chmod 600 %{_sysconfdir}/ocsinventory/%{name}.cfg


%files
%defattr(-, root, root, -)
%{_sbindir}/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%{_sysconfdir}/cron.hourly/%{name}
%{_mandir}/man1/%{name}*

%files -n perl-Ocsinventory-Agent
%defattr(-, root, root, -)
%doc AUTHORS Changes LICENSE README.md THANKS README.RPM
%doc etc/ocsinventory-agent/softwares/example.sh
%lang(fr) %doc README.RPM.fr
%{perl_vendorlib}/Ocsinventory
%{_mandir}/man3/Ocs*
%dir %{_localstatedir}/log/%{name}
%dir %{_localstatedir}/lib/%{name}
%{_localstatedir}/lib/%{name}/download
%{_localstatedir}/lib/%{name}/snmp
%dir %{_sysconfdir}/ocsinventory
%dir %{_sysconfdir}/ocsinventory/softwares
%config(noreplace) %{_sysconfdir}/ocsinventory/%{name}.cfg
%config(noreplace) %{_sysconfdir}/ocsinventory/modules.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}

%changelog
* Mon Jul 18 2022 Charlene Auger <charlene.auger@ocsinventory-ng.org> - 2.9.3-2
- Remove read right of standard user on ocsinventory-agent.cfg

* Mon Jun 27 2022 Charlene Auger <charlene.auger@ocsinventory-ng.org> - 2.9.3-1
- Update to 2.9.3

* Wed Jan 26 2022 Charlene Auger <charlene.auger@ocsinventory-ng.org> - 2.9.1-1
- Update to 2.9.1

* Mon Dec 13 2021 Charlene Auger <charlene.auger@ocsinventory-ng.org> - 2.9.0-1
- Update to 2.9.0

* Mon Oct 05 2020 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.8.0-1
- Update to 2.8.0

* Wed Mar 11 2020 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.6.1-1
- Update to 2.6.1

* Tue Dec 31 2019 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.6.0-5
- Clean spec file

* Sun Dec 29 2019 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.6.0-4
- Add fixes before 2.7
- Upgrade to revision 4 to upgrade unofficial package from EPEL
- Improve some dependancies
- Prepare for rhel 8

* Mon May 20 2019 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.6.0-1
- Update to 2.6.0

* Mon Dec 31 2018 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.4.2-3
- Remove Module::Install as dependancy

* Mon Dec 24 2018 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.4.2-2
- Add core agent

* Tue Jul 31 2018 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.4.2-1
- Update to 2.4.2

* Sun Feb 11 2018 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.4.0-1
- Update to 2.4.0

* Mon Jan 15 2018 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.3.0-2
- Add SSL dependancies

* Thu Jan 12 2017 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.3.0-1
- Update to 2.3.0

* Sun Jan 01 2017 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 2.3.0-0.1
- Update to 2.3RC1

* Thu May 22 2014 Remi Collet <remi@fedoraproject.org> - 2.1.1-2
- Update to 2.1.1

* Thu Feb 13 2014 Remi Collet <remi@fedoraproject.org> - 2.1-2
- more upstream patches
- add /var/lib/ocsinventory-agent/snmp and download folder
- move /etc/ocsinventory and /var/lib to subpackage

* Thu Feb 13 2014 Remi Collet <remi@fedoraproject.org> - 2.1-1
- Update to 2.1
- move perl library to perl-Ocsinventory-Agent
- make main package arched for dependency on dmidecode

* Fri Aug 02 2013 Petr Pisar <ppisar@redhat.com> - 2.0.5-8
- Perl 5.18 rebuild

* Sat Jul 27 2013 Jóhann B. Guðmundsson <johannbg@fedoraproject.org> - 2.0.5-7
- Add a missing requirement on crontabs to spec file

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.5-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Dec 17 2012 Remi Collet <remi@fedoraproject.org> - 2.0.5-5
- fix provided configuration when build with ocsserver defined

* Sun Sep 23 2012 Remi Collet <remi@fedoraproject.org> - 2.0.5-4
- fix ifconfig output parser (#853982)
  https://bugs.launchpad.net/bugs/1045356

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jun 22 2012 Petr Pisar <ppisar@redhat.com> - 2.0.5-2
- Perl 5.16 rebuild

* Sat Apr 14 2012 Remi Collet <remi@fedoraproject.org> - 2.0.5-1
- update to 2.0.5

* Mon Feb 13 2012 Remi Collet <remi@fedoraproject.org> - 2.0.4-1
- update to 2.0.4

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.2.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Jul 20 2011 Petr Sabata <contyk@redhat.com> - 1.1.2.1-3
- Perl mass rebuild

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Oct 13 2010 Remi Collet <Fedora@famillecollet.com> 1.1.2.1-1
- security update for CVE-2009-0667
  http://bugs.debian.org/590879
  http://www.debian.org/security/2009/dsa-1828

* Sat Oct 09 2010 Remi Collet <Fedora@famillecollet.com> 1.1.2-3
- remove perl-XML-SAX optional dep, which is broken on EL5
  and cause overload when installed on the OCS server

* Tue Jun 01 2010 Marcela Maslanova <mmaslano@redhat.com> - 1.1.2-2
- Mass rebuild with perl-5.12.0

* Sun Jan 03 2010 Remi Collet <Fedora@famillecollet.com> 1.1.2-1
- update to 1.1.2

* Sun Dec 27 2009 Remi Collet <Fedora@famillecollet.com> 1.1.1-2
- missing perl(Net::IP) requires (+ some EL3 stuff: yes, I know)

* Tue Dec 22 2009 Remi Collet <Fedora@famillecollet.com> 1.1.1-1
- update to 1.1.1

* Sat Nov 28 2009 Remi Collet <Fedora@famillecollet.com> 1.1-2
- add Requires: which

* Sat Nov 07 2009 Remi Collet <Fedora@famillecollet.com> 1.1-1
- update to 1.1
- add missing modules.conf
- new Requires perl(Net::SSLeay), perl(Crypt::SSLeay), smartmontools
- download URL to launchpad

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu May 14 2009 Remi Collet <Fedora@famillecollet.com> 1.0.1-4
- fix typo

* Thu May 14 2009 Remi Collet <Fedora@famillecollet.com> 1.0.1-3
- define PATH in config (workaround for #500594 + tool path if needed)

* Fri Apr 24 2009 Remi Collet <Fedora@famillecollet.com> 1.0.1-2
- update the README.RPM (new configuration file)
- change from URL to only servername in config comment

* Sun Mar 29 2009 Remi Collet <Fedora@famillecollet.com> 1.0.1-1
- update to 1.0.1

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.0.9.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Oct 20 2008 Remi Collet <Fedora@famillecollet.com> 0.0.9.2-2
- fix FTBFS (#465073)

* Sun Apr 20 2008 Remi Collet <Fedora@famillecollet.com> 0.0.9.2-1
- update to 0.0.9.2 (minor bug fix)

* Mon Apr 07 2008 Remi Collet <Fedora@famillecollet.com> 0.0.9.1-2
- add Requires monitor-edid

* Thu Apr 03 2008 Remi Collet <Fedora@famillecollet.com> 0.0.9.1-1
- update to 0.0.9.1 (minor bug fix)
- swicth back to nobundle sources

* Wed Apr 02 2008 Remi Collet <Fedora@famillecollet.com> 0.0.9-1
- update to 0.0.9 finale
- provides default config to file (need options.patch)
- add requires nmap (for ipdiscover)
- add BR perl(XML::SAX) (to avoid install of bundled one)

* Mon Mar 10 2008 Remi Collet <Fedora@famillecollet.com> 0.0.8.2-0.6.20080305
- rebuild against perl 5.10

* Fri Mar  7 2008 Remi Collet <Fedora@famillecollet.com> 0.0.8.2-0.5.20080305
- patches from review (Patrice Dumas)

* Wed Mar  5 2008 Remi Collet <Fedora@famillecollet.com> 0.0.8.2-0.4.20080305
- update to 2008-03-05
- add /etc/sysconfig/ocsinventory-agent config file for cron job

* Mon Mar  3 2008 Remi Collet <Fedora@famillecollet.com> 0.0.8.2-0.3.20080302
- only enable cron when server is configured

* Sun Mar  2 2008 Remi Collet <Fedora@famillecollet.com> 0.0.8.2-0.2.20080302
- from Review, see #435593

* Sun Mar  2 2008 Remi Collet <Fedora@famillecollet.com> 0.0.8.2-0.1.20080302
- update to 0.0.8.2 from CVS

* Fri Feb 22 2008 Remi Collet <Fedora@famillecollet.com> 0.0.8.2-0.1.20080222
- update to 0.0.8.2 from CVS

* Sun Feb 17 2008 Remi Collet <Fedora@famillecollet.com> 0.0.8.1-0.1.20080217
- update to 0.0.8.1 from CVS
- change config file used
   from /etc/ocsinventory-agent/ocsinv.conf
     to /etc/ocsinventory/ocsinventory-agent.cfg

* Sat Jan 26 2008 Remi Collet <Fedora@famillecollet.com> 0.0.7-1
- update to 0.0.7

* Fri Dec 28 2007 Remi Collet <Fedora@famillecollet.com> 0.0.6.2-1
- update to 0.0.6.2

* Mon Apr 16 2007 Remi Collet <Fedora@famillecollet.com> 0.0.6-1
- update to 0.0.6

* Sat Feb 10 2007 Remi Collet <Fedora@famillecollet.com> 0.0.5-0.20070409
- cvs update 20070409
- create cron.daily file
- create logrotate.d file
- create ocsinv.conf
- cvs update 20070405
- cvs update 20070403

* Sat Feb 10 2007 Remi Collet <Fedora@famillecollet.com> 0.0.2-0.20070210
- initial spec
