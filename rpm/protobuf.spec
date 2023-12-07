%global absl_min_maj 20230125
%global absl_min_rel 3
%global absl_min_ver %{absl_min_maj}.%{absl_min_rel}

# Starting with the v20.x protoc release, the versioning scheme changed:
# Each language has its own major version that can be incremented
# independently of other languages.
# The minor and patch versions, however, remain coupled

%global protobuf_version 25.1
%global protobuf_cpp_maj 4
%global protobuf_cpp_ver %{protobuf_cpp_maj}.%{protobuf_version}

Summary:        Protocol Buffers - Google's data interchange format
Name:           protobuf
# NOTE: Remember to change the macro above as well!
Version:        25.1
Release:        1
License:        BSD
URL:            https://github.com/protocolbuffers/protobuf
Source0:        %{name}-%{version}.tar.gz

# Handle legacy versioning scheme up to and including 3.18.x:
Provides:       %{name} = %{protobuf_cpp_ver}

BuildRequires:  cmake
BuildRequires:  libtool
BuildRequires:  pkgconfig(zlib)
# FIXME: use pkgconfig
# We want >= 20230125.3, but the .pc files only specify the major version:
# See src/google/protobuf/port_def.inc
BuildRequires:  abseil-cpp-devel >= %{absl_min_ver}
# See cmake/abseil-cpp.cmake for the complete list:
BuildRequires:  pkgconfig(absl_base)     >= %{absl_min_maj}
BuildRequires:  pkgconfig(absl_prefetch) >= %{absl_min_maj}

%description
Protocol Buffers are a way of encoding structured data in an efficient
yet extensible format. Google uses Protocol Buffers for almost all of
its internal RPC protocols and file formats.

Protocol buffers are a flexible, efficient, automated mechanism for
serializing structured data – think XML, but smaller, faster, and
simpler. You define how you want your data to be structured once, then
you can use special generated source code to easily write and read
your structured data to and from a variety of data streams and using a
variety of languages. You can even update your data structure without
breaking deployed programs that are compiled against the "old" format.

%package compiler
Summary:        Protocol Buffers compiler
Requires:       %{name} = %{version}-%{release}
Provides:       %{name}-compiler = %{protobuf_version}

%description compiler
This package contains Protocol Buffers compiler for all programming
languages

%package devel
Summary:        Protocol Buffers C++ headers and libraries
Requires:       %{name} = %{version}-%{release}
Requires:       %{name}-compiler = %{protobuf_version}
Requires:       zlib-devel
# Handle legacy versioning scheme up to and including 3.18.x:
Provides:       %{name}-devel = %{protobuf_cpp_ver}
Obsoletes:      %{name}-devel        < 3.20
Obsoletes:      %{name}-static       < 3.20


%description devel
This package contains Protocol Buffers compiler for all languages and
C++ headers and libraries

%package lite
Summary:        Protocol Buffers LITE_RUNTIME libraries

%description lite
Protocol Buffers built with optimize_for = LITE_RUNTIME.

The "optimize_for = LITE_RUNTIME" option causes the compiler to generate code
which only depends libprotobuf-lite, which is much smaller than libprotobuf but
lacks descriptors, reflection, and some other features.

%package lite-devel
Summary:        Protocol Buffers LITE_RUNTIME development libraries
Requires:       %{name}-devel = %{version}-%{release}
Requires:       %{name}-lite = %{version}-%{release}
Obsoletes:      %{name}-lite-static < 3.20

%description lite-devel
This package contains development libraries built with
optimize_for = LITE_RUNTIME.

The "optimize_for = LITE_RUNTIME" option causes the compiler to generate code
which only depends libprotobuf-lite, which is much smaller than libprotobuf but
lacks descriptors, reflection, and some other features.

%prep
%autosetup -n %{name}-%{version}/%{name}
chmod 644 examples/*

%build
iconv -f iso8859-1 -t utf-8 CONTRIBUTORS.txt > CONTRIBUTORS.txt.utf8
mv CONTRIBUTORS.txt.utf8 CONTRIBUTORS.txt
export PTHREAD_LIBS="-lpthread"
%cmake \
    -Dprotobuf_BUILD_TESTS=OFF \
    -Dprotobuf_ABSL_PROVIDER="package" \
    .

%make_build

%install
make %{?_smp_mflags} install DESTDIR=%{buildroot} STRIPBINARIES=no INSTALL="%{__install} -p" CPPROG="cp -p"
find %{buildroot} -type f -name "*.la" -exec rm -f {} \;

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%post lite -p /sbin/ldconfig
%postun lite -p /sbin/ldconfig

%post compiler -p /sbin/ldconfig
%postun compiler -p /sbin/ldconfig

%files
%defattr(-, root, root, -)
%license LICENSE
%{_libdir}/libprotobuf.so.*

%files compiler
%defattr(-, root, root, -)
%{_bindir}/protoc*
%{_libdir}/libprotoc.so.*

%files devel
%defattr(-, root, root, -)
%doc CONTRIBUTORS.txt README.md
%dir %{_includedir}/google
%{_includedir}/google/protobuf/
%{_libdir}/libprotobuf.so
%{_libdir}/libprotoc.so
%{_libdir}/pkgconfig/protobuf.pc
%{_libdir}/cmake/%{name}/
# UTF8_range does not build shared libs yet, see https://github.com/protocolbuffers/protobuf/issues/14958
%{_libdir}/libutf8_range.a
%{_libdir}/libutf8_validity.a
%{_includedir}/utf8_range.h
%{_includedir}/utf8_validity.h
%{_libdir}/pkgconfig/utf8_range.pc
%{_libdir}/cmake/utf8_range/
%exclude %{_includedir}/java/core/src/main/java/com/google/protobuf/java_features.proto

%files lite
%defattr(-, root, root, -)
%license LICENSE
%{_libdir}/libprotobuf-lite.so.*

%files lite-devel
%defattr(-, root, root, -)
%{_libdir}/libprotobuf-lite.so
%{_libdir}/pkgconfig/protobuf-lite.pc

