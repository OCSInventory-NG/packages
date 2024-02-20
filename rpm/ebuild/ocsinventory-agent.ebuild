# Copyright 1999-2015 Gentoo Foundation
# Copyright 2017 OCS Inventory NG Team
# Distributed under the terms of the GNU General Public License v2

EAPI=5

MODULE_AUTHOR="OCS Inventory Contributors"
MODULE_VERSION=${PV}

inherit perl-app versionator

MY_PN="Ocsinventory-Unix-Agent"
MAJ_PV="$(get_version_component_range 1-2)"

DESCRIPTION="OCS Inventory NG Agent"

HOMEPAGE="http://www.ocsinventory-ng.org/"
SRC_URI="https://github.com/OCSInventory-NG/UnixAgent/releases/download/${PV}/${MY_PN}-${PV}.tar.gz"

RESTRICT="mirror"

LICENSE="GPL-2"
SLOT="0"
KEYWORDS="~x86 ~amd64"
IUSE="nmap cups +cron +ssl X"

RDEPEND="dev-perl/XML-Simple
	virtual/perl-IO-Compress
	dev-perl/Net-IP
	dev-perl/libwww-perl
	virtual/perl-Digest-MD5
	dev-perl/Net-SSLeay
	sys-apps/dmidecode
	sys-apps/pciutils
	dev-perl/Proc-Daemon
	dev-perl/Proc-PID-File
	dev-perl/Net-SNMP
	X? ( x11-misc/read-edid )
	sys-apps/smartmontools
	nmap? ( net-analyzer/nmap
		dev-perl/Nmap-Parser )
	cups? ( dev-perl/Net-CUPS )
	cron? ( virtual/cron )
	ssl? ( dev-perl/Crypt-SSLeay )"

DEPEND="${RDEPEND}
	virtual/perl-Module-Build
	dev-lang/perl
	sys-devel/make"

S="${WORKDIR}/${MY_PN}-${PV}"

src_configure()
{
	export PERL_AUTOINSTALL=1
	perl-app_src_configure
}

src_install()
{
	perl-module_src_install
	insinto /etc/ocsinventory-agent
	newins "${FILESDIR}/etc_ocsa_modules.conf" modules.conf
	newins "${FILESDIR}/etc_ocsa_ocsinventory-agent.cfg" ocsinventory-agent.cfg
	if use cron
	then
		insinto /etc/cron.d
		newins "${FILESDIR}/etc_crond_ocsinventory-agent" ocsinventory-agent
	fi
	dodir /var/lib/ocsinventory-agent
}
