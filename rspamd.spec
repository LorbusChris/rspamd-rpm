Name:             rspamd
Version:          1.6.6
Release:          1%{?dist}
Summary:          Rapid spam filtering system
License:          ASL 2.0 and LGPLv2+ and LGPLv3 and BSD and MIT and CC0 and zlib
URL:              https://www.rspamd.com/
Source0:          https://github.com/vstakhov/rspamd/archive/%{version}.tar.gz
Source1:          80-rspamd.preset
Source2:          rspamd.service
Source3:          rspamd.logrotate
#Source4:          rspamd-sysusers.conf
Patch0:           rspamd-1.6.6-ssl_cipher_list.patch

BuildRequires:    cmake
BuildRequires:    fann-devel
BuildRequires:    file-devel
BuildRequires:    glib2-devel
BuildRequires:    gmime-devel
BuildRequires:    hyperscan-devel
BuildRequires:    libaio-devel
BuildRequires:    libevent-devel
BuildRequires:    libicu-devel
BuildRequires:    libnsl2-devel
BuildRequires:    luajit-devel
BuildRequires:    openssl-devel
BuildRequires:    pcre-devel
BuildRequires:    perl
BuildRequires:    perl-Digest-MD5
BuildRequires:    ragel-compat
BuildRequires:    systemd
BuildRequires:    sqlite-devel
%{?systemd_requires}
Requires(pre):    shadow-utils
Requires:         logrotate

# Bundled dependencies
# TODO: Add explicit bundled lib versions
# TODO: Check for bundled js libs
# TODO: Double-check Provides
# aho-corasick: LGPL-3.0
Provides: bundled(aho-corasick)
# cdb: Public Domain
Provides: bundled(cdb) = 1.1.0
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
# ngx-http-parser: MIT
Provides: bundled(ngx-http-parser) = 2.2.0
# snowball: BSD-3-Clause
Provides: bundled(snowball)
# t1ha: Zlib
Provides: bundled(t1ha)
# torch: Apache-2.0 or BSD-3-Clause
Provides: bundled(torch)

# TODO: If unpatched, un-bundle the following:
# hiredis: BSD-3-Clause
Provides: bundled(hiredis) = 0.13.3
# lgpl: LGPL-2.1
Provides: bundled(lgpl)
# linenoise: BSD-2-Clause
Provides: bundled(linenoise) = 1.0
# lua-lpeg: MIT
Provides: bundled(lpeg) = 1.0
# lua-fun: MIT
Provides: bundled(lua-fun)
# perl-Mozilla-PublicSuffix: MIT
Provides: bundled(perl-Mozilla-PublicSuffix)
# uthash: BSD
Provides: bundled(uthash) = 1.9.8
# xxhash: BSD
Provides: bundled(xxhash)
# zstd: BSD
Provides: bundled(zstd) = 1.3.1

%description
Rspamd is a rapid, modular and lightweight spam filter. It is designed to work
with big amount of mail and can be easily extended with own filters written in
lua.

%prep
%setup -q
%patch0 -p1
rm -rf centos
rm -rf debian
rm -rf docker
rm -rf freebsd

%build
# TODO: Investigate, do we want DEBIAN_BUILD=1? Any other improvements?
%cmake \
  -DCONFDIR=%{_sysconfdir}/%{name} \
  -DMANDIR=%{_mandir} \
  -DDBDIR=%{_sharedstatedir}/%{name} \
  -DRUNDIR=%{_localstatedir}/run \
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

%check
# TODO: Run Tests

%pre
getent group rspamd >/dev/null || groupadd -r rspamd
getent passwd rspamd >/dev/null || \
    useradd -r -g rspamd -d %{_sharedstatedir}/rspamd -s /sbin/nologin \
    -c "Rspamd user" rspamd
exit 0

%install
%{make_install} DESTDIR=%{buildroot} INSTALLDIRS=vendor
rm %{buildroot}%{_unitdir}/rspamd.service
install -dpm 0755 %{buildroot}%{_localstatedir}/log/%{name}
install -dpm 0755 %{buildroot}%{_sharedstatedir}/%{name}
install -Ddpm 0755 %{buildroot}%{_sysconfdir}/%{name}/local.d/
install -Ddpm 0755 %{buildroot}%{_sysconfdir}/%{name}/override.d/
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_libdir}/systemd/system-preset/80-rspamd.preset
install -Dpm 0644 %{SOURCE2} %{buildroot}%{_unitdir}/rspamd.service
install -Dpm 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/rspamd

%post
%systemd_post rspamd.service

%preun
%systemd_preun rspamd.service

%postun
%systemd_postun_with_restart rspamd.service

%files
%license LICENSE
%{_bindir}/rspamadm
%{_bindir}/rspamc
%{_bindir}/rspamd
%{_bindir}/rspamd_stats
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/effective_tld_names.dat
%dir %{_datadir}/%{name}/lib
%{_datadir}/%{name}/lib/*.lua
%dir %{_datadir}/%{name}/lua
%{_datadir}/%{name}/lua/*.lua
%dir %{_datadir}/%{name}/rules
%{_datadir}/%{name}/rules/*.lua
%dir %{_datadir}/%{name}/rules/regexp
%{_datadir}/%{name}/rules/regexp/*.lua
%dir %{_datadir}/%{name}/www
%{_datadir}/%{name}/www/*
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/*
%{_libdir}/systemd/system-preset/80-rspamd.preset
%attr(-, rspamd, rspamd) %dir %{_localstatedir}/log/%{name}
%{_mandir}/man1/rspamadm.*
%{_mandir}/man1/rspamc.*
%{_mandir}/man8/rspamd.*
%attr(-, rspamd, rspamd) %dir %{_sharedstatedir}/%{name}
%config(noreplace) %{_sysconfdir}/logrotate.d/rspamd
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/*.conf
%config(noreplace) %{_sysconfdir}/%{name}/*.inc
%dir %{_sysconfdir}/%{name}/local.d
%dir %{_sysconfdir}/%{name}/modules.d
%config(noreplace) %{_sysconfdir}/%{name}/modules.d/*
%dir %{_sysconfdir}/%{name}/override.d
%{_unitdir}/rspamd.service

%changelog
* Wed Feb 21 2018 Christian Glombek <christian.glombek@rwth-aachen.de> - 1.6.6-1
- RPM packaging for Rspamd in Fedora
- Add patch to use OpenSSL system profile cipher list
- Add license information and provides declarations for bundled libraries
- Forked from https://raw.githubusercontent.com/vstakhov/rspamd/b1717aafa379b007a093f16358acaf4b44fc03e2/centos/rspamd.spec
