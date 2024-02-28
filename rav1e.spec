#
# Conditional build:
%bcond_without	clib	# C library

# no working cargo-c on x32 currently
%ifarch x32
%undefine	with_clib
%endif
Summary:	The fastest and safest AV1 encoder
Summary(pl.UTF-8):	Najszybszy i najbezpieczniejszy koder AV1
Name:		rav1e
Version:	0.7.1
Release:	1
License:	BSD
Group:		Libraries
#Source0Download: https://github.com/xiph/rav1e/releases
Source0:	https://github.com/xiph/rav1e/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	2e48f60bea23049a750f0721e30cdd54
# cd %{name}-%{version}
# cargo vendor
# cd ..
# tar cJf rav1e-crates-%{version}.tar.xz %{name}-%{version}/{vendor,Cargo.lock}
Source1:	%{name}-crates-%{version}.tar.xz
# Source1-md5:	cf73acf89cd9948848fec01fc29d0e08
URL:		https://github.com/xiph/rav1e
BuildRequires:	cargo
%{?with_clib:BuildRequires:	cargo-c}
%ifarch %{x8664}
BuildRequires:	nasm >= 2.14
%endif
BuildRequires:	rust >= 1.51.0
# for tests only?
#BuildRequires:	aom-devel
#BuildRequires:	dav1d-devel
ExclusiveArch:	%{ix86} %{x8664} x32 aarch64
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%ifarch	x32
%define		target_opt	--target x86_64-unknown-linux-gnux32
%define		features	--no-default-features --features "binaries signal_support"
%else
%define		target_opt	%{nil}
%define		features	%{nil}
%endif

%description
rav1e is an AV1 video encoder. It is designed to eventually cover all
use cases, though in its current form it is most suitable for cases
where libaom (the reference encoder) is too slow.

%description -l pl.UTF-8
rav1e to koder obrazu AV1. Jest projektowany, aby ewentualnie pokrywać
wszystkie przypadki użycia, ale w obecnej postaci nadaje się najlepiej
tam, gdzie libaom (koder referencyjny) jest zbyt wolny.

%package libs
Summary:	Shared rav1e library
Summary(pl.UTF-8):	Biblioteka współdzielona rav1e
Group:		Libraries

%description libs
Shared rav1e library.

%description libs -l pl.UTF-8
Biblioteka współdzielona rav1e.

%package devel
Summary:	Header files for rav1e library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki rav1e
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
Header files for rav1e library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki rav1e.

%package static
Summary:	Static rav1e library
Summary(pl.UTF-8):	Statyczna biblioteka rav1e
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static rav1e library.

%description static -l pl.UTF-8
Statyczna biblioteka rav1e.

%prep
%setup -q -b1

# use our offline registry
export CARGO_HOME="$(pwd)/.cargo"

mkdir -p "$CARGO_HOME"
cat >.cargo/config <<EOF
[source.crates-io]
replace-with = 'vendored-sources'

[source.vendored-sources]
directory = '$PWD/vendor'
EOF

%build
export CARGO_HOME="$(pwd)/.cargo"

cargo -v build --release --frozen %{target_opt} %{features}

%if %{with clib}
cargo -v cbuild --release --frozen %{target_opt} \
	--prefix %{_prefix} \
	--libdir %{_libdir}
%endif

%install
rm -rf $RPM_BUILD_ROOT

cargo -v install --frozen %{target_opt} %{features} \
	--path . \
	--root $RPM_BUILD_ROOT%{_prefix}

%if %{with clib}
cargo -v cinstall --frozen --release %{target_opt} \
	--destdir $RPM_BUILD_ROOT \
	--prefix %{_prefix} \
	--bindir %{_bindir} \
	--includedir %{_includedir} \
	--libdir %{_libdir}
%endif

%{__rm} $RPM_BUILD_ROOT%{_prefix}/.crates*

%clean
rm -rf $RPM_BUILD_ROOT

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc CHANGELOG.md LICENSE PATENTS README.md
%attr(755,root,root) %{_bindir}/rav1e

%if %{with clib}
%files libs
%defattr(644,root,root,755)
%doc CHANGELOG.md LICENSE PATENTS README.md doc/GLOSSARY.md
%attr(755,root,root) %{_libdir}/librav1e.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/librav1e.so.0.7

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/librav1e.so
%{_includedir}/rav1e
%{_pkgconfigdir}/rav1e.pc

%files static
%defattr(644,root,root,755)
%{_libdir}/librav1e.a
%endif
