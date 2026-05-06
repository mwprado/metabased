Name:           metabase
Version:        0.57.7
Release:        1%{?dist}
Summary:        Open Source Business Intelligence and Analytics (Metabase)

License:        AGPL-3.0-only
URL:            https://www.metabase.com/
BuildArch:      noarch

# Fedora 44 currently resolves Java 25 in the default buildroot. Keep the
# package name centralized so later Fedora/EL conditionals can be added cleanly.
%global metabase_java_pkg java-25-openjdk
%global metabase_java_home %{_jvmdir}/java-25-openjdk

# Source0 contains this RPM packaging repository. The spec intentionally uses
# files under packaging/ as the single source of truth for service/config assets.
Source0:        https://github.com/mwprado/rpm-pck-metabase/archive/refs/heads/main.zip

# Source1 contains the upstream Metabase source tree.
Source1:        https://github.com/metabase/metabase/archive/refs/tags/v%{version}.tar.gz

BuildRequires:  bash
BuildRequires:  coreutils
BuildRequires:  findutils
BuildRequires:  sed
BuildRequires:  tar
BuildRequires:  unzip
BuildRequires:  systemd-rpm-macros

BuildRequires:  %{metabase_java_pkg}-devel
BuildRequires:  nodejs
BuildRequires:  yarnpkg
BuildRequires:  clojure

Requires:       %{metabase_java_pkg}-headless
Requires:       shadow-utils
Requires(pre):  shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
Metabase is an open source business intelligence tool that lets everyone work
with data. This package builds Metabase from source and installs the resulting
uberjar as a systemd service.

%prep
%setup -q -T -c -n wsp

# Extract RPM packaging assets from Source0 into ./rpm-files.
mkdir -p rpm-source rpm-files
unzip -q %{SOURCE0} -d rpm-source
pkgroot="$(find rpm-source -mindepth 1 -maxdepth 1 -type d | head -n 1)"
cp -a "${pkgroot}/packaging/." rpm-files/

# Extract upstream Metabase source from Source1 into ./metabase.
mkdir -p metabase
tar -xzf %{SOURCE1} -C metabase --strip-components=1

%build
pushd metabase

export MB_EDITION=oss
export CI=true
export JAVA_HOME=%{metabase_java_home}

# Build the upstream uberjar. This is the initial working baseline; later
# revisions should address offline/reproducible dependency use.
./bin/build.sh

popd

%install
install -d %{buildroot}%{_libexecdir}/metabase
install -d %{buildroot}%{_sysconfdir}/sysconfig
install -d %{buildroot}%{_unitdir}
install -d %{buildroot}%{_sysusersdir}
install -d %{buildroot}%{_tmpfilesdir}
install -d %{buildroot}%{_localstatedir}/lib/metabase
install -d %{buildroot}%{_localstatedir}/log/metabase

install -m 0644 metabase/target/uberjar/metabase.jar \
  %{buildroot}%{_libexecdir}/metabase/metabase.jar

install -m 0644 rpm-files/systemd/metabase.service \
  %{buildroot}%{_unitdir}/metabase.service
install -m 0644 rpm-files/sysusers.d/metabase.conf \
  %{buildroot}%{_sysusersdir}/metabase.conf
install -m 0644 rpm-files/tmpfiles.d/metabase.conf \
  %{buildroot}%{_tmpfilesdir}/metabase.conf
install -m 0644 rpm-files/sysconfig/metabase \
  %{buildroot}%{_sysconfdir}/sysconfig/metabase

%pre
getent group metabase >/dev/null || groupadd -r metabase
getent passwd metabase >/dev/null || \
  useradd -r -g metabase -d /var/lib/metabase -s /usr/sbin/nologin \
    -c "Metabase Service" metabase
exit 0

%post
%systemd_post metabase.service
%tmpfiles_create %{_tmpfilesdir}/metabase.conf

%preun
%systemd_preun metabase.service

%postun
%systemd_postun_with_restart metabase.service

%files
%license metabase/LICENSE.txt
%doc metabase/README.md
%{_libexecdir}/metabase/metabase.jar
%config(noreplace) %{_sysconfdir}/sysconfig/metabase
%{_unitdir}/metabase.service
%{_sysusersdir}/metabase.conf
%{_tmpfilesdir}/metabase.conf
%dir %attr(0750,metabase,metabase) %{_localstatedir}/lib/metabase
%dir %attr(0750,metabase,metabase) %{_localstatedir}/log/metabase

%changelog
* Tue May 05 2026 Moacyr Prado <mwprado@localhost> - 0.57.7-1
- Initial RPM packaging baseline for Metabase 0.57.7
