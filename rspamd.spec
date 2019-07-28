Name:             rspamd
Version:          1.9.4
Release:          1%{?dist}
Summary:          Rapid spam filtering system
License:          ASL 2.0 and LGPLv3 and BSD and MIT and CC0 and zlib
URL:              https://www.rspamd.com/
Source0:          https://github.com/vstakhov/%{name}/archive/%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:          80-rspamd.preset
Source2:          rspamd.service
Source3:          rspamd.logrotate
Source4:          rspamd.sysusers
Patch0:           rspamd-secure-ssl-ciphers.patch

BuildRequires:    cmake
BuildRequires:    fann-devel
BuildRequires:    file-devel
BuildRequires:    glib2-devel
BuildRequires:    gmime-devel
%ifarch x86_64
BuildRequires:    hyperscan-devel
%endif
BuildRequires:    jemalloc-devel
BuildRequires:    libaio-devel
BuildRequires:    libevent-devel
BuildRequires:    libicu-devel
BuildRequires:    libnsl2-devel
BuildRequires:    libunwind-devel
%ifarch ppc64 ppc64le
BuildRequires:    lua-devel
%else
BuildRequires:    luajit-devel
%endif
BuildRequires:    openssl-devel
BuildRequires:    pcre-devel
BuildRequires:    perl
BuildRequires:    perl-Digest-MD5
BuildRequires:    ragel
BuildRequires:    systemd-rpm-macros
BuildRequires:    sqlite-devel
%{?systemd_requires}
Requires:         logrotate

# Bundled dependencies
# TODO: Check for bundled js libs
# TODO: Add explicit bundled lib versions where known
# TODO: Unbundle deps where possible
# TODO: Double-check Provides
# aho-corasick: LGPL-3.0
Provides: bundled(aho-corasick)
# cdb: Public Domain
Provides: bundled(cdb) = 1.1.0
# hiredis: BSD-3-Clause
Provides: bundled(hiredis) = 0.13.3
# lc-btrie: BSD-3-Clause
Provides: bundled(lc-btrie)
# libottery: CC0
Provides: bundled(libottery)
# librdns: BSD-2-Clause
Provides: bundled(librdns)
# libucl: BSD-2-Clause
Provides: bundled(libucl)
# linenoise: BSD-2-Clause
Provides: bundled(linenoise) = 1.0
# lua-argparse: MIT
Provides: bundled(lua-argparse)
# lua-fun: MIT
Provides: bundled(lua-fun)
# lua-lpeg: MIT
Provides: bundled(lua-lpeg) = 1.0
# lua-moses: MIT
Provides: bundled(lua-moses)
# lua-tableshape: MIT
Provides: bundled(lua-tableshape) = ae67256
# lua-torch: Apache-2.0 or BSD-3-Clause
Provides: bundled(lua-torch)
# mumhash: MIT
Provides: bundled(mumhash)
# ngx-http-parser: MIT
Provides: bundled(ngx-http-parser) = 2.2.0
# perl-Mozilla-PublicSuffix: MIT
Provides: bundled(perl-Mozilla-PublicSuffix)
# snowball: BSD-3-Clause
Provides: bundled(snowball)
# t1ha: Zlib
Provides: bundled(t1ha)
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
# NOTE: To disable tests during build, set DEBIAN_BUILD=1 option
%cmake \
  -DDEBIAN_BUILD=0 \
  -DCONFDIR=%{_sysconfdir}/%{name} \
  -DMANDIR=%{_mandir} \
  -DDBDIR=%{_sharedstatedir}/%{name} \
  -DRUNDIR=%{_localstatedir}/run/%{name} \
  -DLOGDIR=%{_localstatedir}/log/%{name} \
  -DSHAREDIR=%{_datadir}/%{name} \
  -DLIBDIR=%{_libdir}/%{name}/ \
  -DSYSTEMDDIR=%{_unitdir} \
  -DENABLE_FANN=ON \
  -DENABLE_HIREDIS=ON \
%ifarch x86_64
  -DENABLE_HYPERSCAN=ON \
%endif
  -DENABLE_JEMALLOC=ON \
  -DENABLE_LIBUNWIND=ON \
%ifarch ppc64 ppc64le
  -DENABLE_LUAJIT=OFF \
  -DENABLE_TORCH=OFF \
%endif
  -DHYPERSCAN_ROOT_DIR=/opt/hyperscan \
  -DNO_SHARED=ON \
  -DRSPAMD_USER=%{name} \
  -DRSPAMD_GROUP=%{name}
%make_build

