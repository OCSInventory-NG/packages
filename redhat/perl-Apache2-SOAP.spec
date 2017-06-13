%global perlname Apache2-SOAP

Name:      perl-Apache2-SOAP
Version:   0.73
Release:   14%{?dist}
Summary:   A replacement for Apache::SOAP designed to work with mod_perl 2

Group:     Development/Libraries
License:   GPL+ or Artistic
URL:       http://search.cpan.org/dist/Apache2-SOAP/
Source:    http://search.cpan.org/CPAN/authors/id/R/RK/RKOBES/%{perlname}-%{version}.tar.gz

BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: perl(ExtUtils::MakeMaker)
BuildRequires: mod_perl-devel
# perl(ModPerl::MM) is provided by mod_perl on EL5, by mod_perl-devel on Fedora
#BuildRequires: perl(ModPerl::MM)
# BR for test (disabled)
#BuildRequires: httpd, perl(SOAP::Lite), perl(LWP::UserAgent)
#BuildRequires: perl(Test::More)

Requires:  perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

%{?perl_default_filter}


%description
This Apache Perl module provides the ability to add support for SOAP
(Simple Object Access Protocol) protocol with easy configuration
(either in .conf or in .htaccess file). This functionality should
give you lightweight option for hosting SOAP services and greatly
simplify configuration aspects. This module inherites functionality
from SOAP::Transport::HTTP2::Apache component of SOAP::Lite module.


%prep
%setup -q -n %{perlname}-%{version}


%build
%{__perl} Makefile.PL INSTALLDIRS=vendor
make %{?_smp_mflags}


%install
rm -rf %{buildroot}
make pure_install PERL_INSTALL_ROOT=%{buildroot}
find %{buildroot} -type f -name .packlist -exec rm -f {} ';' -print
find %{buildroot} -type d -depth -exec rmdir {} 2>/dev/null ';' -print
chmod -R u+rwX,go+rX,go-w %{buildroot}/*


%clean
rm -rf %{buildroot}


%check
# Running apache on koji fails
#APACHE_TEST_HTTPD=%{_sbindir}/httpd make test


%files
%defattr(-, root, root, -)
%doc Changes README
%{_mandir}/man3/Apache*
%{perl_vendorlib}/Apache2
%{perl_vendorlib}/SOAP/Transport/HTTP2.pm


%changelog
* Sun Jun 26 2016 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 0.73-14
- Rebuild for OCS Inventory NG repository

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.73-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.73-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jun 11 2012 Petr Pisar <ppisar@redhat.com> - 0.73-11
- Perl 5.16 rebuild

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.73-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Jun 17 2011 Marcela Mašláňová <mmaslano@redhat.com> - 0.73-9
- Perl mass rebuild

* Sat Feb 12 2011 Remi Collet <Fedora@famillecollet.com> 0.73-8
- disable test as running apache seems a bad idea

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.73-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Dec 14 2010 Marcela Maslanova <mmaslano@redhat.com> - 0.73-6
- 661697 rebuild for fixing problems with vendorach/lib

* Thu Apr 29 2010 Marcela Maslanova <mmaslano@redhat.com> - 0.73-5
- Mass rebuild with perl-5.12.0

* Mon Dec  7 2009 Stepan Kasal <skasal@redhat.com> - 0.73-4
- rebuild against perl 5.10.1

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.73-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.73-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Jul 22 2008 Remi Collet <Fedora@famillecollet.com> 0.73-1
- initial spec

