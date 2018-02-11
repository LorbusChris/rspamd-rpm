Name:             rspamd
Version:          1.6.6
Release:          1%{?dist}
Summary:          Rapid spam filtering system
License:          ASL 2.0, LGPLv2+, LGPLv3, BSD, MIT, CC0, zlib
URL:              https://www.rspamd.com/
Source0:          https://github.com/vstakhov/rspamd/archive/%{version}.tar.gz
Patch0:           %{name}-ssl_cipher_list.patch

# Bundled dependencies
# TODO: Double-check Provides
# aho-corasick: LGPL-3.0
Provides: bundled(aho-corasick)
# ngx-http-parser: MIT
Provides: bundled(ngx-http-parser)
# lc-btrie: BSD-3-Clause
Provides: bundled(lc-btrie)
# libottery: CC0
Provides: bundled(libottery)
# librdns: BSD-2-Clause
Provides: bundled(librdns)
# libucl: BSD-2-Clause
Provides: bundled(libucl)
# moses: MIT
Provides: bundled(moses)
# mumhash: MIT
Provides: bundled(mumhash)
# snowball: BSD-3-Clause
Provides: bundled(snowball)
# t1ha: Zlib
Provides: bundled(t1ha)
# torch: Apache-2.0, BSD-3-Clause
Provides: bundled(torch)
# TODO: If unpatched, un-bundle the following:
# hiredis: BSD-3-Clause
Provides: bundled(hiredis)
# lgpl: LGPL-2.1
Provides: bundled(lgpl)
# linenoise: BSD-2-Clause
Provides: bundled(linenoise)
# lua-lpeg: MIT
Provides: bundled(lua-lpeg)
# lua-fun: MIT
Provides: bundled(lua-fun)
# perl-Mozilla-PublicSuffix: MIT
Provides: bundled(perl-Mozilla-PublicSuffix)
# uthash: BSD
Provides: bundled(uthash)
# xxhash: BSD
Provides: bundled(xxhash)
# zstd: BSD
Provides: bundled(zstd)
# TODO: Check for bundled js libs

%{?systemd_requires}
BuildRequires:    systemd
BuildRequires:    cmake, glib2-devel, libevent-devel, libicu-devel, openssl-devel
BuildRequires:    gmime-devel, file-devel, sqlite-devel, fann-devel
BuildRequires:    ragel-compat, luajit-devel, pcre-devel, hyperscan-devel
BuildRequires:    perl, perl-Digest-MD5
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
%patch0 -p1
rm -rf debian

%build
# TODO: Investigate, do we want DEBIAN_BUILD=1? Any other improvements?
%cmake \
  -DCONFDIR=%{_sysconfdir}/%{name} \
  -DMANDIR=%{_mandir} \
  -DDBDIR=%{_sharedstatedir}/%{name} \
  -DRUNDIR=%{_localstatedir}/run/%{name} \
  -DWANT_SYSTEMD_UNITS=ON \
  -DSYSTEMDDIR=%{_unitdir} \
  -DENABLE_LUAJIT=ON \
  -DENABLE_HIREDIS=ON \
  -DENABLE_FANN=ON \
  -DENABLE_HYPERSCAN=ON \
  -DHYPERSCAN_ROOT_DIR=/opt/hyperscan \
  -DLOGDIR=%{_localstatedir}/log/%{name} \
  -DPLUGINSDIR=%{_datadir}/%{name} \
  -DLIBDIR=%{_libdir}/%{name}/ \
  -DNO_SHARED=ON \
  -DDEBIAN_BUILD=1 \
  -DRSPAMD_USER=%{name} \
  -DRSPAMD_GROUP=%{name}

%install
%{make_install} DESTDIR=%{buildroot} INSTALLDIRS=vendor
install -p -D -m 0644 centos/sources/80-rspamd.preset %{buildroot}%{_libdir}/systemd/system-preset/80-%{name}.preset
install -p -D -m 0644 centos/sources/rspamd.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
install -d -p -m 0755 %{buildroot}%{_localstatedir}/log/%{name}
install -d -p -m 0755 %{buildroot}%{_sharedstatedir}/%{name}
install -p -D -d -m 0755 %{buildroot}%{_sysconfdir}/%{name}/local.d/
install -p -D -d -m 0755 %{buildroot}%{_sysconfdir}/%{name}/override.d/

