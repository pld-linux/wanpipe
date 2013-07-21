#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
#
%if %{without kernel}
%undefine	with_dist_kernel
%endif

%define		rel    0.1

Summary:	WAN routing package for Sangoma cards
Summary(pl.UTF-8):	Pakiet do rutingu WAN dla kart Sangoma
Name:		wanpipe
Version:	7.0.5
Release:	%{rel}
License:	GPL
Group:		Applications/System
Source0:	ftp://ftp.sangoma.com/linux/current_wanpipe/%{name}-%{version}.tgz
# Source0-md5:	bb058a15054b5d252bcf703adb8a3d5a
Source1:	wanrouter.init
Source2:	wanrouter.sysconfig
Source3:	%{name}1.conf
Patch0:		%{name}-cfgtools.patch
Patch1:		%{name}-opt.patch
Patch2:		%{name}-setup.patch
Patch3:		%{name}-kbuild.patch
URL:		http://www.sangoma.com/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	dahdi-linux-devel
BuildRequires:	flex
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.22}
BuildRequires:	libstdc++-devel
BuildRequires:	libtool
BuildRequires:	ncurses-devel >= 5.2
BuildRequires:	rpmbuild(macros) >= 1.379
BuildRequires:	sed >= 4.0
Requires(post,preun):	/sbin/chkconfig
Requires:	%{name}-libs = %{version}-%{release}
Requires:	rc-scripts
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/wanpipe

%description
Multi-protocol WANPIPE Driver utilities for Linux Operating System.

%description -l pl.UTF-8
Narzędzia do wieloprotokołowego sterownika WANPIPE dla Linuksa.

%package cfgtools
Summary:	Configuration tools for wanpipe
Summary(pl.UTF-8):	Narzędzia konfiguracyjne do wanpipe
Group:		Applications/System
Requires:	%{name} = %{version}-%{release}

%description cfgtools
Menu-driven configuration tools for WANPIPE.

%description cfgtools -l pl.UTF-8
Narzędzia konfiguracyjne do WANPIPE w postaci menu.

%package libs
Summary:	Sangoma WANPIPE libraries
Summary(pl.UTF-8):	Biblioteki Sangoma WANPIPE
Group:		Libraries

%description libs
Sangoma WANPIPE libraries.

%description libs -l pl.UTF-8
Biblioteki Sangoma WANPIPE.

%package devel
Summary:	Header files for Sangoma WANPIPE libraries
Summary(pl.UTF-8):	Pliki nagłówkowe bibliotek Sangoma WANPIPE
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
Header files for Sangoma WANPIPE libraries.

%description devel -l pl.UTF-8
Pliki nagłówkowe bibliotek Sangoma WANPIPE.

%package static
Summary:	Static Sangoma WANPIPE libraries
Summary(pl.UTF-8):	Biblioteki statyczne Sangoma WANPIPE
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static Sangoma WANPIPE libraries.

%description static -l pl.UTF-8
Biblioteki statyczne Sangoma WANPIPE.

%package -n kernel%{_alt_kernel}-%{name}
Summary:	Linux driver for WANPIPE
Summary(pl.UTF-8):	Sterownik WANPIPE dla Linuksa
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%endif

%description -n kernel%{_alt_kernel}-%{name}
This package contains WANPIPE module for Linux.

%description -n kernel%{_alt_kernel}-%{name} -l pl.UTF-8
Ten pakiet zawiera moduł WANPIPE dla Linuksa.

%prep
%setup -q
#%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

sed -i 's#EXTRA_UTIL_FLAGS = #EXTRA_UTIL_FLAGS = -I/usr/include/ncurses #' Makefile
sed -i 's#<ncurses.h>#<ncurses/ncurses.h>#' util/lxdialog/Makefile
sed -i 's#MODULE_EXT=".ko"#MODULE_EXT=".ko.gz"#' util/lxdialog/Makefile

sed "1a\include $(pwd)/Makefile.kbuild" -i patches/kdrivers/src/net/Makefile

%build
cd api/libstelephony
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
cd ../..

%{__make} all_kmod_dahdi all_util all_lib \
	CC="%{__cc}" \
	OPTFLAGS="%{rpmcflags}" \
	DAHDI_DIR=/usr
#	INSTALLPREFIX=$RPM_BUILD_ROOT

%if %{with kernel}
%build_kernel_modules -C patches/kdrivers/src/net -m {af_wanpipe,sdladrv,wanrouter,wanpipe,wanpipe_syncppp,wanec,wan_aften}
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},/etc/{rc.d/init.d,sysconfig},/var/log} \
	$RPM_BUILD_ROOT%{_datadir}/wanrouter/{firmware,wancfg}

%{__make} install_lib \
	INSTALLPREFIX=$RPM_BUILD_ROOT

%{__make} -C util install \
	WAN_VIRTUAL=$RPM_BUILD_ROOT

