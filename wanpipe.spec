#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
#
%if !%{with kernel}
%undefine	with_dist_kernel
%endif

%define	subver	4
%define	_rel	1
Summary:	WAN routing package for Sangoma cards
Summary(pl.UTF-8):   Pakiet do rutingu WAN dla kart Sangoma
Name:		wanpipe
Version:	2.3.4
Release:	%{subver}.%{_rel}
License:	GPL
Group:		Applications/System
Source0:	ftp://ftp.sangoma.com/linux/current_wanpipe/%{name}-%{version}-%{subver}.tgz
# Source0-md5:	c77e6ba5b62ddd79acd7b1249c950cec
Source1:	wanrouter.init
Source2:	wanrouter.sysconfig
Source3:	%{name}1.conf
Patch0:		%{name}-cfgtools.patch
Patch1:		%{name}-opt.patch
Patch2:		%{name}-setup.patch
URL:		http://www.sangoma.com/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.7}
%endif
BuildRequires:	ncurses-devel >= 5.2
BuildRequires:	rpmbuild(macros) >= 1.308
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
Summary(pl.UTF-8):   Narzędzia konfiguracyjne do wanpipe
Group:		Applications/System
Requires:	%{name} = %{version}-%{release}

%description cfgtools
Menu-driven configuration tools for WANPIPE.

%description cfgtools -l pl.UTF-8
Narzędzia konfiguracyjne do WANPIPE w postaci menu.

%package -n kernel%{_alt_kernel}-%{name}
Summary:	Linux driver for WANPIPE
Summary(pl.UTF-8):   Sterownik WANPIPE dla Linuksa
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif

%description -n kernel%{_alt_kernel}-%{name}
This package contains WANPIPE module for Linux.

%description -n kernel%{_alt_kernel}-%{name} -l pl.UTF-8
Ten pakiet zawiera moduł WANPIPE dla Linuksa.

%package -n kernel%{_alt_kernel}-smp-%{name}
Summary:	Linux SMP driver for WANPIPE
Summary(pl.UTF-8):   Sterownik WANPIPE dla Linuksa SMP
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif

%description -n kernel%{_alt_kernel}-smp-%{name}
This package contains WANPIPE module for Linux SMP.

%description -n kernel%{_alt_kernel}-smp-%{name} -l pl.UTF-8
Ten pakiet zawiera moduł WANPIPE dla Linuksa SMP.

%prep
%setup -q -n %{name}
%patch0 -p1
%patch1 -p1
%patch2 -p1

#ugly speedhack
mkdir util/wanec_client/tmp
cp patches/kdrivers/wanec/wanec_iface.h patches/kdrivers/include
cp -a patches/kdrivers/wanec/oct6100_api/include/* patches/kdrivers/include

ln -sf . patches/kdrivers/include/linux

%build

%if %{with kernel}
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf o
	install -d o/include/{linux,config}
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} o/include/asm

	#ugly speedhack
	cp patches/kdrivers/wanec/wanec_iface.h o/include/
	cp -a patches/kdrivers/wanec/oct6100_api.PR43/include/* o/include/
	ln -sf %{_kernelsrcdir}/include/linux/fs.h o/include/linux/fs.h

	%{__make} -j1 -C %{_kernelsrcdir} O=$PWD/o prepare scripts

	mkdir modules-$cfg
	echo -e 'y\n\ny\n2\n/usr/include/zaptel\ny\n\n\n\n\ny\ny\n\n\n\n' | \
	bash -x ./Setup drivers \
	--no-gcc-debug \
	--with-linux=$PWD/o \
	--builddir=$PWD/modules-$cfg
done
%endif

%{__make} -C util \
	CC="%{__cc}" \
	OPTFLAGS="%{rpmcflags}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},/etc/{rc.d/init.d,sysconfig},/var/log} \
	$RPM_BUILD_ROOT%{_datadir}/wanrouter/{firmware,wancfg}

%{__make} -C util install \
	WAN_VIRTUAL=$RPM_BUILD_ROOT

install firmware/* $RPM_BUILD_ROOT%{_datadir}/wanrouter/firmware
#install util/wancfg/lib/* $RPM_BUILD_ROOT%{_datadir}/wanrouter/wancfg

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/wanrouter
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/wanrouter
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}

touch $RPM_BUILD_ROOT/var/log/wanrouter

%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/{net/wanrouter,drivers/net/wan}

install  modules-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}/lib/modules/*/kernel/net/wanrouter/*.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/wanrouter

install  modules-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}/lib/modules/*/kernel/drivers/net/wan/*.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/net/wan
%if %{with smp} && %{with dist_kernel}

install  modules-smp/lib/modules/*/kernel/net/wanrouter/*.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/net/wanrouter

install  modules-smp/lib/modules/*/kernel/drivers/net/wan/*.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/drivers/net/wan
%endif
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
%attr(755,root,root) %{_sbindir}/wancfg
%attr(755,root,root) %{_sbindir}/wanpipe_ft1exec
%attr(755,root,root) %{_sbindir}/wanpipe_lxdialog
%{_datadir}/wanrouter/wancfg

%if %{with kernel}
%files -n kernel%{_alt_kernel}-%{name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/net/wanrouter/*.ko*
/lib/modules/%{_kernel_ver}/kernel/drivers/net/wan/*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel%{_alt_kernel}-smp-%{name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/net/wanrouter/*.ko*
/lib/modules/%{_kernel_ver}smp/kernel/drivers/net/wan/*.ko*
%endif
%endif
