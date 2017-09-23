%define rspamd_user       _rspamd
%define rspamd_group      %{rspamd_user}
%define rspamd_home       %{_localstatedir}/lib/rspamd
%define rspamd_logdir     %{_localstatedir}/log/rspamd
%define rspamd_confdir    %{_sysconfdir}/rspamd
%define rspamd_pluginsdir %{_datadir}/rspamd
%define rspamd_rulesdir   %{_datadir}/rspamd/rules
%define rspamd_wwwdir     %{_datadir}/rspamd/www

Name:             rspamd
Version:          1.6.4
Release:          1%{?dist}
Summary:          Rapid spam filtering system
License:          ASL 2.0
URL:              https://rspamd.com/

Source0:          https://github.com/vstakhov/rspamd/archive/%{version}.tar.gz

%{?systemd_requires}
BuildRequires:    systemd
BuildRequires:    cmake, glib2-devel, libevent-devel, libicu-devel, openssl-devel
BuildRequires:    gmime-devel, file-devel, sqlite-devel, fann-devel
BuildRequires:    ragel-compat, luajit-devel, pcre-devel, hyperscan-devel
BuildRequires:    perl-Digest-MD5
Requires(pre):    systemd, shadow-utils
Requires(post):   systemd
Requires:         logrotate
Requires(preun):  systemd
Requires(postun): systemd

%description
Rspamd is a rapid, modular and lightweight spam filter. It is designed to work
with big amount of mail and can be easily extended with own filters written in
lua.

%prep
%setup -q

%build
%{__cmake} \
  -DCMAKE_C_OPT_FLAGS="%{optflags}" \
  -DCMAKE_INSTALL_PREFIX=%{_prefix} \
  -DCONFDIR=%{_sysconfdir}/rspamd \
  -DMANDIR=%{_mandir} \
  -DDBDIR=%{_localstatedir}/lib/rspamd \
  -DRUNDIR=%{_localstatedir}/run/rspamd \
  -DWANT_SYSTEMD_UNITS=ON \
  -DSYSTEMDDIR=%{_unitdir} \
  -DENABLE_LUAJIT=ON \
  -DENABLE_HIREDIS=ON \
  -DENABLE_FANN=ON \
  -DENABLE_HYPERSCAN=ON \
  -DHYPERSCAN_ROOT_DIR=/opt/hyperscan \
  -DLOGDIR=%{_localstatedir}/log/rspamd \
  -DPLUGINSDIR=%{_datadir}/rspamd \
  -DLIBDIR=%{_libdir}/rspamd/ \
  -DINCLUDEDIR=%{_includedir} \
  -DNO_SHARED=ON \
  -DDEBIAN_BUILD=1 \
  -DRSPAMD_GROUP=%{rspamd_group} \
  -DRSPAMD_USER=%{rspamd_user}

%{__make} %{?jobs:-j%jobs}

%install
%{__make} install DESTDIR=%{buildroot} INSTALLDIRS=vendor
%{__install} -p -D -m 0644 centos/sources/80-rspamd.preset %{buildroot}%{_presetdir}/80-rspamd.preset
%{__install} -p -D -m 0644 centos/sources/rspamd.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__install} -d -p -m 0755 %{buildroot}%{rspamd_logdir}
%{__install} -d -p -m 0755 %{buildroot}%{rspamd_home}
%{__install} -p -D -d -m 0755 %{buildroot}%{_sysconfdir}/%{name}/local.d/
%{__install} -p -D -d -m 0755 %{buildroot}%{_sysconfdir}/%{name}/override.d/

%pre
getent group GROUPNAME >/dev/null || groupadd -r %{rspamd_group}
getent passwd USERNAME >/dev/null || \
    useradd -r -g %{rspamd_group} -d %{rspamd_home} -s /sbin/nologin \
    -c "Rspamd user" %{rspamd_user}
exit 0

%post
#to allow easy upgrade from 0.8.1
%{__chown} -R %{rspamd_user}:%{rspamd_group} %{rspamd_home}
#Macro is not used as we want to do this on upgrade
#%systemd_post %{name}.service
systemctl --no-reload preset %{name}.service >/dev/null 2>&1 || :
%{__chown} %{rspamd_user}:%{rspamd_group} %{rspamd_logdir}

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%{_unitdir}/%{name}.service
%{_presetdir}/80-rspamd.preset
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%dir %{rspamd_logdir}
%{_mandir}/man8/%{name}.*
%{_mandir}/man1/rspamc.*
%{_mandir}/man1/rspamadm.*
%{_bindir}/rspamd
%{_bindir}/rspamd_stats
%{_bindir}/rspamc
%{_bindir}/rspamadm
%config(noreplace) %{rspamd_confdir}/%{name}.conf
%config(noreplace) %{rspamd_confdir}/composites.conf
%config(noreplace) %{rspamd_confdir}/metrics.conf
%config(noreplace) %{rspamd_confdir}/mime_types.inc
%config(noreplace) %{rspamd_confdir}/modules.conf
%config(noreplace) %{rspamd_confdir}/statistic.conf
%config(noreplace) %{rspamd_confdir}/common.conf
%config(noreplace) %{rspamd_confdir}/logging.inc
%config(noreplace) %{rspamd_confdir}/options.inc
%config(noreplace) %{rspamd_confdir}/redirectors.inc
%config(noreplace) %{rspamd_confdir}/worker-controller.inc
%config(noreplace) %{rspamd_confdir}/worker-fuzzy.inc
%config(noreplace) %{rspamd_confdir}/worker-normal.inc
%config(noreplace) %{rspamd_confdir}/modules.d/*
%attr(-, %{rspamd_user}, %{rspamd_group}) %dir %{rspamd_home}
%dir %{rspamd_rulesdir}/regexp
%dir %{rspamd_rulesdir}
%dir %{rspamd_confdir}
%dir %{rspamd_confdir}/modules.d
%dir %{rspamd_confdir}/local.d
%dir %{rspamd_confdir}/override.d
%dir %{rspamd_pluginsdir}/lua
%dir %{rspamd_pluginsdir}
%dir %{rspamd_wwwdir}
%dir %{_libdir}/rspamd
%config(noreplace) %{rspamd_confdir}/2tld.inc
%config(noreplace) %{rspamd_confdir}/surbl-whitelist.inc
%config(noreplace) %{rspamd_confdir}/spf_dkim_whitelist.inc
%config(noreplace) %{rspamd_confdir}/dmarc_whitelist.inc
%config(noreplace) %{rspamd_confdir}/maillist.inc
%config(noreplace) %{rspamd_confdir}/mid.inc
%config(noreplace) %{rspamd_confdir}/worker-proxy.inc
%{rspamd_pluginsdir}/lib/*.lua
%{rspamd_pluginsdir}/lua/*.lua
%{rspamd_rulesdir}/regexp/*.lua
%{rspamd_rulesdir}/*.lua
%{rspamd_wwwdir}/*
%{_libdir}/rspamd/*
%{_datadir}/rspamd/effective_tld_names.dat

%changelog
* Sat Sep 23 2017 Christian Glombek <christian.glombek@rwth-aachen.de> 1.6.4-1
- RPM packaging for Rspamd in Fedora
- Forked from https://raw.githubusercontent.com/vstakhov/rspamd/b1717aafa379b007a093f16358acaf4b44fc03e2/centos/rspamd.spec
