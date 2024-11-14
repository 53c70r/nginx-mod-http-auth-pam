%global nginx_version 1.26.2
%global nginx_user nginx
%global debug_package %{nil}

%global  _hardened_build     1
%global  nginx_user          nginx

# Disable strict symbol checks in the link editor.
# See: https://src.fedoraproject.org/rpms/redhat-rpm-config/c/078af19
%undefine _strict_symbol_defs_build

%bcond_with geoip

# nginx gperftools support should be disabled for RHEL >= 8
# see: https://bugzilla.redhat.com/show_bug.cgi?id=1931402
%if 0%{?rhel} >= 8
%global with_gperftools 0
%else
# gperftools exists only on selected arches
# gperftools *detection* is failing on ppc64*, possibly only configure
# bug, but disable anyway.
%ifnarch s390 s390x ppc64 ppc64le
%global with_gperftools 1
%endif
%endif

%global with_aio 1

%if 0%{?fedora} > 40 || 0%{?rhel} > 9
%bcond_with engine
%else
%bcond_without engine
%endif

%if 0%{?fedora} > 22
%global with_mailcap_mimetypes 1
%endif

# kTLS requires OpenSSL 3.0 (default in F36+ and EL9+, available in EPEL8)
%if 0%{?fedora} >= 36 || 0%{?rhel} >= 8
%global with_ktls 1
%endif

# Build against OpenSSL 1.1 on EL7
%if 0%{?rhel} == 7
%global openssl_pkgversion 11
%endif

# Build against OpenSSL 3 on EL8
%if 0%{?rhel} == 8
%global openssl_pkgversion 3
%endif

Name:           nginx-mod-http-auth-pam
Version:        1.5.5
Release:        2%{?dist}
Summary:        Nginx module to use PAM for simple http authentication
License:        ASL 2.0
URL:            https://github.com/sto/ngx_http_auth_pam_module

Source0:        https://github.com/sto/ngx_http_auth_pam_module/archive/refs/tags/v%{version}.tar.gz

Source2:        https://nginx.org/download/nginx-%{nginx_version}.tar.gz
Source3:        https://nginx.org/download/nginx-%{nginx_version}.tar.gz.asc
Source4:        mod-http-auth-pam.conf
Source101:      https://nginx.org/keys/arut.key
Source102:      https://nginx.org/keys/pluknet.key
Source103:      https://nginx.org/keys/thresh.key
Source104:      https://nginx.org/keys/sb.key

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

Requires:       nginx = 2:%{nginx_version}

%description
HTTP Basic Authentication using PAM.

%prep
cat %{S:101} %{S:102} %{S:103} %{S:104} > %{_builddir}/nginx.gpg
cat %{SOURCE4} > %{_builddir}/mod-http-auth-pam.conf
%{gpgverify} --keyring='%{_builddir}/nginx.gpg' --signature='%{SOURCE3}' --data='%{SOURCE2}'
sed -i "s#MODULE_PATH#%{_prefix}/%{_lib}/nginx/modules/ngx_http_auth_pam_module.so#g" %{_builddir}/mod-http-auth-pam.conf

# extract ngx_http_auth_pam_module
%setup -n ngx_http_auth_pam_module-%{version}
# extract nginx next to ngx_http_auth_pam_module
%setup -T -b 2 -n nginx-%{nginx_version}
%patch -P 0 -p 0

%build
export DESTDIR=%{buildroot}
# alternative get conf from build
# ./configure %(nginx -V 2>&1 | grep 'configure arguments' | sed -r 's@^[^:]+: @@') --add-dynamic-module="../ngx_http_auth_pam_module-%{version}"

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
    --with-stream_geoip_module=dynamic \
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
    --with-http_v3_module \
    --with-http_xslt_module=dynamic \
    --with-mail=dynamic \
    --with-mail_ssl_module \
%if 0%{?with_ktls}
    --with-openssl-opt=enable-ktls \
%endif
%if %{without engine}
    --without-engine \
%endif
    --with-pcre \
    --with-pcre-jit \
    --with-stream=dynamic \
    --with-stream_realip_module \
    --with-stream_ssl_module \
    --with-stream_ssl_preread_module \
    --with-threads \
    --with-cc-opt="%{optflags} $(pcre2-config --cflags)" \
    --with-ld-opt="$nginx_ldopts" \
    --add-dynamic-module="../ngx_http_auth_pam_module-%{version}"; then
  : configure failed
  cat objs/autoconf.err
  exit 1
fi

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
