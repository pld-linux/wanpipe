Summary:	WAN routing package for Sangoma cards
Summary(pl):	Pakiet do rutingu WAN dla kart Sangoma
Name:		wanpipe
Version:	2.3.0
%define	subver	9
Release:	%{subver}.2
License:	GPL
Group:		Applications/System
Source0:	ftp://ftp.sangoma.com/linux/current_wanpipe/%{name}-%{version}-%{subver}.tgz
# Source0-md5:	f8ff399a2f9bb0afc3be418e401e7b30
Source1:	wanrouter.init
Source2:	wanrouter.sysconfig
Source3:	%{name}1.conf
Patch0:		%{name}-cfgtools.patch
Patch1:		%{name}-opt.patch
URL:		http://www.sangoma.com/
BuildRequires:	ncurses-devel >= 5.2
PreReq:		rc-scripts
Requires(post,preun):	/sbin/chkconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/wanpipe

%description
Multi-protocol WANPIPE Driver utilities for Linux Operating System.

%description -l pl
Narzędzia do wieloprotokołowego sterownika WANPIPE dla Linuksa.

%package cfgtools
Summary:	Configuration tools for wanpipe
Summary(pl):	Narzędzia konfiguracyjne do wanpipe
Group:		Applications/System
Requires:	%{name} = %{version}-%{release}

%description cfgtools
Menu-driven configuration tools for WANPIPE.

%description cfgtools -l pl
Narzędzia konfiguracyjne do WANPIPE w postaci menu.

%prep
%setup -q -n %{name}
%patch0 -p1
%patch1 -p1

ln -sf . patches/kdrivers/include/linux

# hack to omit searching libncurses.so in somedirs/lib
touch util/lxdialog/ncurses

%build
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
install util/wancfg/lib/* $RPM_BUILD_ROOT%{_datadir}/wanrouter/wancfg

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
%doc README doc samples
%attr(755,root,root) %{_sbindir}/sdladump
%attr(755,root,root) %{_sbindir}/wanconfig
%attr(755,root,root) %{_sbindir}/wanpipemon
%attr(755,root,root) %{_sbindir}/wpbwm
%attr(755,root,root) %{_sbindir}/wp_pppconfig
%dir %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/*
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/sysconfig/wanrouter
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
