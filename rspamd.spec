Name:             rspamd
Version:          3.6
Release:          1%{?dist}
Summary:          Rapid spam filtering system
License:          ASL 2.0 and LGPLv3 and BSD and MIT and CC0 and zlib
URL:              https://www.rspamd.com/
Source0:          https://github.com/%{name}/%{name}/archive/%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:          80-rspamd.preset
Source2:          rspamd.service
Source3:          rspamd.logrotate
Source4:          rspamd.sysusers
Source5:          rspamd.tmpfilesd
Patch0:           rspamd-secure-ssl-ciphers.patch

# Critical fix patch for https://github.com/rspamd/rspamd/issues/4564
Patch1:		  ffbab4fbf218514845b8e5209aec044621b1f460.patch

# see https://bugzilla.redhat.com/show_bug.cgi?id=2043092
%undefine _package_note_flags

BuildRequires:    cmake
BuildRequires:    gcc
BuildRequires:    file-devel
BuildRequires:    glib2-devel
%ifarch x86_64
BuildRequires:    hyperscan-devel
%endif
BuildRequires:    jemalloc-devel
BuildRequires:    libcurl-devel
BuildRequires:    fmt-devel
BuildRequires:    libicu-devel
BuildRequires:    libsodium-devel
BuildRequires:    libunwind-devel
%ifarch ppc64 ppc64le
BuildRequires:    lua-devel
%else
BuildRequires:    luajit-devel
%endif
BuildRequires:    openblas-devel
BuildRequires:    openssl-devel
BuildRequires:    pcre2-devel
BuildRequires:    perl
BuildRequires:    perl-Digest-MD5
BuildRequires:    ragel
BuildRequires:    systemd-rpm-macros
BuildRequires:    sqlite-devel
BuildRequires:    zlib-devel
%{?systemd_requires}
%{?sysusers_requires_compat}
Requires:         fmt
Requires:         hyperscan
Requires:         jemalloc
Requires:         logrotate
Requires:         openblas
%ifarch ppc64 ppc64le
Requires:         lua
%else
Requires:         luajit
%endif
Requires:         zlib

# Bundled dependencies
# TODO: Check for bundled js libs
# TODO: Add explicit bundled lib versions where known
# TODO: Unbundle deps where possible
# TODO: Double-check Provides
# aho-corasick: LGPL-3.0
Provides: bundled(aho-corasick)
# cdb: Public Domain
Provides: bundled(cdb) = 1.1.0
# google-ced: Apache License v2
# ced = "Compact Encoding Detection", https://github.com/google/compact_enc_det
Provides: bundled(compact_enc_det) = 37529e6
# fastutf8: MIT
Provides: bundled(fastutf8)
# hiredis: BSD-3-Clause
Provides: bundled(hiredis) = 0.13.3
# kann: MIT
Provides: bundled(kann)
# lc-btrie: BSD-3-Clause
Provides: bundled(lc-btrie)
# libev: BSD-2-Clause
Provides: bundled(libev) = 4.33
# libottery: CC0
Provides: bundled(libottery)
# librdns: BSD-2-Clause
Provides: bundled(librdns)
# libucl: BSD-2-Clause
Provides: bundled(libucl)
# lua-argparse: MIT
Provides: bundled(lua-argparse) = 0.7.0
# lua-bit: MIT
Provides: bundled(lua-bit) = 1.0.2
# lua-fun: MIT
Provides: bundled(lua-fun)
# lua-lpeg: MIT
Provides: bundled(lua-lpeg) = 1.0
# lua-lupa: MIT
Provides: bundled(lua-lupa)
# lua-moses: MIT
Provides: bundled(lua-moses)
# lua-tableshape: MIT
Provides: bundled(lua-tableshape) = ae67256
# mumhash: MIT
Provides: bundled(mumhash)
# ngx-http-parser: MIT
Provides: bundled(ngx-http-parser) = 2.2.0
# perl-Mozilla-PublicSuffix: MIT
Provides: bundled(perl-Mozilla-PublicSuffix)
# replxx: BSD-3-Clause
Provides: bundled(replxx) = 0.0.2
# snowball: BSD-3-Clause
Provides: bundled(snowball)
# t1ha: Zlib
Provides: bundled(t1ha)
# uthash: BSD
Provides: bundled(uthash) = 1.9.8
# xxhash: BSD
Provides: bundled(xxhash)
# zstd: BSD
Provides: bundled(zstd) = 1.4.5

%description
Rspamd is a rapid, modular and lightweight spam filter. It is designed to work
with big amount of mail and can be easily extended with own filters written in
lua.

%prep
%autosetup -p1
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
  -DRUNDIR=%{_rundir}/%{name} \
  -DLOGDIR=%{_localstatedir}/log/%{name} \
  -DSHAREDIR=%{_datadir}/%{name} \
  -DLIBDIR=%{_libdir}/%{name}/ \
  -DSYSTEMDDIR=%{_unitdir} \
  -DSYSTEM_FMT=ON \
%ifarch x86_64
  -DENABLE_HYPERSCAN=ON \
%endif
  -DENABLE_JEMALLOC=ON \
  -DENABLE_LIBUNWIND=ON \
%ifarch ppc64 ppc64le
  -DENABLE_LUAJIT=OFF \
%endif
  -DENABLE_PCRE2=ON \
  -DRSPAMD_USER=%{name}
%cmake_build