%check
# TODO: Run Tests

%pre
# TODO: Investigate, do we need a SELinux policy for rspamd?
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
    useradd -r -g %{name} -d %{_sharedstatedir}/%{name} -s /sbin/nologin \
    -c "Rspamd user" %{name}
exit 0

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%license LICENSE
%{_unitdir}/%{name}.service
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/*
%{_libdir}/systemd/system-preset/80-%{name}.preset
%{_bindir}/rspamd
%{_bindir}/rspamd_stats
%{_bindir}/rspamc
%{_bindir}/rspamadm
%{_datadir}/%{name}/effective_tld_names.dat
%attr(-, %{name}, %{name}) %dir %{_sharedstatedir}/%{name}
%attr(-, %{name}, %{name}) %dir %{_localstatedir}/log/%{name}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/modules.d
%config(noreplace) %{_sysconfdir}/%{name}/modules.d/*
%dir %{_sysconfdir}/%{name}/local.d
%dir %{_sysconfdir}/%{name}/override.d
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %{_sysconfdir}/%{name}/composites.conf
%config(noreplace) %{_sysconfdir}/%{name}/metrics.conf
%config(noreplace) %{_sysconfdir}/%{name}/mime_types.inc
%config(noreplace) %{_sysconfdir}/%{name}/modules.conf
%config(noreplace) %{_sysconfdir}/%{name}/statistic.conf
%config(noreplace) %{_sysconfdir}/%{name}/common.conf
%config(noreplace) %{_sysconfdir}/%{name}/logging.inc
%config(noreplace) %{_sysconfdir}/%{name}/options.inc
%config(noreplace) %{_sysconfdir}/%{name}/redirectors.inc
%config(noreplace) %{_sysconfdir}/%{name}/worker-controller.inc
%config(noreplace) %{_sysconfdir}/%{name}/worker-fuzzy.inc
%config(noreplace) %{_sysconfdir}/%{name}/worker-normal.inc
%config(noreplace) %{_sysconfdir}/%{name}/2tld.inc
%config(noreplace) %{_sysconfdir}/%{name}/surbl-whitelist.inc
%config(noreplace) %{_sysconfdir}/%{name}/spf_dkim_whitelist.inc
%config(noreplace) %{_sysconfdir}/%{name}/dmarc_whitelist.inc
%config(noreplace) %{_sysconfdir}/%{name}/maillist.inc
%config(noreplace) %{_sysconfdir}/%{name}/mid.inc
%config(noreplace) %{_sysconfdir}/%{name}/worker-proxy.inc
%dir %{_datadir}/%{name}/rules
%{_datadir}/%{name}/rules/*.lua
%dir %{_datadir}/%{name}/rules/regexp
%{_datadir}/%{name}/rules/regexp/*.lua
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/lib
%{_datadir}/%{name}/lib/*.lua
%dir %{_datadir}/%{name}/lua
%{_datadir}/%{name}/lua/*.lua
%dir %{_datadir}/%{name}/www
%{_datadir}/%{name}/www/*
%{_mandir}/man8/%{name}.*
%{_mandir}/man1/rspamc.*
%{_mandir}/man1/rspamadm.*

%changelog
* Wed Feb 21 2018 Christian Glombek <christian.glombek@rwth-aachen.de> 1.6.6-1
- Update to 1.6.6
- Add patch to use OpenSSL system profile cipher list
- Add license information for bundled libraries

* Thu Oct 05 2017 Christian Glombek <christian.glombek@rwth-aachen.de> 1.6.4-2
- Incorporate Spec Review

* Sat Sep 23 2017 Christian Glombek <christian.glombek@rwth-aachen.de> 1.6.4-1
- RPM packaging for Rspamd in Fedora
- Forked from https://raw.githubusercontent.com/vstakhov/rspamd/b1717aafa379b007a093f16358acaf4b44fc03e2/centos/rspamd.spec