install firmware/*.sfm $RPM_BUILD_ROOT%{_datadir}/wanrouter/firmware
#install util/wancfg/lib/* $RPM_BUILD_ROOT%{_datadir}/wanrouter/wancfg

#install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/wanrouter

sed 's#MODULE_EXT=".ko"#MODULE_EXT=".ko.gz"#' samples/wanrouter > $RPM_BUILD_ROOT/etc/rc.d/init.d/wanrouter
ln -s /etc/rc.d/init.d/wanrouter $RPM_BUILD_ROOT/%{_sbindir}/wanrouter

install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/wanrouter
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}

touch $RPM_BUILD_ROOT/var/log/wanrouter

%{__mv} $RPM_BUILD_ROOT/usr/local/sbin/setup-sangoma $RPM_BUILD_ROOT/usr/sbin/setup-sangoma

%if %{with kernel}
%install_kernel_modules -m patches/kdrivers/src/net/{wanec,af_wanpipe,wanrouter} -d kernel/net/wanrouter
%install_kernel_modules -m patches/kdrivers/src/net/{sdladrv,wanpipe_syncppp,wanpipe,wan_aften} -d kernel/drivers/net/wan
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add wanrouter
%service wanrouter restart
if [ "$1" = 1 ]; then
	echo "Edit configuration files in %{_sysconfdir} and /etc/sysconfig/interfaces"
fi

%preun
if [ "$1" = "0" ]; then
	%service wanrouter stop
	/sbin/chkconfig --del wanrouter
fi

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc README doc samples
%attr(755,root,root) %{_sbindir}/setup-sangoma
%attr(755,root,root) %{_sbindir}/wanconfig
%attr(755,root,root) %{_sbindir}/wanpipemon
%attr(755,root,root) %{_sbindir}/wanrouter
%attr(755,root,root) %{_sbindir}/wpbwm
%attr(755,root,root) %{_sbindir}/wp_pppconfig
%dir %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/wanpipe1.conf
%dir %{_sysconfdir}/lib
%{_sysconfdir}/lib/*_lib.sh
%{_sysconfdir}/lib/lib.sh
%{_sysconfdir}/lib/help.sh
%dir %{_sysconfdir}/util
%dir %{_sysconfdir}/util/wan_aftup
%{_sysconfdir}/util/wan_aftup/*.BIN
%attr(754,root,root) %{_sysconfdir}/util/wan_aftup/update_aft_firm.sh
# XXX: ELF binary
%attr(754,root,root) %{_sysconfdir}/util/wan_aftup/wan_aftup
%dir %{_sysconfdir}/util/wan_aftup/scripts
%attr(754,root,root) %{_sysconfdir}/util/wan_aftup/scripts/load.sh
%attr(754,root,root) %{_sysconfdir}/util/wan_aftup/scripts/unload.sh
%dir %{_sysconfdir}/wancfg_zaptel
%{_sysconfdir}/wancfg_zaptel/Makefile
%{_sysconfdir}/wancfg_zaptel/*.pm
%attr(754,root,root) %{_sysconfdir}/wancfg_zaptel/clean.sh
%attr(754,root,root) %{_sysconfdir}/wancfg_zaptel/install.sh
%attr(754,root,root) %{_sysconfdir}/wancfg_zaptel/uninstall.sh
%attr(754,root,root) %{_sysconfdir}/wancfg_zaptel/setup-sangoma
%attr(754,root,root) %{_sysconfdir}/wancfg_zaptel/wancfg_*
%{_sysconfdir}/wancfg_zaptel/templates
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/wanrouter
%attr(754,root,root) /etc/rc.d/init.d/wanrouter
%dir %{_datadir}/wanrouter
%{_datadir}/wanrouter/firmware
%attr(640,root,root) %ghost /var/log/wanrouter

%files cfgtools
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/wan_aftup
%attr(755,root,root) %{_sbindir}/wan_ec_client
%attr(755,root,root) %{_sbindir}/wan_plxup
%attr(755,root,root) %{_sbindir}/wancfg_*
%attr(755,root,root) %{_sbindir}/wanconfig
%attr(755,root,root) %{_sbindir}/wanpipe_lxdialog
%attr(755,root,root) %{_sbindir}/wanpipemon
%attr(755,root,root) %{_sbindir}/wanpipemon_legacy
%{_datadir}/wanrouter/wancfg

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libsangoma.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libsangoma.so.3
%attr(755,root,root) %{_libdir}/libstelephony.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libstelephony.so.1

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libsangoma.so
%attr(755,root,root) %{_libdir}/libstelephony.so
%{_libdir}/libsangoma.la
%{_libdir}/libstelephony.la
%{_includedir}/libhpsangoma.h
%{_includedir}/libsangoma.h
%{_includedir}/libstelephony.h
%{_includedir}/wanec_api.h

%files static
%defattr(644,root,root,755)
%{_libdir}/libsangoma.a
%{_libdir}/libstelephony.a

%if %{with kernel}
%files -n kernel%{_alt_kernel}-%{name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/drivers/net/wan/sdladrv.ko*
/lib/modules/%{_kernel_ver}/kernel/drivers/net/wan/wan_aften.ko*
/lib/modules/%{_kernel_ver}/kernel/drivers/net/wan/wanpipe.ko*
/lib/modules/%{_kernel_ver}/kernel/drivers/net/wan/wanpipe_syncppp.ko*
/lib/modules/%{_kernel_ver}/kernel/net/wanrouter/af_wanpipe.ko*
/lib/modules/%{_kernel_ver}/kernel/net/wanrouter/wanec.ko*
/lib/modules/%{_kernel_ver}/kernel/net/wanrouter/wanrouter.ko*
%endif
