Summary:	WAN routing package for Sangoma cards
Summary(pl):	Pakiet do rutingu WAN dla kart Sangoma
Name:		wanpipe
Version:	2.1.3
Release:	3
License:	GPL
Group:		Applications/System
Source0:	ftp://ftp.sangoma.com/linux/current_wanpipe/%{name}-%{version}.tgz
# Source0-md5:	d461607e5e2c53018abb1abab43bacd8
Source1:	wanrouter.init
Source2:	wanrouter.sysconfig
Source3:	%{name}1.conf
Patch0:		%{name}-cfgtools.patch
Patch1:		%{name}-opt.patch
Patch2:		%{name}-ncurses.patch
URL:		http://www.sangoma.com/
Buildrequires:	ncurses-devel >= 5.2
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Prereq:		/sbin/chkconfig

%define		_sysconfdir	/etc/wanpipe

%description
Multi-protocol WANPIPE Driver utilities for Linux Operating System.

%description -l pl
Narzędzia do wieloprotokołowego drivera WANPIPE dla Linuksa.

%package cfgtools
Summary:	Configuration tools for wanpipe
Summary(pl):	Narzędzia konfiguracyjne do wanpipe
Group:		Applications/System
Requires:	%{name} = %{version}

%description cfgtools
Menu-driven configuration tools for WANPIPE.

%description cfgtools -l pl
Narzędzia konfiguracyjne do WANPIPE w postaci menu.

%prep
%setup -qn usr/local/wanrouter
%patch0 -p1
%patch1 -p1
%patch2 -p1
rm -f util/bin/*
rm -f config/ft1/source/ft1_exec
rm -f config/lxdialog/lxdialog

%build
OPTFLAGS="%{rpmcflags}"
export OPTFLAGS

cd util
%{__make} OUTDIR=bin

cd ../config/ft1/source
%{__make}

cd ../../lxdialog
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/{%{_sbindir},%{_libdir}/wanrouter/{firmware,config/wancfg,config/ft1}} \
	$RPM_BUILD_ROOT/{/var/log,%{_sysconfdir},/etc/{rc.d/init.d,sysconfig}}

install util/bin/* $RPM_BUILD_ROOT%{_sbindir}
install firmware/* $RPM_BUILD_ROOT%{_libdir}/wanrouter/firmware
install config/lxdialog/lxdialog  $RPM_BUILD_ROOT%{_libdir}/wanrouter/config
install config/wancfg/wancfg  $RPM_BUILD_ROOT%{_sbindir}
install config/wancfg/lib/*  $RPM_BUILD_ROOT%{_libdir}/wanrouter/config/wancfg
install config/ft1/cfgft1 $RPM_BUILD_ROOT%{_sbindir}
install config/ft1/source/{ft1_exec,ft1_print}  $RPM_BUILD_ROOT%{_libdir}/wanrouter/config/ft1
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/wanrouter
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/wanrouter
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}

touch $RPM_BUILD_ROOT/var/log/wanrouter

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add wanrouter
if [ -f /var/lock/subsys/wanrouter ]; then
        /etc/rc.d/init.d/wanrouter restart 1>&2
else
	echo "Edit configuration files in /etc/wanpipe and /etc/sysconfig/interfaces"
        echo "and type \"/etc/rc.d/init.d/wanrouter start\" to start wanrouter" 1>&2
fi

%preun
if [ "$1" = "0" ]; then
        if [ -f /var/lock/subsys/wanrouter ]; then
                /etc/rc.d/init.d/wanrouter stop 1>&2
        fi
        /sbin/chkconfig --del wanrouter
fi

%files
%defattr(644,root,root,755)
%doc README doc/* samples/*
%dir %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/*
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/sysconfig/wanrouter
%attr(754,root,root) /etc/rc.d/init.d/wanrouter
%attr(755,root,root) %{_sbindir}/*
%attr(755,root,root) %dir %{_libdir}/wanrouter
%{_libdir}/wanrouter/firmware
%attr(640,root,root) %ghost /var/log/wanrouter

%files cfgtools
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/wanrouter/config/lxdialog
%attr(755,root,root) %dir %{_libdir}/wanrouter/config/ft1
%attr(755,root,root) %{_libdir}/wanrouter/config/ft1/*
%{_libdir}/wanrouter/config/wancfg
