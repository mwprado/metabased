Name:           metabase
Version:        0.57.7
Release:        1%{?dist}

Summary:        Metabase is the easy, open-source way for everyone in your company to ask questions and learn from data.

License:        GNU Affero General Public License (AGPL),
URL:            https://github.com/metabase
Source0:        https://github.com/metabase/metabase/archive/refs/tags/v%{version}.tar.gz
Source1:        https://github.com/mwprado/metabased/archive/refs/heads/main.zip

BuildArch:      %{_arch}
	
Requires(pre): /usr/sbin/useradd, /usr/bin/getent
Requires:       systemd
BuildRequires:  systemd
BuildRequires:  gcc-c++


%description
Metabase is the easy, open-source way for everyone to ask questions and learn from data.

%prep
%setup
%setup -T -D -a 1

%build
# Compile the source code for Ollama
make -C %{_builddir}/ollama-%{version}
go build

%install
# Install Ollama binary
install -Dm0755 %{_builddir}/ollama-%{version}/ollama %{buildroot}%{_bindir}/ollama

# Install Systemd service file
install -Dm0644 %{_builddir}/ollama-%{version}/ollamad-main/ollamad.service %{buildroot}%{_unitdir}/ollamad.service

# Install Config  Systemd Service file
install -Dm0644 %{_builddir}/ollama-%{version}/ollamad-main/ollamad.conf    %{buildroot}%{_sysconfdir}/ollama/ollamad.conf
           
%files
%defattr(-,root,root)
%license LICENSE
%doc README.md
%{_bindir}/ollama
%{_unitdir}/ollamad.service
%config(noreplace) %{_sysconfdir}/ollama/ollamad.conf
%dir %{_sysconfdir}/ollama

%post
# Reload Systemd daemon to recognize the service
systemctl daemon-reload

%preun
if [ $1 -eq 0 ]; then
    systemctl stop ollamad.service || true
    systemctl disable ollamad.service || true
fi

%postun
if [ $1 -eq 0 ]; then
    systemctl daemon-reload
fi

%changelog
%autochangelog
