#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
#
%if !%{with kernel}
%undefine	with_dist_kernel
%endif

%define		rel    0.1

Summary:	WAN routing package for Sangoma cards
Summary(pl.UTF-8):	Pakiet do rutingu WAN dla kart Sangoma
Name:		wanpipe
Version:	3.5.18
Release:	%{rel}
License:	GPL
Group:		Applications/System
Source0:	ftp://ftp.sangoma.com/linux/current_wanpipe/%{name}-%{version}.tgz
# Source0-md5:	f72c7536555a3402165d543722da5841
Source1:	wanrouter.init
Source2:	wanrouter.sysconfig
Source3:	%{name}1.conf
Patch0:		%{name}-cfgtools.patch
Patch1:		%{name}-opt.patch
Patch2:		%{name}-setup.patch
Patch3:		%{name}-include-limits.patch
URL:		http://www.sangoma.com/
BuildRequires:	bison
BuildRequires:	flex
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.22}
BuildRequires:	libstdc++-devel
BuildRequires:	ncurses-devel >= 5.2
BuildRequires:	rpmbuild(macros) >= 1.379
BuildRequires:	dahdi-linux-devel
Requires(post,preun):	/sbin/chkconfig
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
#%patch1 -p1
%patch2 -p1
#%patch3 -p1

sed -i 's#EXTRA_UTIL_FLAGS = #EXTRA_UTIL_FLAGS = -I/usr/include/ncurses #' Makefile
sed -i 's#<ncurses.h>#<ncurses/ncurses.h>#' util/lxdialog/Makefile
sed -i 's#MODULE_EXT=".ko"#MODULE_EXT=".ko.gz"#' util/lxdialog/Makefile

%build

%if %{with kernel}
	cfg=%{!?with_dist_kernel:non}dist
	install -d o/include/{linux,config}
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h

	%{__make} -j1 -C %{_kernelsrcdir} O=$PWD/o prepare scripts

	export KBUILD_MODPOST_WARN=1

	%{__make} dahdi DAHDI_DIR=/usr KDIR=$PWD/o KVER=%{_kernel_ver} INSTALLPREFIX=%{buildroot}
	
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},/etc/{rc.d/init.d,sysconfig},/var/log} \
	$RPM_BUILD_ROOT%{_datadir}/wanrouter/{firmware,wancfg}

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

%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/{net/wanrouter,drivers/net/wan}

install  patches/kdrivers/src/net/{wanec,af_wanpipe,wanrouter}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/wanrouter

install  patches/kdrivers/src/net/{sdladrv,wanpipe_syncppp,wanpipe,wan_aften}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/net/wan

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

%files
%defattr(644,root,root,755)
%doc README doc samples
%attr(755,root,root) %{_sbindir}/sdladump
%attr(755,root,root) %{_sbindir}/wanconfig
%attr(755,root,root) %{_sbindir}/wanpipemon
%attr(755,root,root) %{_sbindir}/wpbwm
%attr(755,root,root) %{_sbindir}/wp_pppconfig
%dir %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/wanrouter
%attr(754,root,root) /etc/rc.d/init.d/wanrouter
%dir %{_datadir}/wanrouter
%{_datadir}/wanrouter/firmware
%attr(640,root,root) %ghost /var/log/wanrouter

%files cfgtools
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/cfgft1
%attr(755,root,root) %{_sbindir}/wan*
%{_datadir}/wanrouter/wancfg

%if %{with kernel}
%files -n kernel%{_alt_kernel}-%{name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/net/wanrouter/*.ko*
/lib/modules/%{_kernel_ver}/kernel/drivers/net/wan/*.ko*
%endif