%pre
%sysusers_create_compat %{SOURCE4}

%install
%cmake_install
# The tests install some files we don't want so ship
rm -f %{buildroot}%{_libdir}/debug/usr/bin/rspam*
mkdir -p %{buildroot}{%{_localstatedir}/log,%{_rundir}}/%{name}/
install -Ddm 0755 %{buildroot}%{_sysconfdir}/%{name}/{local,override}.d/
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_presetdir}/80-rspamd.preset
install -Dpm 0644 %{SOURCE2} %{buildroot}%{_unitdir}/rspamd.service
install -Dpm 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/rspamd
install -Dpm 0644 %{SOURCE4} %{buildroot}%{_sysusersdir}/%{name}.conf
install -Dpm 0644 %{SOURCE5} %{buildroot}%{_tmpfilesdir}/%{name}.conf
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
%dir %{_datadir}/%{name}/{lualib,plugins,rules,redis_scripts}
%{_datadir}/%{name}/{lualib,plugins,rules,redis_scripts}/*.lua
%dir %{_datadir}/%{name}/lualib/{lua_content,lua_ffi,lua_magic,lua_scanners,lua_selectors,plugins,redis_scripts,rspamadm}
%{_datadir}/%{name}/lualib/{lua_content,lua_ffi,lua_magic,lua_scanners,lua_selectors,plugins,redis_scripts,rspamadm}/*.lua
%dir %{_datadir}/%{name}/rules/{controller,regexp}
%{_datadir}/%{name}/rules/{controller,regexp}/*.lua
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
%config(noreplace) %{_sysconfdir}/%{name}/*.{inc,conf}
%dir %{_sysconfdir}/%{name}/{local,maps,modules,override,scores}.d
%config(noreplace) %{_sysconfdir}/%{name}/{local,maps,modules,override,scores}.d/*
%{_unitdir}/%{name}.service
%{_sysusersdir}/%{name}.conf
%{_tmpfilesdir}/%{name}.conf
%dir %attr(0750,%{name},%{name}) %{_rundir}/%{name}
%dir %attr(0750,%{name},%{name}) %{_localstatedir}/log/%{name}

%changelog
* Tue Aug 08 2023 Ajay Ramaswamy <ajay@ramaswamy.net> - 3.6-1
- update to 3.6

* Sun Mar 19 2023 Ajay Ramaswamy <ajay@ramaswamy.net> - 3.5-1
- update to 3.5

* Wed Dec 07 2022 Ajay Ramaswamy <ajay@ramaswamy.net> - 3.4-2
- disable package-note-flags to fix link with gcc12
  see details in rhbz #2043092

* Thu Nov 17 2022 Ajay Ramaswamy <ajay@ramaswamy.net> - 3.4-1
- update to 3.4
- fix crash in hyperscan see https://github.com/rspamd/rspamd/issues/4329

* Mon Nov 07 2022 Ajay Ramaswamy <ajay@ramaswamy.net> - 3.3-1
- update to 3.3
- use ld.bfd to link on Fedora 36+

* Wed Mar 09 2022 Christian Glombek <lorbus@fedoraproject.org> - 3.1-3
- Add missing runtime dependencies
- Add log and run dirs

* Wed Mar 09 2022 Christian Glombek <lorbus@fedoraproject.org> - 3.1-2
- Add fmt-devel build dependency

* Fri Mar 04 2022 Christian Glombek <lorbus@fedoraproject.org> - 3.1-1
- Update to 3.1
- Fix sysusers.d file and use it according to Fedora guidelines
  (see https://fedoraproject.org/wiki/Changes/Adopting_sysusers.d_format).

* Fri Jan 08 2021 Johan Kok <johan@fedoraproject.org> - 2.7-1
- Update to 2.7
- Updated cmake rpm macros
- Updated ssl ciphers patch
- Removed replxx compile patch

* Sat Apr 25 2020 Johan Kok <johan@fedoraproject.org> - 2.5-1
- Update to 2.5

* Fri Mar 06 2020 Julian DeMille <me@jdemille.com> - 2.4-1
- update to 2.4
- integrate Felix's changes

* Thu Feb 06 2020 Felix Kaechele <heffer@fedoraproject.org> - 2.3-1
- update to 2.3
- changed upstream URL to use a sensible filename
- add lua_content directory
- use %%autosetup macro
- refresh ciphers patch
- add replxx compile fix patch

* Wed Dec 25 2019 Christian Glombek <lorbus@fedoraproject.org> - 2.2-2
- Remove untested and experimental GD support
- Remove torch related things as they are no longer part of Rspamd
- Remove untested URL_INCLUDE feature

* Tue Nov 26 2019 Johan Kok <johan@fedoraproject.org> - 2.2-1
- Update to 2.2
- Added bundled Provides for fastutf8

* Sat Nov 09 2019 Johan Kok <johan@fedoraproject.org> - 2.1-1
- Update to 2.1
- Added BuildRequire for libsodium
- Updated Source URL
- Replace libevent with bundled libev
- Updated bundled Provides for version 2.1

* Fri Aug 02 2019 Felix Kaechele <heffer@fedoraproject.org> - 1.9.4-2
- remove fann BR, deprecated in favor of torch
- add gd support
- remove gmime BR, it's unused
- add libcurl, enables the use of UCL URL includes
- add openblas support for enhanced regex performance
- switch to pcre2 for enhanced regex performance
- drop some unused defines in the cmake call

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