%pre
%sysusers_create_package %{name} %{SOURCE4}

%install
%{make_install} DESTDIR=%{buildroot} INSTALLDIRS=vendor
# The tests install some files we don't want so ship
rm -f %{buildroot}%{_libdir}/debug/usr/bin/rspam*
install -Ddpm 0755 %{buildroot}%{_sysconfdir}/%{name}/{local,override}.d/
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_presetdir}/80-rspamd.preset
install -Dpm 0644 %{SOURCE2} %{buildroot}%{_unitdir}/rspamd.service
install -Dpm 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/rspamd
install -Dpm 0644 %{SOURCE4} %{buildroot}%{_sysusersdir}/%{name}.conf
install -Dpm 0644 LICENSE.md %{buildroot}%{_docdir}/licenses/LICENSE.md

%post
%systemd_post rspamd.service

%preun
%systemd_preun rspamd.service

%postun
%systemd_postun_with_restart rspamd.service

%files
# TODO: Collect licenses from all bundled dependencies
%license %{_docdir}/licenses/LICENSE.md
%{_bindir}/rspam{adm,c,d}{,-%{version}}
%{_bindir}/rspamd_stats

%dir %{_datadir}/%{name}
%{_datadir}/%{name}/effective_tld_names.dat

%dir %{_datadir}/%{name}/{elastic,languages}
%{_datadir}/%{name}/{elastic,languages}/*.json
%{_datadir}/%{name}/languages/stop_words

%dir %{_datadir}/%{name}/{lualib,plugins,rules}
%{_datadir}/%{name}/{lualib,plugins,rules}/*.lua

%dir %{_datadir}/%{name}/lualib/{decisiontree,nn,lua_ffi,lua_scanners,optim,paths,rspamadm,torch}
%{_datadir}/%{name}/lualib/{decisiontree,nn,lua_ffi,lua_scanners,optim,paths,rspamadm,torch}/*.lua

%dir %{_datadir}/%{name}/rules/regexp
%{_datadir}/%{name}/rules/regexp/*.lua

%dir %{_datadir}/%{name}/www
%{_datadir}/%{name}/www/*

%dir %{_libdir}/%{name}
%{_libdir}/%{name}/*
%{_presetdir}/80-rspamd.preset
%{_mandir}/man1/rspamadm.*
%{_mandir}/man1/rspamc.*
%{_mandir}/man8/rspamd.*
%config(noreplace) %{_sysconfdir}/logrotate.d/rspamd
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/*.conf
%config(noreplace) %{_sysconfdir}/%{name}/*.inc
%dir %{_sysconfdir}/%{name}/{local,modules,override,scores}.d
%config(noreplace) %{_sysconfdir}/%{name}/{modules,scores}.d/*
%{_unitdir}/%{name}.service
%{_sysusersdir}/%{name}.conf

%changelog
* Sun Jul 28 2019 Christian Glombek <lorbus@fedoraproject.org> - 1.9.4-1
- Update to 1.9.4
- Keep versioned symlinks (Evan Klitzke)
- Run make_build macro in build section (Evan Klitzke)

* Wed Jan 30 2019 Ajay Ramaswamy <ajayr@krithika.net> - 1.8.3-2
- use proper macro for systemd preset file

* Thu Dec 20 2018 Christian Glombek <lorbus@fedoraproject.org> - 1.8.3-1
- Update to 1.8.3
- Use sysusers config and %%sysusers_create_package macro for user creation
- Added libunwind and jemalloc build dependencies
- Enabled builds for ppc arches without luajit availability
- Turned on testing during build
- Disabled install of service unit from upstream repo
- Manage local and shared state dirs with systemd service unit

* Mon Oct 22 2018 Evan Klitzke <evan@eklitzke.org> - 1.8.1-1
- Update for 1.8.1 release
- Build now uses upstream ragel, not ragel-compat

* Fri May 18 2018 patrick@pichon.me - 1.7.4
- Updated for 1.7.4 release
- Make hyperscan-devel only for x86_64 architecure for which the package exist

* Sun Mar 25 2018 evan@eklitzke.org - 1.7.1-1
- Updated for 1.7.1 release

* Wed Feb 21 2018 Christian Glombek <christian.glombek@rwth-aachen.de> - 1.6.6-1
- RPM packaging for Rspamd in Fedora
- Add patch to use OpenSSL system profile cipher list
- Add license information and provides declarations for bundled libraries
- Forked from https://raw.githubusercontent.com/vstakhov/rspamd/b1717aafa379b007a093f16358acaf4b44fc03e2/centos/rspamd.spec
