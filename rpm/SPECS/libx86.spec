Name:           libx86
Version:        1.1
Release:        23%{?dist}
Summary:        Library for making real-mode x86 calls

Group:          System Environment/Libraries
License:        MIT
URL:            http://www.codon.org.uk/~mjg59/libx86
Source0:        http://www.codon.org.uk/~mjg59/libx86/downloads/%{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
# does not build on ppc, ppc64 and s390* yet, due to the lack of port i/o
# redirection and video routing
ExcludeArch:    ppc ppc64 s390 s390x %{sparc} aarch64

Patch0: libx86-add-pkgconfig.patch
Patch1: libx86-mmap-offset.patch
# patch from  https://bugs.debian.org/cgi-bin/bugreport.cgi?msg=34;filename=libx86-libc-test.patch.txt;att=1;bug=570676
# debian control portion removed as it fails to apply and we do not need it anyway
Patch2: libx86-libc-test.patch

%description
A library to provide support for making real-mode x86 calls with an emulated
x86 processor.

%package devel
Summary:        Development tools for programs which will use libx86
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}

%description devel
This package contains the static library and header file necessary for
development of programs that will use libx86 to make real-mode x86 calls.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1


%build
CFLAGS="$RPM_OPT_FLAGS" make BACKEND=x86emu LIBDIR=%{_libdir} %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT LIBDIR=%{_libdir}
rm $RPM_BUILD_ROOT/%{_libdir}/*.a

%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc COPYRIGHT
%{_libdir}/lib*.so.*

%files devel
%defattr(-,root,root,-)
%{_libdir}/lib*.so
%{_includedir}/*.h
%{_libdir}/pkgconfig/x86.pc

%changelog
* Thu Jan 19 2017 Philippe Beaumont <philippe.beaumont@ocsinventory-ng.org> - 1.1-23
- Backport from Fedora

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.1-22
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1-21
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1-20
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Tue Jul 08 2014 Yaakov Selkowitz <yselkowi@redhat.com> - 1.1-19
- ExcludeArch: aarch64 due to missing sys/io.h

* Tue Jun 24 2014 Dennis Gilmore <dennis@ausil.us> - 1.1-18
- add patch from debian for ftbfs

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1-17
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sun Apr 14 2013 Matthew Garrett <mjg59@srcf.ucam.org> .1-15
- Revert previous change

* Sun Apr 14 2013 Peter Robinson <pbrobinson@fedoraproject.org> 1.1-14
- Make ExclusiveArch x86

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Nov 04 2009 Dennis Gilmore <dennis@ausil.us> - 1.1-9
- Exclude sparc arches

* Tue Oct 27 2009 Adam Jackson <ajax@redhat.com> 1.1-8
- libx86-mmap-offset.patch: Attempt to make selinux happy by not mmap'ing
  the zero page.

* Thu Sep 03 2009 Karsten Hopp <karsten@redhat.com> 1.1-7
- excludearch s390, s390x where we don't have sys/io.h

* Tue Aug 04 2009 Dave Airlie <airlied@redhat.com> 1.1-6
- add pkgconfig support

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue May 20 2008 Matthew Garrett <mjg@redhat.com> 1.1-3
- Fix bizarre provides/obsoletes thinko 

* Tue May 20 2008 Matthew Garrett <mjg@redhat.com> 1.1-2
- Ensure RPM_OPT_FLAGS are passed. Patch from Till Maas.

* Mon May 19 2008 Matthew Garrett <mjg@redhat.com> 1.1-1
- Initial packaging of libx86
