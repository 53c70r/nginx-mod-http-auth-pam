%global _hardened_build 1
%global nginx_version 1.26.1
%global nginx_user nginx
%global debug_package %{nil}
%global with_aio 1

%if 0%{?fedora} > 22
%global with_mailcap_mimetypes 1
%endif

%ifnarch s390 s390x ppc64 ppc64le
%global with_gperftools 1
%endif

%undefine _strict_symbol_defs_build
%bcond_with geoip

Name:           nginx-mod-http-auth-pam
Version:        1.5.5
Release:        1%{?dist}
Summary:        Nginx module to use PAM for simple http authentication
License:        ASL 2.0
URL:            https://github.com/sto/ngx_http_auth_pam_module

Source0:        https://github.com/sto/ngx_http_auth_pam_module/archive/refs/tags/v%{version}.tar.gz

Source2:        https://nginx.org/download/nginx-%{nginx_version}.tar.gz
Source3:        https://nginx.org/download/nginx-%{nginx_version}.tar.gz.asc
Source4:        mod-http-auth-pam.conf
Source101:      https://nginx.org/keys/is.key
Source102:      https://nginx.org/keys/maxim.key
Source103:      https://nginx.org/keys/mdounin.key
Source104:      https://nginx.org/keys/sb.key
Source105:      https://nginx.org/keys/thresh.key

Patch0:         nginx-auto-cc-gcc.patch

%if 0%{?with_gperftools}
BuildRequires:  gperftools-devel
%endif
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  gd-devel
BuildRequires:  libtool
BuildRequires:  libxslt-devel
BuildRequires:  nginx
BuildRequires:  openssl-devel
BuildRequires:  pcre-devel
BuildRequires:  perl-devel
BuildRequires:  perl(ExtUtils::Embed)
BuildRequires:  zlib-devel
BuildRequires:  pam-devel
BuildRequires:  gpg

Requires:       nginx = 1:%{nginx_version}

%description
HTTP Basic Authentication using PAM.

%prep
cat %{S:101} %{S:102} %{S:103} %{S:104} %{S:105} > %{_builddir}/nginx.gpg
cat %{SOURCE4} > %{_builddir}/mod-http-auth-pam.conf
%{gpgverify} --keyring='%{_builddir}/nginx.gpg' --signature='%{SOURCE3}' --data='%{SOURCE2}'
sed -i "s#MODULE_PATH#%{_prefix}/%{_lib}/nginx/modules/ngx_http_auth_pam_module.so#g" %{_builddir}/mod-http-auth-pam.conf

# extract ngx_http_auth_pam_module
%setup -n ngx_http_auth_pam_module-%{version}
# extract nginx next to ngx_http_auth_pam_module
%setup -T -b 2 -n nginx-%{nginx_version}
%patch0 -p 0

%build
export DESTDIR=%{buildroot}
./configure %(nginx -V 2>&1 | grep 'configure arguments' | sed -r 's@^[^:]+: @@') --add-dynamic-module="../ngx_http_auth_pam_module-%{version}"
make modules %{?_smp_mflags}

%install
%{__install} -p -D -m 0755 objs/ngx_http_auth_pam_module.so %{buildroot}%{_libdir}/nginx/modules/ngx_http_auth_pam_module.so
%{__install} -p -D -m 0644 %{_builddir}/mod-http-auth-pam.conf %{buildroot}%{_datadir}/nginx/modules/mod-http-auth-pam.conf

%files
%{_libdir}/nginx/modules/ngx_http_auth_pam_module.so
%{_datadir}/nginx/modules/mod-http-auth-pam.conf
%license ../ngx_http_auth_pam_module-%{version}/LICENSE

%changelog
* Fri Mar 3 2023 Silvan Nagl <mail@53c70r.de> 1.5.3-2
- Get configure arguments dynamically
