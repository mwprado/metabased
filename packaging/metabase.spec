Name:           metabase
Version:        0.57.7
Release:        1%{?dist}
Summary:        Open Source Business Intelligence and Analytics (Metabase)

License:        AGPL-3.0-only
URL:            https://www.metabase.com/
BuildArch:      noarch

# Source0: seu repositório de empacotamento (assets/patches/service templates etc.)
Source0:        https://github.com/mwprado/metabase-rpm-package/archive/refs/heads/main.zip
# Source1: código-fonte do Metabase
Source1:        https://github.com/metabase/metabase/archive/refs/tags/v%{version}.tar.gz

# Build deps (ajuste nomes conforme Fedora/EL)
BuildRequires:  bash
BuildRequires:  coreutils
BuildRequires:  findutils
BuildRequires:  sed
BuildRequires:  tar
BuildRequires:  unzip

BuildRequires:  java-21-openjdk-devel
BuildRequires:  nodejs
BuildRequires:  yarnpkg
BuildRequires:  clojure

# Runtime
Requires:       java-21-openjdk-headless
Requires:       shadow-utils
Requires(pre):  systemd
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
Metabase is an open source business intelligence tool that lets everyone work with data.
This package builds Metabase from source and installs the resulting uberjar as a systemd service.

%prep
# workspace estável
%setup -q -T -c -n wsp

# 1) extrai o metabase-rpm-package (Source0) em ./packaging
mkdir -p packaging
unzip -q %{SOURCE0} -d packaging
# achata o 1o nível (main.zip costuma vir como metabase-rpm-package-main/)
if [ -d packaging/metabase-rpm-package-main ]; then
  shopt -s dotglob
  mv packaging/metabase-rpm-package-main/* packaging/
  rmdir packaging/metabase-rpm-package-main
fi

# 2) extrai o Metabase (Source1) em ./metabase
mkdir -p metabase
tar -xzf %{SOURCE1} -C metabase --strip-components=1

%build
pushd metabase

# garante edition OSS
export MB_EDITION=oss
# deixa build mais “determinístico” em ambientes de CI/RPM
export CI=true

# Alguns builds usam JAVA_HOME; em Fedora normalmente já está ok, mas deixo explícito:
export JAVA_HOME=%{java_home}

# Build do uberjar (gera target/uberjar/metabase.jar)
./bin/build.sh

popd

%install
# diretórios
install -d %{buildroot}%{_libexecdir}/metabase
install -d %{buildroot}%{_sysconfdir}/sysconfig
install -d %{buildroot}%{_unitdir}
install -d %{buildroot}%{_sysusersdir}
install -d %{buildroot}%{_tmpfilesdir}
install -d %{buildroot}%{_localstatedir}/lib/metabase
install -d %{buildroot}%{_localstatedir}/log/metabase

# jar final
install -m 0644 metabase/target/uberjar/metabase.jar %{buildroot}%{_libexecdir}/metabase/metabase.jar

# sysconfig (opções de execução)
cat > %{buildroot}%{_sysconfdir}/sysconfig/metabase <<'EOF'
# /etc/sysconfig/metabase
# Opções extras para a JVM (memória, GC etc.)
JAVA_OPTS="-Xms512m -Xmx2g"

# Opções do Metabase (exemplos):
# MB_DB_TYPE=postgres
# MB_DB_DBNAME=metabase
# MB_DB_PORT=5432
# MB_DB_USER=metabase
# MB
