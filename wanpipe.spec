# $Revision $, $Date $
Summary:	WAN routing package for Sangoma cards
Name:		wanpipe
Version:	2.1.1
Release:	0
License:	GPL
Group:		Utilities/System
Group(pl):	Narzêdzia/System
Source0:	ftp://ftp.sangoma.com/linux/current_%{name}/%{name}-%{version}.tgz
Source1:	wanrouter.init
Source2:	wanrouter.sysconfig
Source3:	wanpipe1.conf
URL:		http://www.freeciv.org/
Icon:		freeciv.gif
Requires:	kernel >= 2.2.14
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Multi-protocol WANPIPE Driver utilities for Linux Operating System

%prep
%setup -qn usr/lib/wanrouter
rm -f src/bin/*

%build
cd src
make OUTDIR=bin

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{%{_sbindir},%{_libdir}/wanrouter/wanpipe,/var/log}
install -d $RPM_BUILD_ROOT%{_sysconfdir}{/wanpipe,/rc.d/init.d,/sysconfig}

install src/bin/* $RPM_BUILD_ROOT/%{_sbindir}
install wanpipe/* $RPM_BUILD_ROOT/%{_libdir}/wanrouter/wanpipe
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/wanrouter
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/wanrouter
install %{SOURCE3} $RPM_BUILD_ROOT/etc/wanpipe

touch $RPM_BUILD_ROOT/var/log/wanrouter

gzip -9nf README doc/* samples/* || :

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
%doc README.gz doc/*.gz samples/*.gz
%dir %{_sysconfdir}/wanpipe
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/wanpipe/*
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/sysconfig/wanrouter
%attr(754,root,root) /etc/rc.d/init.d/wanrouter
%attr(755,root,root) %{_sbindir}/*
%{_libdir}/wanrouter
%attr(640,root,root) %ghost /var/log/wanrouter
