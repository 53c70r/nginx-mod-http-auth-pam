%global _hardened_build 1
%global nginx_user nginx
%global debug_package %{nil}
%global with_aio 1
%global fedora_nginx_version 1.20.2

%if 0%{?fedora} > 22
%global with_mailcap_mimetypes 1
%endif

%ifnarch s390 s390x ppc64 ppc64le
%global with_gperftools 1
%endif

%undefine _strict_symbol_defs_build
%bcond_with geoip

Name:           nginx-mod-http-auth-pam
Version:        1.5.3
Release:        0%{?dist}
Summary:        Nginx module to use PAM for simple http authentication
License:        ASL 2.0
BuildArch:      x86_64
URL:            https://github.com/sto/ngx_http_auth_pam_module

Source0:        https://github.com/sto/ngx_http_auth_pam_module/archive/refs/tags/v%{version}.tar.gz

Source2:        https://nginx.org/download/nginx-%{fedora_nginx_version}.tar.gz
Source3:        https://nginx.org/download/nginx-%{fedora_nginx_version}.tar.gz.asc
Source4:        mod-http-auth-pam.conf
Source101:      https://nginx.org/keys/is.key
Source102:      https://nginx.org/keys/maxim.key
Source103:      https://nginx.org/keys/mdounin.key
Source104:      https://nginx.org/keys/sb.key

Patch0:         nginx-auto-cc-gcc.patch

%if 0%{?with_gperftools}
BuildRequires:  gperftools-devel
%endif

BuildRequires:  gcc
BuildRequires:  openssl-devel
BuildRequires:  pcre-devel
BuildRequires:  zlib-devel
BuildRequires:  libxslt-devel
BuildRequires:  gd-devel
BuildRequires:  GeoIP-devel
BuildRequires:  libcurl-devel
BuildRequires:  yajl-devel
BuildRequires:  lmdb-devel
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  perl-ExtUtils-Embed
BuildRequires:  libmodsecurity-nginx-devel
BuildRequires:  gnupg
BuildRequires:  pam-devel


Requires:       nginx >= %{fedora_nginx_version}

%description
HTTP Basic Authentication using PAM.

%prep
cat %{S:101} %{S:102} %{S:103} %{S:104} > %{_builddir}/nginx.gpg
%{gpgverify} --keyring='%{_builddir}/nginx.gpg' --signature='%{SOURCE3}' --data='%{SOURCE2}'

# extract ngx_http_auth_pam_module
%setup -n ngx_http_auth_pam_module-%{version}
# extract nginx next to ngx_http_auth_pam_module
%setup -T -b 2 -n nginx-%{fedora_nginx_version}
%patch0 -p 0

%build
export DESTDIR=%{buildroot}
nginx_ldopts="$RPM_LD_FLAGS -Wl,-E"
if ! ./configure \
    --prefix=%{_datadir}/nginx \
    --sbin-path=%{_sbindir}/nginx \
    --modules-path=%{nginx_moduledir} \
    --conf-path=%{_sysconfdir}/nginx/nginx.conf \
    --error-log-path=%{_localstatedir}/log/nginx/error.log \
    --http-log-path=%{_localstatedir}/log/nginx/access.log \
    --http-client-body-temp-path=%{_localstatedir}/lib/nginx/tmp/client_body \
    --http-proxy-temp-path=%{_localstatedir}/lib/nginx/tmp/proxy \
    --http-fastcgi-temp-path=%{_localstatedir}/lib/nginx/tmp/fastcgi \
    --http-uwsgi-temp-path=%{_localstatedir}/lib/nginx/tmp/uwsgi \
    --http-scgi-temp-path=%{_localstatedir}/lib/nginx/tmp/scgi \
    --pid-path=/run/nginx.pid \
    --lock-path=/run/lock/subsys/nginx \
    --user=%{nginx_user} \
    --group=%{nginx_user} \
    --with-compat \
    --with-debug \
%if 0%{?with_aio}
    --with-file-aio \
%endif
%if 0%{?with_gperftools}
    --with-google_perftools_module \
%endif
    --with-http_addition_module \
    --with-http_auth_request_module \
    --with-http_dav_module \
    --with-http_degradation_module \
    --with-http_flv_module \
%if %{with geoip}
    --with-http_geoip_module=dynamic \
%endif
    --with-http_gunzip_module \
    --with-http_gzip_static_module \
    --with-http_image_filter_module=dynamic \
    --with-http_mp4_module \
    --with-http_perl_module=dynamic \
    --with-http_random_index_module \
    --with-http_realip_module \
    --with-http_secure_link_module \
    --with-http_slice_module \
    --with-http_ssl_module \
    --with-http_stub_status_module \
    --with-http_sub_module \
    --with-http_v2_module \
    --with-http_xslt_module=dynamic \
    --with-mail=dynamic \
    --with-mail_ssl_module \
    --with-pcre \
    --with-pcre-jit \
    --with-stream=dynamic \
    --with-stream_ssl_module \
    --with-stream_ssl_preread_module \
    --with-threads \
    --with-cc-opt="%{optflags} $(pcre-config --cflags)" \
    --with-ld-opt="$nginx_ldopts" \
    --add-dynamic-module="../ngx_http_auth_pam_module-%{version}"; then
  : configure failed
  cat objs/autoconf.err
  exit 1
fi

make modules %{?_smp_mflags}

%install
%{__install} -p -D -m 0755 objs/ngx_http_auth_pam_module.so %{buildroot}%{_libdir}/nginx/modules/ngx_http_auth_pam_module.so
%{__install} -p -D -m 0644 %{SOURCE4} %{buildroot}%{_datadir}/nginx/modules/mod-http-auth-pam.conf

%files
%{_libdir}/nginx/modules/ngx_http_auth_pam_module.so
%{_datadir}/nginx/modules/mod-http-auth-pam.conf
%license ../ngx_http_auth_pam_module-%{version}/LICENSE
